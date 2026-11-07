"use client";

export type FunnelEvent =
  | "cta_impression"
  | "cta_click"
  | "lead_form_start"
  | "lead_submit"
  | "question_submit"
  | "asset_interest"
  | "brief_confirm"
  | "desk_enter";

interface TrackOptions {
  /** Null on the apex lobby: the event belongs to no single desk. */
  industry?: string | null;
  /** Cross-desk event surface, e.g. "lobby". */
  surface?: string;
  locale: string;
  placement: string;
  articleId?: string;
  result?: string;
}

export function sessionHash(): string {
  if (typeof window === "undefined") return "";
  const key = "sn_session";
  let value = window.sessionStorage.getItem(key);
  if (!value) {
    const uuid =
      typeof crypto !== "undefined" && typeof crypto.randomUUID === "function"
        ? crypto.randomUUID()
        : `${Date.now().toString(36)}${Math.random().toString(36).slice(2)}`;
    value = uuid.replaceAll("-", "");
    window.sessionStorage.setItem(key, value);
  }
  return value;
}

export function track(event: FunnelEvent, options: TrackOptions): void {
  if (typeof window === "undefined") return;
  const payload = {
    industry: options.industry ?? null,
    surface: options.surface ?? "",
    event,
    placement: options.placement,
    locale: options.locale,
    article_id: options.articleId ?? null,
    session_hash: sessionHash(),
    result: options.result ?? null,
  };
  if (!options.industry && !options.surface) return;

  try {
    void fetch("/api/proxy/v1/cta-events", {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify(payload),
      keepalive: true,
    });
  } catch {
    /* analytics must never break the page */
  }
}
