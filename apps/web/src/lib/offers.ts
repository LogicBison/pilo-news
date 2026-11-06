import type { Industry, OfferConfig } from "@/lib/api";

/**
 * Effective free offers for a channel. The API already resolves the stored
 * switches; the fallback keeps server-rendered pages safe when an older API
 * response has no `offers` key during a rolling deploy.
 */
export function offersOf(channel: Pick<Industry, "offers">): OfferConfig {
  return {
    consultation: channel.offers?.consultation ?? true,
    brief: channel.offers?.brief ?? true,
    question: channel.offers?.question ?? true,
    asset: channel.offers?.asset ?? false,
  };
}
