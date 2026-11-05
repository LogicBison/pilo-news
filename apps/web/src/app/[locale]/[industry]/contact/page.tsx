import type { Metadata } from "next";
import { notFound } from "next/navigation";

import { ContactForm } from "@/components/ContactForm";
import { getIndustry } from "@/lib/api";
import { fallbackIndustry } from "@/lib/fallback";
import { resolveLocale, t } from "@/lib/i18n";
import { pageMetadata } from "@/lib/seo";

type Params = { params: Promise<{ locale: string; industry: string }> };

export async function generateMetadata({ params }: Params): Promise<Metadata> {
  const { locale, industry } = await params;
  const resolved = resolveLocale(locale);
  const result = await getIndustry(industry, resolved);
  const name = result.ok ? result.data.name : industry;
  return pageMetadata({
    title: t(resolved, "contact.title", { industry: name }),
    description: t(resolved, "contact.description", { industry: name }),
    path: `/${industry}/contact`,
    locale: resolved,
  });
}

export default async function ContactPage({ params }: Params) {
  const { locale, industry } = await params;
  const resolved = resolveLocale(locale);
  const result = await getIndustry(industry, resolved);
  if (!result.ok && result.status === 404) notFound();
  const channel = result.ok ? result.data : fallbackIndustry(industry);
  const email = process.env.CONTACT_TO ?? "news@example.com";

  return (
    <div className="grid gap-8 lg:grid-cols-[minmax(0,2fr)_minmax(280px,1fr)]">
      <div>
        <h1 className="text-3xl font-extrabold tracking-tight text-[var(--sn-text)]">
          {t(resolved, "contact.title", { industry: channel.name })}
        </h1>
        <p className="mt-3 max-w-2xl text-base text-[var(--sn-muted)]">
          {t(resolved, "contact.description", { industry: channel.name })}
        </p>
        <p className="mt-3 text-sm text-[var(--sn-muted)]">
          {t(resolved, "contact.emailLabel")}:{" "}
          <a href={`mailto:${email}`} className="font-semibold underline">
            {email}
          </a>
        </p>
        <div className="mt-6">
          <ContactForm industry={industry} locale={resolved} />
        </div>
      </div>
      <aside className="sn-card sn-card-surface p-5">
        <h2 className="text-sm font-semibold uppercase tracking-[0.14em] text-[var(--sn-muted)]">
          {t(resolved, "footer.disclaimer")}
        </h2>
        <p className="mt-2 text-sm text-[var(--sn-text)]">{channel.disclaimer}</p>
      </aside>
    </div>
  );
}
