export default function IndustryLoading() {
  return (
    <div aria-busy="true" aria-live="polite" className="animate-pulse space-y-6">
      <span className="sr-only">Loading stories</span>
      <div className="h-8 w-2/3 rounded bg-[var(--sn-surface)]" />
      <div className="h-64 animate-pulse rounded-[calc(var(--sn-radius)+6px)] bg-[var(--sn-surface)]" />
      <div className="grid gap-5 md:grid-cols-3">
        {[0, 1, 2].map((index) => (
          <div key={index} className="h-48 animate-pulse rounded-[calc(var(--sn-radius)+6px)] bg-[var(--sn-surface)]" />
        ))}
      </div>
    </div>
  );
}
