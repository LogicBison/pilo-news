"use client";

const STORAGE_KEY = "sn_utm";
const KEYS = ["utm_source", "utm_medium", "utm_campaign", "utm_term", "utm_content"] as const;

type Utm = Partial<Record<(typeof KEYS)[number], string>>;

/** Cache the inbound campaign parameters for the rest of the browser session. */
export function captureUtm(): Utm {
  if (typeof window === "undefined") return {};
  let stored: Utm = {};
  try {
    stored = JSON.parse(window.sessionStorage.getItem(STORAGE_KEY) ?? "{}") as Utm;
  } catch {
    stored = {};
  }
  const params = new URLSearchParams(window.location.search);
  let changed = false;
  for (const key of KEYS) {
    const value = params.get(key);
    if (value) {
      stored[key] = value.slice(0, 120);
      changed = true;
    }
  }
  if (changed) {
    try {
      window.sessionStorage.setItem(STORAGE_KEY, JSON.stringify(stored));
    } catch {
      /* storage may be blocked; the lead still submits */
    }
  }
  return stored;
}

export function readUtm(): Utm {
  if (typeof window === "undefined") return {};
  try {
    return JSON.parse(window.sessionStorage.getItem(STORAGE_KEY) ?? "{}") as Utm;
  } catch {
    return {};
  }
}

export function submitUtm(): Utm {
  return captureUtm();
}
