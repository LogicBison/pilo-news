import type { ReactNode } from "react";

/**
 * Catalog primitive `SectionHeader`. Renders the section `h2` so screens never
 * invent their own heading level; `kicker` adds the eyebrow rule used by the
 * conversion spine.
 */
const WEIGHT = { bold: "font-bold", semibold: "font-semibold" } as const;

export function SectionHeader({
  title,
  description,
  kicker,
  id,
  weight = "bold",
  className = "",
}: {
  title: ReactNode;
  description?: ReactNode;
  kicker?: ReactNode;
  id?: string;
  weight?: "bold" | "semibold";
  className?: string;
}) {
  return (
    <div className={className}>
      {kicker ? (
        <div className="flex items-center gap-2">
          <span className="sn-kicker" aria-hidden="true" />
          <p className="sn-eyebrow">{kicker}</p>
        </div>
      ) : null}
      <h2 id={id} className={["sn-section-title mt-2", WEIGHT[weight], "text-[var(--sn-text)]"].join(" ")}>
        {title}
      </h2>
      {description ? (
        <p className="mt-2 text-sm text-[var(--sn-muted)]">{description}</p>
      ) : null}
    </div>
  );
}
