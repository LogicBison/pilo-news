import type { Metadata } from "next";
import { notFound } from "next/navigation";

// Publisher-facing. The API owns the numbers; this page renders one source's
// own record under an unguessable token, and nothing else.
const API_BASE = process.env.API_INTERNAL_URL ?? "http://api:8080";

export const dynamic = "force-dynamic";

export const metadata: Metadata = {
  title: "Reading record",
  robots: { index: false, follow: false },
};

type Summary = {
  name: string;
  industry: string;
  items_30d: number;
  clicks_30d: number;
  attempts_30d: number;
  success_rate_30d: number | null;
  period_days: number;
};

async function load(token: string): Promise<Summary | null> {
  try {
    const response = await fetch(`${API_BASE.replace(/\/$/, "")}/v1/traffic/${token}`, {
      cache: "no-store",
    });
    if (!response.ok) return null;
    const body = (await response.json()) as { data?: Summary };
    return body.data ?? null;
  } catch {
    return null;
  }
}

export default async function TrafficPage({ params }: { params: Promise<{ token: string }> }) {
  const { token } = await params;
  const summary = await load(token);
  if (!summary) notFound();
  const rate =
    summary.success_rate_30d === null ? "no checks yet" : `${Math.round(summary.success_rate_30d * 100)}%`;

  return (
    <main className="mx-auto flex min-h-screen max-w-2xl flex-col justify-center gap-6 px-6 py-16">
      <p className="text-sm font-semibold uppercase tracking-[0.16em] text-[var(--sn-muted)]">
        Reading record · last {summary.period_days} days
      </p>
      <h1 className="text-3xl font-semibold">{summary.name}</h1>
      <p className="text-base leading-relaxed text-[var(--sn-text)]">
        We linked to <strong>{summary.items_30d}</strong> of your stories and sent{" "}
        <strong>{summary.clicks_30d}</strong> reader clicks to your site in the last{" "}
        {summary.period_days} days.
      </p>
      <dl className="grid grid-cols-2 gap-4 text-sm">
        <div>
          <dt className="text-[var(--sn-muted)]">Requests to your feed</dt>
          <dd className="text-lg">{summary.attempts_30d}</dd>
        </div>
        <div>
          <dt className="text-[var(--sn-muted)]">Successful fetches</dt>
          <dd className="text-lg">{rate}</dd>
        </div>
      </dl>
      <p className="text-xs leading-relaxed text-[var(--sn-muted)]">
        Clicks are counted when a reader follows our &ldquo;read the full story&rdquo; link. We
        store one counter per story — no reader identifiers, no IP addresses, no cookies.
      </p>
      <p className="text-xs text-[var(--sn-muted)]">
        Desk: {summary.industry}. This page is private to its link and is not indexed.
      </p>
    </main>
  );
}
