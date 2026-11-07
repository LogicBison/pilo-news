-- The apex lobby is cross-desk: a CTA there belongs to no single industry, and
-- its funnel is read per surface instead of per channel. Widen the event table
-- rather than inventing a pseudo-channel that would pollute /v1/industries.

ALTER TABLE cta_events ALTER COLUMN industry_id DROP NOT NULL;

ALTER TABLE cta_events ADD COLUMN IF NOT EXISTS surface TEXT NOT NULL DEFAULT '';

-- `desk_enter` is the lobby's own event: a visitor left the apex for a desk.
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
            'brief_confirm',
            'desk_enter'
        )
    );

CREATE INDEX IF NOT EXISTS ix_cta_events_surface_created
    ON cta_events (surface, created_at DESC);
