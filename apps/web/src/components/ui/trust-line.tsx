import type { ReactNode } from "react";

/**
 * Catalog primitive `TrustLine` — the disclosure / response-expectation line
 * that sits under a form or action panel. Plain text, no icon-only meaning.
 */
export function TrustLine({
  children,
  tone = "muted",
  className = "",
}: {
  children: ReactNode;
  tone?: "muted" | "default";
  className?: string;
}) {
  const color = tone === "muted" ? "text-[var(--sn-muted)]" : "text-[var(--sn-text)]";
  return (
    <p className={["text-xs", color, className].filter(Boolean).join(" ")}>{children}</p>
  );
}
