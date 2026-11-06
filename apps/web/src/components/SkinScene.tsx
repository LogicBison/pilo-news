import Image from "next/image";
import Link from "next/link";

import type { Industry } from "@/lib/api";
import { localePath, t, type Locale } from "@/lib/i18n";
import type { Skin } from "@/lib/skins";

/**
 * Per-channel imagery. Photography is the primary surface (realistic colour,
 * licence recorded per file in `apps/web/public/photos/credits.json`); the
 * line-art SVG stays as the fallback and as the motif/emblem layer.
 * Placements:
 *  - `band`  channel home: full-height photo, captioned with the tagline.
 *  - `strip` article page: short crop with a quiet link back to the channel.
 * The photo is decorative — the caption carries the meaning.
 */
export function SkinScene({
  skin,
  channel,
  locale,
  variant = "band",
}: {
  skin: Skin;
  channel: Industry;
  locale: Locale;
  variant?: "band" | "strip";
}) {
  const home = localePath(locale, `/${channel.slug}`);
  const compact = variant === "strip";
  const illustration = skin.photo.endsWith(".svg");

  return (
    <figure className={compact ? "sn-scene sn-scene-strip" : "sn-scene"}>
      <Image
        src={skin.photo}
        alt=""
        aria-hidden="true"
        fill
        sizes={compact ? "(min-width: 1024px) 768px, 100vw" : "(min-width: 1024px) 1152px, 100vw"}
        className="sn-scene-img"
        loading={compact ? "lazy" : "eager"}
        unoptimized={illustration}
      />
      <figcaption>
        <span className="sn-eyebrow">{channel.name}</span>
        {compact ? (
          <Link href={home} className="sn-scene-link">
            {t(locale, "scene.moreCoverage")}
          </Link>
        ) : (
          <span className="sn-scene-line">{channel.tagline}</span>
        )}
        {skin.credit ? (
          <a className="sn-scene-credit" href={skin.credit.href} target="_blank" rel="noreferrer">
            {skin.credit.label}
          </a>
        ) : null}
      </figcaption>
    </figure>
  );
}
