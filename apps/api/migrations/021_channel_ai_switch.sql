-- M21: per-channel AI switch.
--
-- `auto_fetch_enabled` (013) stops new fetches. This column stops the paid part
-- only: the desk keeps fetching and publishing, but no provider call is made for
-- its summaries, desk brief or featured pick. It exists so an operator can park a
-- channel's AI spend without taking the channel down.
--
-- Default TRUE keeps every existing desk summarising exactly as before.

ALTER TABLE industries
    ADD COLUMN IF NOT EXISTS ai_summaries_enabled BOOLEAN NOT NULL DEFAULT TRUE;
