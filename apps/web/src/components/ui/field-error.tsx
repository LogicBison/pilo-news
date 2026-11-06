/**
 * Catalog compound `FieldError`. One polite live region per form; the field it
 * belongs to sets `aria-invalid` + `aria-describedby` (see `TextField`).
 */
export function FieldError({
  message,
  id,
  className = "mt-3",
}: {
  message: string;
  id?: string;
  className?: string;
}) {
  return (
    <div
      id={id}
      aria-live="polite"
      className={["text-sm text-[var(--sn-danger)]", className].filter(Boolean).join(" ")}
    >
      {message}
    </div>
  );
}
