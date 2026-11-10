from __future__ import annotations

from prometheus_client import CONTENT_TYPE_LATEST, Counter, Gauge, Histogram, generate_latest

from news_api.platform.settings import get_settings


def _counter(name: str, description: str, labels: tuple[str, ...] = ()) -> Counter:
    try:
        return Counter(name, description, labels)
    except ValueError:  # pragma: no cover - re-import in tests
        from prometheus_client import REGISTRY

        return REGISTRY._names_to_collectors[name]  # type: ignore[return-value]


def _histogram(name: str, description: str, labels: tuple[str, ...] = ()) -> Histogram:
    try:
        return Histogram(name, description, labels, buckets=(0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0))
    except ValueError:  # pragma: no cover
        from prometheus_client import REGISTRY

        return REGISTRY._names_to_collectors[name]  # type: ignore[return-value]


def _gauge(name: str, description: str, labels: tuple[str, ...] = ()) -> Gauge:
    try:
        return Gauge(name, description, labels)
    except ValueError:  # pragma: no cover
        from prometheus_client import REGISTRY

        return REGISTRY._names_to_collectors[name]  # type: ignore[return-value]


HTTP_REQUESTS = _counter(
    "http_requests_total", "HTTP requests", ("route", "method", "status_class")
)
HTTP_DURATION = _histogram(
    "http_request_duration_seconds", "HTTP request duration", ("route", "method")
)
HTTP_IN_FLIGHT = _gauge("http_in_flight_requests", "In-flight HTTP requests")
RATE_LIMITED = _counter("rate_limited_total", "Rate-limited requests", ("scope",))
CACHE_HITS = _counter("cache_hits_total", "Cache hits", ("cache",))
CACHE_MISSES = _counter("cache_misses_total", "Cache misses", ("cache",))

INGEST_FETCH = _counter("ingest_fetch_total", "Feed fetches", ("source", "status"))
INGEST_FETCH_BLOCKED = _counter(
    "ingest_fetch_blocked_total", "Feed fetches refused before or without parsing", ("reason",)
)
INGEST_HOST_COOLDOWN = _gauge(
    "ingest_host_cooldown_seconds", "Seconds until a host may be polled again", ("host",)
)
INGEST_FETCH_DURATION = _histogram(
    "ingest_fetch_duration_seconds", "Feed fetch duration", ("source",)
)
INGEST_ITEMS = _counter("ingest_items_total", "Ingested items", ("industry", "result"))
INGEST_LAG = _histogram("ingest_lag_seconds", "Seconds since last successful run", ("industry",))
ARTICLES_SCORED = _counter("articles_scored_total", "Scored articles", ("industry", "result"))
REFRESH_RUNS = _counter("refresh_runs_total", "Refresh runs", ("trigger", "status"))
REFRESH_DURATION = _histogram("refresh_duration_seconds", "Refresh duration", ("industry",))
QUEUE_DEPTH = _gauge("queue_depth", "Redis stream depth", ("stream",))

SUMMARIES = _counter("summaries_generated_total", "AI summaries", ("language", "status"))
SUMMARY_LATENCY = _histogram("summary_latency_seconds", "Summary latency", ("locale",))
AI_TOKENS = _counter("ai_tokens_total", "AI tokens", ("model", "direction"))
AI_COST = _counter("ai_estimated_cost_usd_total", "Estimated AI cost", ("model",))

NEWS_READS = _counter("news_reads_total", "News reads", ("industry", "endpoint", "language"))
REFRESH_MANUAL = _counter("refresh_manual_total", "Manual refreshes", ("industry",))
CONTACT_SUBMISSIONS = _counter(
    "contact_submissions_total", "Contact submissions", ("industry", "result")
)
CONTACT_RATE_LIMITED = _counter("contact_rate_limited_total", "Contact rate limited", ("industry",))
LEADS = _counter("leads_total", "Leads", ("industry", "status"))
LEADS_RATE_LIMITED = _counter("leads_rate_limited_total", "Leads rate limited", ("industry",))
LEAD_ROUTE_LATENCY = _histogram("lead_route_latency_seconds", "Lead routing latency", ("industry",))
CTA_EVENTS = _counter("cta_events_total", "CTA funnel events", ("industry", "event", "placement"))
OFFER_ISSUES = _counter("offer_issues_total", "Generated offer issues", ("offer", "status"))

ADMIN_AUTH = _counter("admin_auth_total", "Admin auth attempts", ("result",))
ADMIN_MUTATIONS = _counter("admin_mutations_total", "Admin mutations", ("action",))
API_KEYS_ACTIVE = _gauge("api_keys_active", "Active API keys")


def metrics_payload() -> tuple[bytes, str]:
    return generate_latest(), CONTENT_TYPE_LATEST


def metrics_enabled() -> bool:
    return get_settings().metrics_enabled
