from __future__ import annotations

import json
import re
import time
from dataclasses import dataclass

import httpx
import structlog

from news_api.platform.cache import get_float, increment
from news_api.platform.clock import monthly_bucket
from news_api.platform.config import prompt_table, scoring_config
from news_api.platform.metrics import AI_COST, AI_TOKENS, SUMMARIES, SUMMARY_LATENCY
from news_api.platform.settings import get_settings

log = structlog.get_logger(__name__)

LEGACY_MODEL_IDS = {"deepseek-v4-flash", "deepseek-chat", "deepseek-reasoner"}
URL_RE = re.compile(r"https?://|www\.", re.IGNORECASE)
DOMAIN_RE = re.compile(
    r"\b[a-z0-9][a-z0-9-]*\.(?:com|org|net|io|es|gov|edu|co|ai|info|biz)\b", re.IGNORECASE
)
HTML_RE = re.compile(r"<[^>]+>")
SENTENCE_RE = re.compile(r"[^.!?]+[.!?]+")
BULLET_RE = re.compile(r"^\s*(?:[-*•]|\d+[.)])\s+", re.MULTILINE)


class AIError(Exception):
    pass


class BudgetExceeded(AIError):
    pass


@dataclass
class AIResult:
    text: str
    prompt_tokens: int = 0
    completion_tokens: int = 0


def _plain(value: str) -> str:
    text = BULLET_RE.sub("", value or "").strip()
    return re.sub(r"\s+", " ", text).strip()


def validate_summary(text: str, title: str) -> tuple[bool, str]:
    candidate = _plain(text)
    if not candidate:
        return False, "empty"
    if len(candidate) < 80 or len(candidate) > 900:
        return False, "length"
    if URL_RE.search(candidate) or DOMAIN_RE.search(candidate):
        return False, "url"
    if HTML_RE.search(candidate):
        return False, "html"
    sentences = [item.strip() for item in SENTENCE_RE.findall(candidate) if item.strip()]
    if not 2 <= len(sentences) <= 4:
        return False, "sentences"
    if title and title.casefold().strip() and title.casefold().strip() in candidate.casefold():
        return False, "copied-title"
    return True, "ok"


def validate_brief(text: str) -> tuple[bool, str]:
    candidate = (text or "").strip()
    if not candidate or len(candidate) > 1200:
        return False, "length"
    if URL_RE.search(candidate) or HTML_RE.search(candidate):
        return False, "url-or-html"
    lines = [line.strip(" -•\t") for line in candidate.splitlines() if line.strip()]
    if not 3 <= len(lines) <= 7:
        return False, "lines"
    if any(len(line) > 200 for line in lines):
        return False, "line-length"
    return True, "ok"


def normalize_brief(text: str) -> str:
    """Repair a model paragraph into the 3-7 line shape the validator expects."""
    candidate = _plain(text or "")
    if not candidate:
        return ""
    sentences = [part.strip() for part in SENTENCE_RE.findall(candidate) if part.strip()]
    if len(sentences) < 3:
        return candidate[:1150]
    picked: list[str] = []
    total = 0
    for sentence in sentences:
        if len(picked) >= 5 or total + len(sentence) > 1100:
            break
        picked.append(sentence)
        total += len(sentence)
    if len(picked) >= 3:
        return "\n".join(picked)
    return "\n".join(sentences[:5])


def _replace(template: str, **values: str) -> str:
    result = template
    for key, value in values.items():
        result = result.replace("{" + key + "}", value)
    return result


class AIClient:
    def __init__(self, client: httpx.AsyncClient | None = None) -> None:
        self.settings = get_settings()
        self._client = client
        self.model = self.settings.ai_model
        if self.model in LEGACY_MODEL_IDS:
            raise AIError(f"legacy model id rejected: {self.model}")

    def available(self) -> bool:
        return bool(
            self.settings.ai_enabled
            and self.settings.ai_api_key
            and self.model not in LEGACY_MODEL_IDS
        )

    async def _chat(
        self,
        messages: list[dict[str, str]],
        *,
        temperature: float,
        timeout: float,
        max_tokens: int = 400,
    ) -> AIResult:
        if not self.available():
            raise AIError("AI provider is not configured")
        await self._check_budget()
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": False,
        }
        owns = self._client is None
        client = self._client or httpx.AsyncClient(timeout=timeout)
        started = time.perf_counter()
        try:
            response = await client.post(
                f"{self.settings.ai_base_url.rstrip('/')}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.settings.ai_api_key}",
                    "Content-Type": "application/json",
                },
                json=payload,
                timeout=timeout,
            )
            if response.status_code >= 400:
                raise AIError(f"provider status {response.status_code}")
            body = response.json()
            choices = body.get("choices") or []
            if not choices:
                raise AIError("provider returned no choices")
            text = str(choices[0].get("message", {}).get("content") or "").strip()
            usage = body.get("usage") or {}
            prompt_tokens = int(usage.get("prompt_tokens") or 0)
            completion_tokens = int(usage.get("completion_tokens") or 0)
            await self._record_usage(prompt_tokens, completion_tokens)
            SUMMARY_LATENCY.labels(locale="mixed").observe(time.perf_counter() - started)
            return AIResult(text, prompt_tokens, completion_tokens)
        except httpx.HTTPError as exc:
            raise AIError(type(exc).__name__) from exc
        except (KeyError, ValueError, TypeError) as exc:
            raise AIError("invalid provider response") from exc
        finally:
            if owns:
                await client.aclose()

    async def _check_budget(self) -> None:
        key = f"ai:spend:{monthly_bucket()}"
        spent = await get_float(key)
        if spent >= self.settings.ai_monthly_budget_usd:
            raise BudgetExceeded("monthly AI budget exhausted")

    async def _record_usage(self, prompt_tokens: int, completion_tokens: int) -> None:
        pricing = scoring_config().get("ai", {})
        input_price = float(pricing.get("input_price_per_million", 0.27))
        output_price = float(pricing.get("output_price_per_million", 1.1))
        cost = (prompt_tokens / 1_000_000) * input_price + (
            completion_tokens / 1_000_000
        ) * output_price
        AI_TOKENS.labels(model=self.model, direction="prompt").inc(prompt_tokens)
        AI_TOKENS.labels(model=self.model, direction="completion").inc(completion_tokens)
        AI_COST.labels(model=self.model).inc(cost)
        await increment(f"ai:spend:{monthly_bucket()}", cost)

    async def complete_json(
        self,
        *,
        system: str,
        user: str,
        timeout: float = 60.0,
        max_tokens: int = 1600,
    ) -> str:
        if not self.available():
            raise AIError("AI provider is not configured")
        result = await self._chat(
            [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            temperature=0.1,
            timeout=timeout,
            max_tokens=max_tokens,
        )
        return result.text

    async def summarize(self, *, title: str, excerpt: str, language: str) -> str | None:
        table = prompt_table(language)
        messages = [
            {"role": "system", "content": str(table["item"]["system"])},
            {
                "role": "user",
                "content": _replace(
                    str(table["item"]["user"]),
                    title=title[:300],
                    excerpt=excerpt[:280] or title[:280],
                ),
            },
        ]
        for attempt in range(2):
            try:
                result = await self._chat(
                    messages,
                    temperature=0.4,
                    timeout=self.settings.ai_item_timeout_seconds,
                    max_tokens=500,
                )
            except AIError as exc:
                SUMMARIES.labels(language=language, status="failed").inc()
                log.warning("summary.failed", error=str(exc), attempt=attempt + 1)
                if isinstance(exc, BudgetExceeded):
                    return None
                continue
            valid, reason = validate_summary(result.text, title)
            if valid:
                SUMMARIES.labels(language=language, status="ok").inc()
                return _plain(result.text)
            SUMMARIES.labels(language=language, status="invalid").inc()
            log.warning("summary.invalid", reason=reason, attempt=attempt + 1)
        return None

    async def desk_brief(self, *, headlines: list[str], language: str) -> str | None:
        if not headlines:
            return None
        table = prompt_table(language)
        joined = "\n".join(f"- {headline[:200]}" for headline in headlines[:12])
        messages = [
            {"role": "system", "content": str(table["desk"]["system"])},
            {"role": "user", "content": _replace(str(table["desk"]["user"]), headlines=joined)},
        ]
        for attempt in range(2):
            try:
                result = await self._chat(
                    messages,
                    temperature=0.4,
                    timeout=self.settings.ai_desk_timeout_seconds,
                    max_tokens=900,
                )
            except AIError as exc:
                log.warning("desk_brief.failed", error=str(exc), attempt=attempt + 1)
                if isinstance(exc, BudgetExceeded):
                    return None
                continue
            brief = normalize_brief(result.text)
            valid, reason = validate_brief(brief)
            if valid:
                return brief
            log.warning("desk_brief.invalid", reason=reason, attempt=attempt + 1)
        return None

    async def pick_featured(
        self, *, candidates: list[dict[str, str]], language: str
    ) -> tuple[str | None, list[str]]:
        if len(candidates) < 2:
            return None, []
        table = prompt_table(language)
        joined = "\n".join(f"- {item['id']}: {item['title'][:160]}" for item in candidates[:20])
        messages = [
            {"role": "system", "content": str(table["picks"]["system"])},
            {"role": "user", "content": _replace(str(table["picks"]["user"]), candidates=joined)},
        ]
        try:
            result = await self._chat(
                messages,
                temperature=0.3,
                timeout=self.settings.ai_picks_timeout_seconds,
                max_tokens=200,
            )
            payload = json.loads(result.text)
        except (AIError, ValueError):
            return None, []
        valid_ids = {item["id"] for item in candidates}
        lead = payload.get("lead")
        favorites = payload.get("favorites") or []
        if lead not in valid_ids:
            lead = None
        favorites = [item for item in favorites if item in valid_ids and item != lead][:3]
        return lead, favorites
