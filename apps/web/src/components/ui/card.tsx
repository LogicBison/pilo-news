import type { HTMLAttributes, ReactNode } from "react";

export type CardVariant = "flat" | "elevated" | "inset";

const VARIANT: Record<CardVariant, string> = {
  flat: "sn-card",
  elevated: "sn-card sn-card-surface",
  inset: "sn-card",
};

/** Catalog primitive `Card`. Radius is forced to 0 under `[data-skin]`. */
export function Card({
  variant = "flat",
  interactive = false,
  as: Tag = "div",
  className = "",
  children,
  ...rest
}: HTMLAttributes<HTMLElement> & {
  variant?: CardVariant;
  interactive?: boolean;
  as?: "div" | "section" | "aside" | "article";
  children: ReactNode;
}) {
  const classes = [VARIANT[variant], interactive ? "sn-card-interactive" : "", className]
    .filter(Boolean)
    .join(" ");
  return (
    <Tag className={classes} {...rest}>
      {children}
    </Tag>
  );
}
