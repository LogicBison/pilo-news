-- 011_seed_asset_offers.sql
-- Which gated reference asset each channel offers, kept in channel config (R16:
-- placement and offer come from JSONB, not JSX).
-- Idempotent: the key is set only when absent, so an operator edit always wins.

UPDATE industries
SET cta = jsonb_set(cta, '{asset}', to_jsonb('legal-regulatory-calendar'::text), true)
WHERE slug = 'legal' AND cta -> 'asset' IS NULL;

UPDATE industries
SET cta = jsonb_set(cta, '{asset}', to_jsonb('cybersecurity-kev-digest'::text), true)
WHERE slug = 'cybersecurity' AND cta -> 'asset' IS NULL;
