import type { ReactNode, TextareaHTMLAttributes } from "react";

const WEIGHT = { semibold: "font-semibold", medium: "font-medium" } as const;

export type TextAreaProps = Omit<TextareaHTMLAttributes<HTMLTextAreaElement>, "id"> & {
  label: ReactNode;
  name: string;
  id?: string;
  hint?: ReactNode;
  error?: string;
  optionalLabel?: ReactNode;
  labelWeight?: "semibold" | "medium";
  wrapperClassName?: string;
};

/** Catalog primitive `TextArea` — same label/error wiring as `TextField`. */
export function TextArea({
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
}: TextAreaProps) {
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
      <textarea
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
