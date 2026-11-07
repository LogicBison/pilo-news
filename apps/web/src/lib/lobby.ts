/**
 * The lobby's view model. One place turns `/v1/desks` into what the directory,
 * the board and the footer need, so no component has to know about the request
 * host or the API shape.
 */

import { getDesks, type DeskSummary } from "@/lib/api";
import { localePath, type Locale } from "@/lib/i18n";
import { channelOrigin } from "@/lib/url";

export interface DeskView {
  slug: string;
  name: string;
  tagline: string;
  accent: string;
  /** Absolute canonical URL: the desk's own host, in the requested locale. */
  href: string;
  /** Absolute URL of the desk's Spanish edition. */
  hrefEs: string;
  locales: string[];
  offers: DeskSummary["offers"];
  /** Whole hours between scheduled fetches; the deployment default is 12. */
  hours: number;
  latest: string | null;
}

export interface DesksResult {
  ok: boolean;
  desks: DeskView[];
}

function hoursFrom(minutes: number | null): number {
  const value = minutes && minutes > 0 ? minutes : 720;
  return Math.max(1, Math.round(value / 60));
}

export async function deskViews(locale: Locale): Promise<DesksResult> {
  const result = await getDesks(locale);
  if (!result.ok) return { ok: false, desks: [] };
  const desks = await Promise.all(
    result.data.map(async (desk) => {
      const origin = await channelOrigin(desk.slug);
      return {
        slug: desk.slug,
        name: desk.name,
        tagline: desk.tagline,
        accent: desk.accent,
        href: `${origin}${localePath(locale, "/")}`,
        hrefEs: `${origin}/es`,
        locales: desk.locales,
        offers: desk.offers,
        hours: hoursFrom(desk.fetch_interval_minutes),
        latest: desk.latest_published_at,
      } satisfies DeskView;
    }),
  );
  return { ok: true, desks };
}

/** Slug list for the sitemap and for the reserved-segment check. */
export function offerChips(desk: DeskView): { label: string; key: string }[] {
  const chips: { label: string; key: string }[] = [];
  if (desk.offers.asset) chips.push({ key: "offerAsset", label: "lobby.dir.offerAsset" });
  if (desk.offers.brief) chips.push({ key: "offerBrief", label: "lobby.dir.offerBrief" });
  if (desk.offers.question) chips.push({ key: "offerQuestion", label: "lobby.dir.offerQuestion" });
  if (desk.offers.consultation) {
    chips.push({ key: "offerConsultation", label: "lobby.dir.offerConsultation" });
  }
  return chips;
}
