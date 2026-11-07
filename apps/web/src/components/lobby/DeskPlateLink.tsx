"use client";

import type { ReactNode } from "react";

import { track } from "@/lib/analytics";

/**
 * A desk plate. The click is measured before the browser leaves the apex:
 * `desk_enter` is the only signal that says which desks the lobby moves.
 */
export function DeskPlateLink({
  href,
  slug,
  locale,
  label,
  accent,
  children,
}: {
  href: string;
  slug: string;
  locale: "en" | "es";
  label: string;
  accent: string;
  children: ReactNode;
}) {
  return (
    <a
      className="lb-plate"
      href={href}
      style={{ ["--lb-plate-accent" as string]: accent }}
      aria-label={label}
      onClick={() => {
        track("cta_click", { industry: slug, locale, placement: "lobby-desk" });
        track("desk_enter", { industry: slug, locale, placement: "lobby-desk" });
      }}
    >
      {children}
    </a>
  );
}
