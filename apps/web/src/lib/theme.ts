import type { CSSProperties } from "react";

import type { IndustryTheme } from "@/lib/api";

export const DEFAULT_THEME: IndustryTheme = {
  primary: "#1e3a5f",
  accent: "#8a4b08",
  bg: "#ffffff",
  surface: "#f6f7f9",
  text: "#111827",
  muted: "#4b5563",
  border: "#d8dee6",
  radius: "10px",
  font_heading: "Georgia, Times New Roman, serif",
  font_body: "system-ui, -apple-system, Segoe UI, sans-serif",
  layout: "editorial",
};

const TOKENS = [
  "primary",
  "accent",
  "bg",
  "surface",
  "text",
  "muted",
  "border",
] as const;

export function resolveTheme(theme: Partial<IndustryTheme> | undefined): IndustryTheme {
  const merged = { ...DEFAULT_THEME, ...(theme ?? {}) };
  for (const token of TOKENS) {
    if (!merged[token]) merged[token] = DEFAULT_THEME[token];
  }
  return merged;
}

export function themeStyle(theme: Partial<IndustryTheme> | undefined): CSSProperties {
  const resolved = resolveTheme(theme);
  const danger = contrastRatio("#b91c1c", resolved.bg) >= 4.5 ? "#b91c1c" : "#fca5a5";
  return {
    "--sn-bg": resolved.bg,
    "--sn-surface": resolved.surface,
    "--sn-text": resolved.text,
    "--sn-muted": resolved.muted,
    "--sn-primary": resolved.primary,
    "--sn-accent": resolved.accent,
    "--sn-border": resolved.border,
    "--sn-radius": resolved.radius,
    "--sn-font-heading": resolved.font_heading,
    "--sn-font-body": resolved.font_body,
    "--sn-on-primary": "#ffffff",
    "--sn-shade": "#000000",
    "--sn-danger": danger,
  } as CSSProperties;
}

export function relativeLuminance(hex: string): number {
  const color = hex.replace("#", "");
  if (color.length !== 6) return 0;
  const channels = [0, 2, 4].map((index) => {
    const value = parseInt(color.slice(index, index + 2), 16) / 255;
    return value <= 0.03928 ? value / 12.92 : ((value + 0.055) / 1.055) ** 2.4;
  });
  return 0.2126 * (channels[0] ?? 0) + 0.7152 * (channels[1] ?? 0) + 0.0722 * (channels[2] ?? 0);
}

export function contrastRatio(foreground: string, background: string): number {
  const first = relativeLuminance(foreground);
  const second = relativeLuminance(background);
  const lighter = Math.max(first, second);
  const darker = Math.min(first, second);
  return (lighter + 0.05) / (darker + 0.05);
}

export function localized(value: Record<string, string> | undefined, locale: string): string {
  if (!value) return "";
  return value[locale] ?? value.en ?? "";
}
