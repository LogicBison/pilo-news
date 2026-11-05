"use client";

import { usePathname } from "next/navigation";
import { useEffect } from "react";

import { t } from "@/lib/i18n";

export default function IndustryError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  const pathname = usePathname() ?? "/";
  const locale = pathname.startsWith("/es") ? "es" : "en";

  useEffect(() => {
    console.error("page_error", error.digest ?? "unknown");
  }, [error]);

  return (
    <div
      role="alert"
      className="rounded-[calc(var(--sn-radius)+6px)] border border-red-300 bg-red-50 p-6 text-red-950 shadow-[var(--sn-elev-1)]"
    >
      <h1 className="text-2xl font-semibold">{t(locale, "states.errorTitle")}</h1>
      <p className="mt-2 text-sm">{t(locale, "states.errorBody")}</p>
      <button
        type="button"
        onClick={reset}
        className="mt-4 rounded-full bg-red-900 px-5 py-2 text-sm font-semibold text-white"
      >
        {t(locale, "states.retry")}
      </button>
    </div>
  );
}
