import type { ButtonHTMLAttributes, ReactNode } from "react";

export type ButtonVariant = "primary" | "ghost";
export type ButtonSize = "sm" | "md" | "lg";

const VARIANT: Record<ButtonVariant, string> = {
  primary: "sn-btn",
  ghost: "sn-btn sn-btn-ghost",
};

const SIZE: Record<ButtonSize, string> = {
  sm: "",
  md: "",
  lg: "",
};

/**
 * Catalog primitive `Button`. Token-backed through `.sn-btn`; focus ring,
 * hover and disabled states live in globals.css so skins cannot fork them.
 */
export function Button({
  variant = "primary",
  size = "md",
  className = "",
  children,
  type = "button",
  ...rest
}: ButtonHTMLAttributes<HTMLButtonElement> & {
  variant?: ButtonVariant;
  size?: ButtonSize;
  children: ReactNode;
}) {
  const classes = [VARIANT[variant], SIZE[size], className].filter(Boolean).join(" ");
  return (
    <button type={type} className={classes} {...rest}>
      {children}
    </button>
  );
}
