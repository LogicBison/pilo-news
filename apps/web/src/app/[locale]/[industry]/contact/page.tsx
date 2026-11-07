import type { Metadata } from "next";
import { notFound } from "next/navigation";

import { ContactForm } from "@/components/ContactForm";
import { SectionHeader } from "@/components/ui/section-header";
import { getIndustry } from "@/lib/api";
import { fallbackIndustry } from "@/lib/fallback";
import { localePath, resolveLocale, t } from "@/lib/i18n";
import { channelBase } from "@/lib/url";
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
    industry,
  });
}

export default async function ContactPage({ params }: Params) {
  const { locale, industry } = await params;
  const resolved = resolveLocale(locale);
  const base = await channelBase(industry);
  const result = await getIndustry(industry, resolved);
  if (!result.ok && result.status === 404) notFound();
  const channel = result.ok ? result.data : fallbackIndustry(industry);
  const configured = process.env.CONTACT_TO?.trim();
  const email = configured ? configured : undefined;

  return (
    <div className="grid gap-8 lg:grid-cols-[minmax(0,2fr)_minmax(280px,1fr)]">
      <div>
        <h1 className="text-3xl font-extrabold tracking-tight text-[var(--sn-text)]">
          {t(resolved, "contact.title", { industry: channel.name })}
        </h1>
        <p className="mt-3 max-w-[65ch] text-base text-[var(--sn-muted)]">
          {t(resolved, "contact.description", { industry: channel.name })}
        </p>
        {email ? (
          <p className="mt-3 text-sm text-[var(--sn-muted)]">
            {t(resolved, "contact.emailLabel")}:{" "}
            <a href={`mailto:${email}`} className="font-semibold underline">
              {email}
            </a>
          </p>
        ) : null}
        <ContactForm industry={industry} locale={resolved} email={email} />
      </div>
      <aside className="border-t border-[var(--sn-border)] pt-4">
        <SectionHeader title={t(resolved, "contact.nextTitle")} weight="semibold" />
        <p className="mt-2 text-sm text-[var(--sn-muted)]">{t(resolved, "contact.nextBody")}</p>
        <p className="mt-4 text-sm text-[var(--sn-muted)]">
          {t(resolved, "contact.privacyNote")}{" "}
          <a
            href={localePath(resolved, `${base}/privacy`)}
            className="font-semibold underline"
          >
            {t(resolved, "footer.privacy")}
          </a>
        </p>
        <div className="mt-6 border-t border-[var(--sn-border)] pt-4">
          <h2 className="text-xs font-semibold uppercase tracking-[0.14em] text-[var(--sn-muted)]">
            {t(resolved, "footer.disclaimer")}
          </h2>
          <p className="mt-2 text-sm text-[var(--sn-text)]">{channel.disclaimer}</p>
        </div>
      </aside>
    </div>
  );
}
