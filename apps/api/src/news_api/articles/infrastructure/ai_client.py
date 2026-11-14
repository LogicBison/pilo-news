from __future__ import annotations

import json
import re
import time
from dataclasses import dataclass, replace
from typing import Any

import httpx
import structlog

from news_api.articles.infrastructure import ai_budget
from news_api.platform import overrides
from news_api.platform.clock import utcnow
from news_api.platform.config import prompt_table
from news_api.platform.metrics import (
    AI_BUDGET_REMAINING,
    AI_BUDGET_SPENT,
    AI_COST,
    AI_DENIED,
    AI_LIMIT_REMAINING,
    AI_TOKENS,
    SUMMARIES,
    SUMMARY_LATENCY,
)
from news_api.platform.offpeak import (
    is_peak,
    parse_peak_days,
    parse_peak_holidays,
    parse_peak_windows,
)
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

# D2 - stock tails that read as machine copy. Exact phrases, both languages;
# a hit means the model produced the habit rather than the fact.
BANNED_PHRASES: tuple[str, ...] = (
    "for professional readers",
    "the takeaway is",
    "the move signals",
    "it is worth noting",
    "it's worth noting",
    "a significant development",
    "in today's fast-paced",
    "plays a crucial role",
    "shed light on",
    "resulta relevante para los profesionales",
    "el movimiento señala",
    "es importante destacar",
    "en el panorama actual",
    "juega un papel crucial",
    "vale la pena señalar",
)

# D4 - vague verbs that carry the meaning instead of stating it. Only the
# verb forms the plan names: the singular nouns ("a signal from the Fed")
# survive, because banning them would reject facts rather than filler.
BANNED_VERBS_RE = re.compile(
    r"\bsignals\b|\bhighlights\b|\bunderscores\b|\bmatters to\b"
    r"|\bseñala\b|\bsubraya\b|\bes relevante para\b",
    re.IGNORECASE,
)

# D7 - a pointer the public page cannot follow ("see URL in Notes").
REFERENCE_RE = re.compile(
    r"\bsee\b[^.!?]{0,60}\b(?:link|url|notes?|below|above)\b"
    r"|\b(?:link|url|notes?)\s+(?:above|below)\b"
    r"|\bin\s+(?:the\s+)?notes\b",
    re.IGNORECASE,
)

# D3 - an article opener buries the actor. "The European Commission" keeps its
# actor (proper noun follows); "The change shortens..." does not. English
# articles only: a Spanish "Los reguladores publicó..." leads with its actor
# too, so applying El/La/Los here would reject correct Spanish openers.
OPENER_RE = re.compile(r"^(?:A|An|The)\s+[a-z]")

MAX_SUMMARY_CHARS = 520
MAX_SUMMARY_SENTENCES = 3
MAX_OPENER_WORDS = 25
DIGIT_RE = re.compile(r"\d")


class AIError(Exception):
    pass


class BudgetExceeded(AIError):
    pass


# Consecutive provider failures in this process. A provider that is down, rate
# limiting or rejecting the key gets one halt, not one retry per candidate: at
# two attempts per item a single run can otherwise send hundreds of requests
# that book nothing and buy nothing.
_consecutive_failures = 0


def _breaker_hit() -> int:
    global _consecutive_failures
    _consecutive_failures += 1
    return _consecutive_failures


def _breaker_reset() -> None:
    global _consecutive_failures
    _consecutive_failures = 0


@dataclass
class AIResult:
    text: str
    prompt_tokens: int = 0
    completion_tokens: int = 0


def _as_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        lowered = value.strip().lower()
        if lowered in ("1", "true", "yes", "on"):
            return True
        if lowered in ("0", "false", "no", "off"):
            return False
    raise ValueError("not a boolean")


def _plain(value: str) -> str:
    text = BULLET_RE.sub("", value or "").strip()
    return re.sub(r"\s+", " ", text).strip()


def validate_summary(text: str, title: str, *, excerpt: str = "") -> tuple[bool, str]:
    """Gate one candidate summary (SPEC-adjacent: improvement plan D1-D5, D7).

    ``excerpt`` is the source the model was given; when it carries a digit the
    summary has to carry one too (D5). Every failure is a distinct reason so
    the retry log tells us *which* rule the model broke.
    """
    candidate = _plain(text)
    if not candidate:
        return False, "empty"
    if len(candidate) < 80 or len(candidate) > MAX_SUMMARY_CHARS:
        return False, "length"
    if URL_RE.search(candidate) or DOMAIN_RE.search(candidate):
        return False, "url"
    if HTML_RE.search(candidate):
        return False, "html"
    sentences = [item.strip() for item in SENTENCE_RE.findall(candidate) if item.strip()]
    if not 2 <= len(sentences) <= MAX_SUMMARY_SENTENCES:
        return False, "sentences"
    # Checked before ``opener``: a stock tail reads as machine copy whether or
    # not it also buries the actor, and the reason is what the retry log keeps.
    lowered = candidate.casefold()
    hit = next((phrase for phrase in BANNED_PHRASES if phrase in lowered), None)
    if hit:
        return False, f"banned-phrase:{hit}"
    if title and title.casefold().strip() and title.casefold().strip() in candidate.casefold():
        return False, "copied-title"
    # D3: actor first, and short enough to read as one breath.
    if OPENER_RE.match(sentences[0]):
        return False, "opener"
    if len(sentences[0].split()) > MAX_OPENER_WORDS:
        return False, "opener-length"
    # D4 / D7: the habits the reader can spot without being told.
    if BANNED_VERBS_RE.search(candidate):
        return False, "banned-verb"
    if REFERENCE_RE.search(candidate):
        return False, "reference"
    # D5: the source had a number, so the summary has to keep one.
    if DIGIT_RE.search(f"{title} {excerpt}") and not DIGIT_RE.search(candidate):
        return False, "missing-number"
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


@dataclass(frozen=True)
class AIConfig:
    """Effective cost controls: `.env` defaults with the admin row on top."""

    enabled: bool
    limits: ai_budget.Limits
    max_items_per_run: int
    desks_per_tick: int
    offpeak_only: bool
    peak_windows: str
    peak_days: str
    peak_holidays: str
    breaker_failures: int = 5
    breaker_seconds: int = 1800


class AIClient:
    def __init__(self, client: httpx.AsyncClient | None = None) -> None:
        self.settings = get_settings()
        self._client = client
        self.model = self.settings.ai_model
        self._offpeak_logged = False
        # Set when a limit or a halt stops a call, so the caller can abandon the
        # rest of the run instead of walking every remaining candidate.
        self.stop_reason: str | None = None
        if self.model in LEGACY_MODEL_IDS:
            raise AIError(f"legacy model id rejected: {self.model}")

    async def config(self) -> AIConfig:
        """Environment first, then whatever the admin console saved."""
        env = self.settings
        values = await overrides.load()

        def typed(key: str, default, cast):
            if key not in values:
                return default
            try:
                return cast(values[key])
            except (TypeError, ValueError):
                # A bad stored value must not take the desk down; use the env.
                log.warning("ai.override_ignored", key=key, value=str(values[key])[:40])
                return default

        config = AIConfig(
            enabled=typed("ai_enabled", env.ai_enabled, _as_bool),
            limits=ai_budget.Limits(
                daily_tokens=typed("ai_daily_token_limit", int(env.ai_daily_token_limit), int),
                monthly_tokens=typed(
                    "ai_monthly_token_limit", int(env.ai_monthly_token_limit), int
                ),
                daily_requests=typed(
                    "ai_daily_request_limit", int(env.ai_daily_request_limit), int
                ),
                monthly_requests=typed(
                    "ai_monthly_request_limit", int(env.ai_monthly_request_limit), int
                ),
                daily_usd=typed("ai_daily_budget_usd", float(env.ai_daily_budget_usd), float),
                monthly_usd=typed("ai_monthly_budget_usd", float(env.ai_monthly_budget_usd), float),
            ),
            max_items_per_run=typed("ai_max_items_per_run", int(env.ai_max_items_per_run), int),
            desks_per_tick=typed("ai_desks_per_tick", int(env.ai_desks_per_tick), int),
            offpeak_only=typed("ai_offpeak_only", env.ai_offpeak_only, _as_bool),
            peak_windows=typed("ai_peak_windows", env.ai_peak_windows, str),
            peak_days=typed("ai_peak_days", env.ai_peak_days, str),
            peak_holidays=typed("ai_peak_holidays", env.ai_peak_holidays, str),
            breaker_failures=int(env.ai_breaker_failures),
            breaker_seconds=int(env.ai_breaker_seconds),
        )
        try:
            # Parse the calendar instead of asking whether *now* is peak:
            # `is_peak` returns early on a non-peak weekday, so a hand-edited bad
            # row would slip through at the weekend and only be caught on Monday.
            parse_peak_windows(config.peak_windows)
            parse_peak_days(config.peak_days)
            parse_peak_holidays(config.peak_holidays)
        except ValueError:
            # A hand-edited row must not take the desks down: use the env calendar.
            log.warning("ai.override_calendar_invalid", windows=config.peak_windows)
            return replace(
                config,
                peak_windows=env.ai_peak_windows,
                peak_days=env.ai_peak_days,
                peak_holidays=env.ai_peak_holidays,
            )
        return config

    async def available(self) -> bool:
        return self._available(await self.config())

    def _available(self, config: AIConfig) -> bool:
        if not (config.enabled and self.settings.ai_api_key and self.model not in LEGACY_MODEL_IDS):
            return False
        if config.offpeak_only and self._peak(config):
            if not self._offpeak_logged:
                # Once per process, not once per item.
                log.info(
                    "ai.peak_skip",
                    windows=config.peak_windows,
                    days=config.peak_days,
                    utc=utcnow().isoformat(timespec="minutes"),
                )
                self._offpeak_logged = True
            return False
        return True

    def _period(self, config: AIConfig) -> str:
        return "peak" if self._peak(config) else "off_peak"

    def _peak(self, config: AIConfig) -> bool:
        return is_peak(
            utcnow(),
            windows=config.peak_windows,
            days=config.peak_days,
            holidays=config.peak_holidays,
        )

    async def allowance(self, *, interval_minutes: int, desks: int = 1) -> int:
        """Items this run may attempt under the tightest bucket.

        Sized twice - by tokens, which is what the provider bills, and by
        dollars, which is what an operator reads - across the runs still due
        today and this month. The smallest of the four is the allowance, so a
        run can never spend a day's or a month's headroom at once.
        """
        config = await self.config()
        try:
            state = await ai_budget.snapshot(config.limits)
        except ai_budget.BudgetUnavailable:
            return 0
        if state.get("halted_reason"):
            # Halted means no call will be sent, so the run gets no items: it
            # publishes from the source excerpts instead of walking the pool.
            return 0
        desk_count = max(1, desks)
        spans = (
            ("day", ai_budget.runs_left_today(interval_minutes)),
            ("month", ai_budget.runs_left_in_period(interval_minutes)),
        )
        candidates: list[int] = []
        for period, runs_left in spans:
            bucket = state.get(period)
            if not bucket:
                continue
            remaining = bucket["remaining"]
            candidates.append(
                ai_budget.allowance(
                    remaining=float(remaining["tokens"]),
                    runs_left=runs_left * desk_count,
                    item_cost=float(ai_budget.plan_tokens()),
                    maximum=config.max_items_per_run,
                )
            )
            candidates.append(
                ai_budget.allowance(
                    remaining=float(remaining["usd"]),
                    runs_left=runs_left * desk_count,
                    item_cost=float(self.settings.ai_item_cost_estimate_usd),
                    maximum=config.max_items_per_run,
                )
            )
        return min(candidates) if candidates else 0

    async def _chat(
        self,
        messages: list[dict[str, str]],
        *,
        temperature: float,
        timeout: float,
        max_tokens: int = 400,
    ) -> AIResult:
        config = await self.config()
        if not self._available(config):
            raise AIError("AI provider is not configured")
        period = self._period(config)
        reservation = await self._reserve(config, messages, max_tokens)
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
            if response.status_code in (401, 403):
                # The key is wrong, revoked, or the account is stopped. Retrying
                # cannot help, and every retry is another request against the
                # provider's rate limit - so this stops the period, not the call.
                await ai_budget.release(reservation)
                await ai_budget.halt(f"auth_{response.status_code}")
                self.stop_reason = "halted:auth"
                raise BudgetExceeded(
                    f"provider rejected the key ({response.status_code}); ai halted"
                )
            if response.status_code == 402:
                # The provider is out of money: stop trying, not just this call.
                await ai_budget.release(reservation)
                await ai_budget.mark_exhausted()
                self.stop_reason = "halted:provider_402"
                raise BudgetExceeded("provider balance exhausted")
            if response.status_code >= 400:
                await ai_budget.release(reservation)
                await self._failure(config, f"status_{response.status_code}")
                raise AIError(f"provider status {response.status_code}")
            try:
                body = response.json()
                choices = body.get("choices") or []
                if not choices:
                    # Sent and possibly billed, just unusable: book the worst case.
                    await ai_budget.settle_worst_case(reservation)
                    await self._failure(config, "no_choices")
                    raise AIError("provider returned no choices")
                text = str(choices[0].get("message", {}).get("content") or "").strip()
                booked = ai_budget.usage_from_response(body.get("usage") or {}, period=period)
            except (KeyError, ValueError, TypeError) as exc:
                # The request was sent, so it may have been billed; keep the hold.
                await ai_budget.settle_worst_case(reservation)
                await self._failure(config, "unparsable")
                raise AIError("invalid provider response") from exc
            await ai_budget.settle(reservation, booked)
            _breaker_reset()
            await self._record_usage(booked, config)
            SUMMARY_LATENCY.labels(locale="mixed").observe(time.perf_counter() - started)
            return AIResult(text, booked.prompt_tokens, booked.completion_tokens)
        except httpx.HTTPError as exc:
            # Unknown outcome after the request left: assume it was billed.
            await ai_budget.settle_worst_case(reservation)
            await self._failure(config, type(exc).__name__)
            raise AIError(type(exc).__name__) from exc
        finally:
            if owns:
                await client.aclose()

    async def _failure(self, config: AIConfig, reason: str) -> None:
        """Count a provider failure; open the breaker when they pile up."""
        count = _breaker_hit()
        if config.breaker_failures > 0 and count >= config.breaker_failures:
            await ai_budget.halt("circuit_breaker", for_seconds=config.breaker_seconds)
            self.stop_reason = "halted:circuit_breaker"
        log.warning("ai.provider_failure", reason=reason, consecutive=count)

    async def _reserve(
        self, config: AIConfig, messages: list[dict[str, str]], max_tokens: int
    ) -> ai_budget.Reservation:
        worst_case = ai_budget.estimate(messages, max_tokens=max_tokens)
        try:
            return await ai_budget.reserve(worst_case, config.limits)
        except ai_budget.BudgetUnavailable as exc:
            # Fail closed: an unreadable ledger must not become a free pass.
            log.warning("ai.budget_unavailable", error=str(exc))
            self.stop_reason = "ledger_unavailable"
            AI_DENIED.labels(reason="ledger_unavailable").inc()
            raise BudgetExceeded("ai budget ledger unavailable") from exc
        except ai_budget.BudgetExceeded as exc:
            self.stop_reason = exc.reason
            AI_DENIED.labels(reason=exc.reason).inc()
            log.info("ai.denied", reason=exc.reason, detail=str(exc))
            raise BudgetExceeded(str(exc)) from exc

    async def _record_usage(self, booked: ai_budget.Usage, config: AIConfig) -> None:
        AI_TOKENS.labels(model=self.model, direction="prompt").inc(booked.prompt_tokens)
        AI_TOKENS.labels(model=self.model, direction="completion").inc(booked.completion_tokens)
        AI_COST.labels(model=self.model).inc(booked.cost_usd)
        try:
            state = await ai_budget.snapshot(config.limits)
        except ai_budget.BudgetUnavailable:  # pragma: no cover - metrics only
            return
        month = state.get("month") or {}
        AI_BUDGET_SPENT.set(float(month.get("cost_usd") or 0.0))
        AI_BUDGET_REMAINING.set(float((month.get("remaining") or {}).get("usd") or 0.0))
        for period in ("day", "month"):
            remaining = (state.get(period) or {}).get("remaining") or {}
            for dimension in ("requests", "tokens", "usd"):
                AI_LIMIT_REMAINING.labels(dimension=dimension, period=period).set(
                    float(remaining.get(dimension) or 0.0)
                )

    async def complete_json(
        self,
        *,
        system: str,
        user: str,
        timeout: float = 60.0,
        max_tokens: int = 1600,
    ) -> str:
        if not await self.available():
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
                    max_tokens=240,
                )
            except AIError as exc:
                SUMMARIES.labels(language=language, status="failed").inc()
                log.warning("summary.failed", error=str(exc), attempt=attempt + 1)
                if isinstance(exc, BudgetExceeded):
                    return None
                continue
            valid, reason = validate_summary(result.text, title, excerpt=excerpt)
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
                    max_tokens=400,
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
