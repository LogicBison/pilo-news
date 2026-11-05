import type { Skin } from "@/lib/skins";

/**
 * Per-channel masthead mark. Inline SVG so it inherits `currentColor` — the
 * brandmark keeps the channel's primary fill and the mark stays legible on it.
 * Line-art only: no licensed icon set, nothing copied from a third party.
 */
export function SkinEmblem({ skin, className }: { skin: Skin; className?: string }) {
  const common = {
    viewBox: "0 0 24 24",
    fill: "none",
    stroke: "currentColor",
    strokeWidth: 1.6,
    strokeLinecap: "round" as const,
    strokeLinejoin: "round" as const,
    "aria-hidden": true,
    focusable: "false" as const,
    className,
  };

  switch (skin.key) {
    case "chambers":
      // scales of justice
      return (
        <svg {...common}>
          <path d="M12 4v15M6.5 19h11M4 8h16" />
          <path d="M4 8l-2.2 4.4a2.6 2.6 0 0 0 4.4 0L4 8Z" />
          <path d="M20 8l-2.2 4.4a2.6 2.6 0 0 0 4.4 0L20 8Z" />
          <circle cx="12" cy="4" r="1.4" />
        </svg>
      );
    case "terminal":
      // ascending bars + trend tick
      return (
        <svg {...common}>
          <path d="M4 19V13M9.3 19V9.5M14.6 19v-4.2M20 19V6" />
          <path d="M3 6.5l5-2.5 5 2 6-3" />
          <path d="M16.5 3H19v2.5" />
        </svg>
      );
    case "sanctuary":
      // open arcs, never closing — calm
      return (
        <svg {...common}>
          <path d="M4 16a8 8 0 0 1 16 0" />
          <path d="M7.5 16a4.5 4.5 0 0 1 9 0" />
          <path d="M3 20h18" />
          <circle cx="12" cy="8" r="1.2" />
        </svg>
      );
    case "campus":
      // open book
      return (
        <svg {...common}>
          <path d="M12 7.5C10 6 7 6 4.5 7v11c2.5-1 5.5-1 7.5.5 2-1.5 5-1.5 7.5-.5V7c-2.5-1-5.5-1-7.5.5Z" />
          <path d="M12 7.5v11" />
          <path d="M6.8 10.2c1.2-.3 2.6-.2 3.6.2M6.8 13.2c1.2-.3 2.6-.2 3.6.2" />
        </svg>
      );
    case "network":
      // routed nodes
      return (
        <svg {...common}>
          <circle cx="5" cy="18" r="2" />
          <circle cx="12" cy="9" r="2" />
          <circle cx="19" cy="15" r="2" />
          <path d="M6.4 16.4 10.7 10.6M13.6 10.6l3.9 3.3" strokeDasharray="3 2.5" />
        </svg>
      );
    case "sentinel":
      // shield with check
      return (
        <svg {...common}>
          <path d="M12 3.5l7 3v5.8c0 3.6-2.9 6.6-7 8.2-4.1-1.6-7-4.6-7-8.2V6.5l7-3Z" />
          <path d="M9 12.2l2.1 2.1 4-4.3" />
        </svg>
      );
    case "lab":
      // cell with nucleus
      return (
        <svg {...common}>
          <circle cx="12" cy="12" r="8" />
          <circle cx="12" cy="12" r="3" />
          <circle cx="17" cy="8" r="1" />
          <circle cx="8" cy="16" r="1" />
        </svg>
      );
  }
}
