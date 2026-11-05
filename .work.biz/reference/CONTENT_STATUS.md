# Content Status

**Purpose:** Single source of truth for what content exists and whether it is published. Read at session start and before any drafting. Do not recommend publishing anything marked `published`. Every content skill reads this file before drafting and records into it after producing or publishing (see CONVENTIONS § Content Status Protocol).

**Last updated:** <date>

## Summary

| Content type | Total | Published | Ready | Draft | Blocked | Hold |
|--------------|-------|-----------|-------|-------|---------|------|

## By platform

Cross-platform index. Per-platform performance belongs in `pipeline/<platform>-tracker.md`, not here.

| Platform | Role in channel plan | Published | Last publish | Tracker file | Conversations produced |
|----------|---------------------|-----------|--------------|--------------|------------------------|

`Role in channel plan` must match `strategy/channel-plan.md`. If a platform has published items but no role, mark it **`not sanctioned`** and resolve the drift: either amend the channel plan or stop publishing there. A platform with published items and zero conversations is producing authority, not pipeline. Record that honestly rather than leaving the column blank.

## By pillar

A pillar is one of the 3–5 strategic messages the offer stands on, traceable to `strategy/one-pager.md` / `strategy/offer-scope.md` (for example: "fixed-price de-risks platform builds", "solo senior delivery beats agency overhead"). Define the list once here; every Items row names one. Quarterly, `@biz-review quarterly` aggregates conversations per pillar to see which strategic message actually converts.

| Pillar | Pieces | Published | Conversations |
|--------|--------|-----------|---------------|

## Items

Status values: `draft` (needs owner edits) · `ready` (publication-ready) · `published` (live; date + URL required) · `blocked` (say why in Note) · `hold` (say until what in Note).

This file tracks the **active inventory**. Piece directories live under `.work.biz/ideas/<subdir>/<piece>/`. When the operator archives published content (`@biz-archive`), a `published` piece moves to `.work.biz/ideas.archive/<subdir>/<piece>/` (structure mirrored) and gets its own `status.md` carrying its publish record (date, platform/URL, pillar, notes); once that file is written, the piece's row **leaves** this table. Lifetime aggregates (By platform Last publish, By pillar conversations) stay.

Pillar must name one entry from **By pillar**; leave blank only while a piece is unclassified, and never leave a published piece unclassified.

| # | Piece | Pillar | Status | Published | Platform / URL | Note |
|---|-------|--------|--------|-----------|----------------|------|

## What to do after a publish

1. Update this file with the publish date and platform, and refresh the **By platform** and **By pillar** rows.
2. Append the piece to `pipeline/<platform>-tracker.md`. Create it from `templates/work/pipeline/platform-tracker.md.template` if this is the first publish on that platform.
3. Add the piece's entry to `reference/VOICE_RETRO.md` (or record that the owner pass was waived). A publish without a retro entry leaves voice convergence measured on a partial sample.
4. Update `plans/NEXT.md` - remove the completed item, reorder what is left.
5. Update `context/HANDOFF.md` - log the publish.
6. Update `pipeline/pipeline_tracker.md` weekly metrics if it is the same week.
7. If the piece produced a conversation, log it in the tracker's conversations table and in **By pillar**. Those columns are the only ones that connect content to revenue.
