from __future__ import annotations

import re
import unicodedata
from difflib import SequenceMatcher
from typing import Any

from news_api.articles.domain.models import Candidate
from news_api.platform.config import scoring_config

TOKEN_RE = re.compile(r"[^\W_]+", re.UNICODE)


def tokenize(text: str) -> set[str]:
    normalized = unicodedata.normalize("NFKC", text).casefold()
    return {token for token in TOKEN_RE.findall(normalized) if len(token) > 1}


def title_similarity(left: str, right: str) -> float:
    left_tokens = tokenize(left)
    right_tokens = tokenize(right)
    if not left_tokens or not right_tokens:
        return 0.0
    union = left_tokens | right_tokens
    jaccard = len(left_tokens & right_tokens) / len(union)
    sequence = SequenceMatcher(None, " ".join(sorted(left_tokens)), " ".join(sorted(right_tokens)))
    return max(jaccard, sequence.ratio())


def dedupe_candidates(
    candidates: list[Candidate],
    *,
    config: dict[str, Any] | None = None,
) -> list[Candidate]:
    rules = config or scoring_config()
    threshold = float(rules.get("dedupe_similarity", 0.72))
    ordered = sorted(candidates, key=lambda item: item.score, reverse=True)

    clusters: list[list[Candidate]] = []
    for candidate in ordered:
        placed = False
        for cluster in clusters:
            if title_similarity(cluster[0].title, candidate.title) >= threshold:
                cluster.append(candidate)
                placed = True
                break
        if not placed:
            clusters.append([candidate])

    deduped: list[Candidate] = []
    for cluster in clusters:
        representative = max(cluster, key=lambda item: item.score)
        sources = []
        for member in cluster:
            label = member.source_name or member.publisher
            if label and label not in sources:
                sources.append(label)
        representative.corroboration = max(1, len(sources))
        representative.corroborating_sources = sources
        bonus = float(rules.get("corroboration_bonus", 0.15)) * (representative.corroboration - 1)
        representative.score = round(representative.score + bonus, 4)
        trust_floor = float(rules.get("single_source_trust_threshold", 0.8))
        if representative.corroboration >= 2:
            representative.verification = "corroborated"
        elif representative.source_trust < trust_floor and not representative.pinned:
            representative.score = round(
                representative.score - float(rules.get("single_source_penalty", 0.12)), 4
            )
            representative.verification = "single-source"
        else:
            representative.verification = "trusted-source"
        deduped.append(representative)

    deduped.sort(key=lambda item: item.score, reverse=True)
    return deduped
