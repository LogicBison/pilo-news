# ADR 004 - Frontend: Next.js 15 + React 19 + Tailwind 4

**Status:** Decided · 2026-11-05 · **Decision authority:** prepared under owner instruction "prepare everything"; ratification tracked in `HANDOFF.md` O1.
**Needs:** owner ratification (HANDOFF O1-O3) - review action, not a blocker.

**Decides:** how industry sites are rendered.

## Context

- Reference site is a content-first landing/news site: nav, hero, story grid, article pages, contact form. SEO and fast first paint matter (NFR-2, NFR-11).
- The reference implementation is Next.js 15 App Router with `[locale]` routing and Tailwind 4 - working code to reuse.
- Each channel needs a distinct skin without forking pages (doc 03 adjacency: new verticals add data, not code).

## Decision

Use **Next.js 15.1.8 (App Router, RSC) + React 19.1.0 + Tailwind CSS 4.1.6 + TypeScript 5.8**:

- Public pages are **server components**; data fetched from `/v1` server-side with `next: { revalidate }` (ISR 60 s, article pages 300 s).
- **Route shape:** `/[locale]/[industry]` home, `/[locale]/[industry]/article/[id]`, `/[locale]/[industry]/about`, `/[locale]/[industry]/contact`, plus channel-agnostic `/`→locale+default industry redirect and `/search`.
- **Theming:** server-injected CSS custom properties from `industries.theme` (colors, fonts, radii) + a small set of layout variants (`editorial`, `compact`, `professional`); no per-industry page forks.
- **SEO:** `generateMetadata` per channel/locale (title, description, canonical, `hreflang`, OpenGraph), JSON-LD `NewsArticle`/`ItemList`, sitemap route handlers.
- **No client-side data layer** for first paint; small client islands only for the locale switch, search box, and contact form.
- **Fonts:** `next/font` with system fallback; no third-party font CDN by default (privacy + performance).

## Consequences

- **Positive:** SSR/ISR + RSC give fast LCP and crawlable HTML; existing reference UI logic transfers; channel theming stays data-driven.
- **Negative:** Next.js majors move quickly (pin + upgrade deliberately); RSC mental model has a learning curve; ISR needs cache invalidation awareness on publish (acceptable 60 s staleness).
- **Neutral:** a static Astro site would be lighter but loses the reference implementation and server-side API composition.

## Alternatives considered

| Option | Why rejected |
|--------|--------------|
| React + Vite SPA | Weak SEO/first paint; needs a separate SSR layer |
| Astro | Great for static content, but discards reference code and adds a new mental model |
| Nuxt/Vue | No reuse; team fluency is React/Next here |
| Static site generator + rebuilds | Rebuild storm risk with frequent updates; ISR covers it |

## References

- `/mnt/work/Projects/LogicBison/frontend/package.json`
- `DOCS_TECH_STACK.md` §1
- SPEC `.work/features/industry-sites/20261105-SPEC.md`

---

## Next action

None - decision recorded; execution is tracked by the relevant SPEC and the master plan (`@plan-master greenfield`).
