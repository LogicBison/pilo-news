import type { Industry } from "@/lib/api";
import type { Skin } from "@/lib/skins";
import { localized } from "@/lib/theme";
import { t, type Locale } from "@/lib/i18n";

/**
 * Per-channel illustration band. The artwork is original in-repo vector art
 * (no third-party licence), rendered behind the channel tagline so the first
 * screen reads as this industry's page, not a shared template.
 */
export function SkinScene({
  skin,
  channel,
  locale,
}: {
  skin: Skin;
  channel: Industry;
  locale: Locale;
}) {
  const tagline = channel.tagline || localized(channel.cta.headline, locale);
  return (
    <figure className="sn-scene">
      {/* eslint-disable-next-line @next/next/no-img-element */}
      <img src={skin.scene} alt="" aria-hidden="true" loading="lazy" decoding="async" />
      <figcaption>
        <span className="sn-eyebrow">{channel.name}</span>
        {tagline ? <span className="sn-scene-line">{tagline}</span> : null}
      </figcaption>
      <span className="sr-only">{t(locale, "proof.label")}</span>
    </figure>
  );
}
