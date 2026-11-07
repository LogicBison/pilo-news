"use client";

import { useMemo, useState } from "react";

import type { ReferenceDetail } from "@/lib/api";
import { t, type Locale } from "@/lib/i18n";

export function ReferenceTable({
  issue,
  locale,
}: {
  issue: ReferenceDetail;
  locale: Locale;
}) {
  const jurisdictions = useMemo(
    () => Array.from(new Set(issue.items.map((item) => item.jurisdiction))).sort(),
    [issue.items],
  );
  const [selected, setSelected] = useState("all");
  const items =
    selected === "all"
      ? issue.items
      : issue.items.filter((item) => item.jurisdiction === selected);

  return (
    <div className="mt-6">
      <div className="flex flex-wrap items-end gap-3">
        <label className="flex flex-col gap-1 text-sm font-semibold text-[var(--sn-text)]">
          {t(locale, "reference.filterLabel")}
          <select
            value={selected}
            onChange={(event) => setSelected(event.target.value)}
            className="rounded border border-[var(--sn-border)] bg-[var(--sn-bg)] px-3 py-2 text-sm font-normal"
          >
            <option value="all">{t(locale, "reference.allJurisdictions")}</option>
            {jurisdictions.map((jurisdiction) => (
              <option key={jurisdiction} value={jurisdiction}>
                {jurisdiction}
              </option>
            ))}
          </select>
        </label>
        <p className="text-xs text-[var(--sn-muted)]">
          {t(locale, "reference.showing", { n: items.length })}
        </p>
      </div>

      <div className="mt-4 overflow-x-auto">
        <table className="w-full text-sm">
          <caption className="sr-only">
            {t(locale, "reference.tableCaption", { date: issue.issue_date })}
          </caption>
          <thead>
            <tr className="border-b border-[var(--sn-border)]">
              <th scope="col" className="p-2 text-left font-semibold">
                {t(locale, "reference.tableDate")}
              </th>
              <th scope="col" className="p-2 text-left font-semibold">
                {t(locale, "reference.tableChange")}
              </th>
              <th scope="col" className="p-2 text-left font-semibold">
                {t(locale, "reference.tableAction")}
              </th>
              <th scope="col" className="p-2 text-left font-semibold">
                {t(locale, "reference.tableSource")}
              </th>
            </tr>
          </thead>
          <tbody>
            {items.map((item) => (
              <tr
                key={`${item.source_url}:${item.date}`}
                className="border-b border-[var(--sn-border)] align-top"
              >
                <td className="whitespace-nowrap p-2 tabular-nums">{item.date}</td>
                <td className="max-w-xl p-2">
                  <p className="font-semibold text-[var(--sn-text)]">{item.headline}</p>
                  <p className="mt-1 text-xs leading-relaxed text-[var(--sn-muted)]">{item.change}</p>
                  <p className="mt-1 text-xs text-[var(--sn-muted)]">{item.jurisdiction}</p>
                </td>
                <td className="max-w-xs p-2 text-xs leading-relaxed text-[var(--sn-text)]">
                  {item.action}
                </td>
                <td className="p-2 text-xs">
                  <a
                    href={item.source_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="underline underline-offset-2"
                  >
                    {item.source_name}
                  </a>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
