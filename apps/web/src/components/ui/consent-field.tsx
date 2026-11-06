import type { ReactNode } from "react";

/**
 * Catalog primitive `ConsentField`. The checkbox sits inside the label, so the
 * whole sentence is the click target (≥24px) while the box itself stays 16px.
 */
export function ConsentField({
  name,
  required = true,
  children,
  className = "text-sm",
  boxClassName = "mt-1 h-4 w-4",
}: {
  name: string;
  required?: boolean;
  children: ReactNode;
  className?: string;
  boxClassName?: string;
}) {
  return (
    <label className={["flex items-start gap-3", className].filter(Boolean).join(" ")}>
      <input type="checkbox" name={name} required={required} className={boxClassName} />
      <span>
        <span className="sn-req" aria-hidden="true">
          *
        </span>{" "}
        {children}
      </span>
    </label>
  );
}
