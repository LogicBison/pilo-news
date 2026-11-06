import Link from "next/link";
import type { AnchorHTMLAttributes, HTMLAttributes, ReactNode } from "react";

export type ChipVariant = "filter" | "label" | "topic";

const VARIANT: Record<ChipVariant, string> = {
  filter: "sn-chip sn-chip-link",
  label: "sn-chip",
  topic: "sn-chip sn-chip-link",
};

/** Catalog primitive `Chip` — a static label or a topic/filter link. */
export function Chip({
  variant = "label",
  className = "",
  children,
  ...rest
}: HTMLAttributes<HTMLSpanElement> & {
  variant?: ChipVariant;
  children: ReactNode;
}) {
  const classes = [VARIANT[variant], className].filter(Boolean).join(" ");
  return (
    <span className={classes} {...rest}>
      {children}
    </span>
  );
}

/** Anchor variant of the same surface, for topic rails and filters. */
export function ChipLink({
  variant = "topic",
  className = "",
  href,
  children,
  ...rest
}: Omit<AnchorHTMLAttributes<HTMLAnchorElement>, "href"> & {
  variant?: ChipVariant;
  href: string;
  children: ReactNode;
}) {
  const classes = [VARIANT[variant], className].filter(Boolean).join(" ");
  return (
    <Link href={href} className={classes} {...rest}>
      {children}
    </Link>
  );
}
