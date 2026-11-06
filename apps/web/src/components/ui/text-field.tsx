import type { InputHTMLAttributes, ReactNode } from "react";

const WEIGHT = { semibold: "font-semibold", medium: "font-medium" } as const;

export type TextFieldProps = Omit<InputHTMLAttributes<HTMLInputElement>, "id"> & {
  label: ReactNode;
  name: string;
  id?: string;
  hint?: ReactNode;
  error?: string;
  optionalLabel?: ReactNode;
  labelWeight?: "semibold" | "medium";
  wrapperClassName?: string;
};

/**
 * Catalog primitive `TextField`. The label wraps the control (implicit label),
 * required state comes from the native `required` attribute, and an optional
 * `error` wires `aria-invalid` + `aria-describedby` so the message is announced
 * with the field, not only through the form-level live region.
 */
export function TextField({
  label,
  name,
  id,
  hint,
  error,
  optionalLabel,
  labelWeight = "semibold",
  required,
  wrapperClassName = "",
  className = "",
  ...rest
}: TextFieldProps) {
  const fieldId = id ?? name;
  const hintId = hint ? `${fieldId}-hint` : undefined;
  const errorId = error ? `${fieldId}-error` : undefined;
  const describedBy = [hintId, errorId].filter(Boolean).join(" ") || undefined;

  return (
    <label className={[WEIGHT[labelWeight], "flex flex-col gap-1 text-sm", wrapperClassName].filter(Boolean).join(" ")}>
      <span>
        {label}
        {required ? (
          <span className="sn-req" aria-hidden="true">
            {" "}*
          </span>
        ) : null}
        {optionalLabel ? (
          <span className="font-normal text-[var(--sn-muted)]"> ({optionalLabel})</span>
        ) : null}
      </span>
      <input
        id={fieldId}
        name={name}
        required={required}
        aria-invalid={error ? true : undefined}
        aria-describedby={describedBy}
        className={["sn-input", className].filter(Boolean).join(" ")}
        {...rest}
      />
      {hint ? (
        <span id={hintId} className="text-xs font-normal text-[var(--sn-muted)]">
          {hint}
        </span>
      ) : null}
      {error ? (
        <span id={errorId} className="text-xs font-normal text-[var(--sn-danger)]">
          {error}
        </span>
      ) : null}
    </label>
  );
}
