import Image from "next/image";

import logicbisonIcon from "@/assets/logicbison-icon.png";

import { t, type Locale } from "@/lib/i18n";

/**
 * The house credit: the LogicBison mark and wordmark as one link.
 * Used in every footer so the attribution is the same shape on every skin.
 */
export function DevelopedBy({ locale }: { locale: Locale }) {
  return (
    <a
      className="sn-credit"
      href="https://logicbison.com"
      target="_blank"
      rel="noopener noreferrer"
    >
      <Image
        src={logicbisonIcon}
        alt=""
        width={20}
        height={20}
        className="sn-credit-mark"
      />
      <span className="sn-credit-copy">
        <span className="sn-credit-label">{t(locale, "footer.developedBy")}</span>
        <span className="sn-credit-name">LogicBison</span>
      </span>
      <span className="sn-credit-arrow" aria-hidden="true">
        &#8599;
      </span>
    </a>
  );
}
