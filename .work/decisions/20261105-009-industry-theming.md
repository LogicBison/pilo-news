# ADR 009 - Industry theming model: data-driven tokens + layout variants

**Status:** Decided · 2026-11-05 · **Decision authority:** prepared under owner instruction "prepare everything"; ratification tracked in `HANDOFF.md` O1.
**Needs:** owner ratification (HANDOFF O1-O3) - review action, not a blocker.

**Decides:** how each channel gets a distinct, professional skin without forking the app.

## Context

- Brief: each site must be "single-themed, professionally suited (UI+UIX+SKIN+STYLING+CSS+LOOKS)" for its industry.
- Five industries at launch, "any industry supported by the system" later - so theming must be additive data, not code per vertical.
- Design quality still matters: tokens alone can look generic if layout doesn't adapt to content type.

## Decision

- **Theme schema (versioned `v1`)** stored in `industries.theme` JSONB:
  `{ schema_version, colors: { bg, surface, text, muted, primary, accent, border }, typography: { heading_font, body_font, scale }, shape: { radius, shadow }, layout: { variant, density, hero, columns } }`.
- **Two-layer rendering:**
  1. CSS custom properties injected on `<html>` per request (no FOUC, no client JS).
  2. One of three **layout variants** - `editorial` (serif, generous whitespace - legal/health), `professional` (dense, data-forward - financial/logistics), `academic` (structured, calm - education) - chosen by the industry config, not by hardcoded slug checks.
- **Component contract:** shared primitives (`Hero`, `StoryCard`, `Splash`, `TopicRail`, `Disclaimer`, `Footer`) read tokens only; variants adjust composition/spacing, not business logic.
- **Per-channel disclaimers** are content (JSONB, per locale), rendered by `Disclaimer` and included in metadata where required.
- **Validation:** theme JSON is validated by a Pydantic model at startup and by an admin endpoint; unknown schema versions fail fast in CI, not at runtime.
- **Design guardrails:** WCAG AA contrast checks in CI for every theme pair; max 2 font families; no background images without alt/attribution.

## Consequences

- **Positive:** new industry = data + assets, no page forks; consistent structure; contrast/quality gates automated.
- **Negative:** three variants may not fit a future industry (add a variant, still no page fork); token discipline requires review.
- **Neutral:** a full design-system package (`.ai.ui`) can later supply tokens/components without changing the model.

## Alternatives considered

| Option | Why rejected |
|--------|--------------|
| One page tree per industry | Unmaintainable duplication; drift |
| Single generic theme with color swap | Fails "professionally suited to each industry" |
| Runtime CSS-in-JS theming | Client cost + FOUC; SSR tokens are simpler |
| Hosted page builder | Loses control, performance, and API integration |

## References

- Doc 01 § success criteria S1
- Doc 04 §2 (channels), §10
- SPEC `.work/features/industry-sites/20261105-SPEC.md` R4-R6
- `.work/plans/20261105-personas-v1.md`

---

## Next action

None - decision recorded; execution is tracked by the relevant SPEC and the master plan (`@plan-master greenfield`).
