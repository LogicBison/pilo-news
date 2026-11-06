-- Offer rungs: question and gated-asset leads, plus their funnel events.
-- Idempotent: constraints are dropped and re-added, the column is IF NOT EXISTS.

ALTER TABLE leads DROP CONSTRAINT IF EXISTS leads_kind_check;
ALTER TABLE leads
    ADD CONSTRAINT leads_kind_check
    CHECK (kind IN ('consultation', 'brief', 'question', 'asset'));

ALTER TABLE leads ADD COLUMN IF NOT EXISTS asset TEXT;

ALTER TABLE cta_events DROP CONSTRAINT IF EXISTS cta_events_event_check;
ALTER TABLE cta_events
    ADD CONSTRAINT cta_events_event_check
    CHECK (
        event IN (
            'cta_impression',
            'cta_click',
            'lead_form_start',
            'lead_submit',
            'question_submit',
            'asset_interest',
            'brief_confirm'
        )
    );
