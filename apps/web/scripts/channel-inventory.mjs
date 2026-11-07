#!/usr/bin/env node
/**
 * Channel inventory generator/check.
 *
 * Channels come from the live API when it answers (authoritative: includes
 * channels created from the admin console) and from the deployment profiles on
 * disk otherwise (CI, docs-only check). The address shape is environment-free on
 * purpose: a channel is `{slug}.<channel-domain>`, never a literal port, so the
 * committed file is identical on every machine and the check can run in CI.
 *
 * The generated block lives in docs/channel-inventory.md between markers so the
 * surrounding prose stays hand-authored.
 *
 * Usage:
 *   node apps/web/scripts/channel-inventory.mjs           # print the block
 *   node apps/web/scripts/channel-inventory.mjs --write   # update the doc
 *   node apps/web/scripts/channel-inventory.mjs --check   # fail when stale
 *   node apps/web/scripts/channel-inventory.mjs --urls    # print concrete URLs for this env
 *
 * The wrapper ./bin/channels.sh supplies the env (ports, base URL, default
 * channel) and is what `./bin/start.sh test` and CI run.
 */
import { readFileSync, readdirSync, writeFileSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";

const ROOT = resolve(dirname(fileURLToPath(import.meta.url)), "../../..");
const DOC = resolve(ROOT, "docs/channel-inventory.md");
const PROFILES = resolve(ROOT, "apps/api/config/deployments");
const BEGIN = "<!-- CHANNEL_INVENTORY_BEGIN -->";
const END = "<!-- CHANNEL_INVENTORY_END -->";

const API_URL = (process.env.API_URL || process.env.API_INTERNAL_URL || "http://127.0.0.1:46105").replace(/\/$/, "");
const BASE = (process.env.APP_BASE_URL || "http://localhost:43991").replace(/\/$/, "");
const DEFAULT = process.env.SN_DEFAULT_INDUSTRY || "";
const DOMAIN =
  process.env.SN_CHANNEL_DOMAIN ||
  (process.env.APP_ENV === "prd" ? process.env.APP_DOMAIN || "" : "");
const API_PUBLIC =
  process.env.API_PUBLIC_URL ||
  (process.env.API_PORT ? `http://localhost:${process.env.API_PORT}` : API_URL);

function cell(value) {
  return String(value).replaceAll("|", "\\|");
}

/** Live API first: it is the only source that knows console-created channels. */
async function fetchChannels() {
  try {
    const response = await fetch(`${API_URL}/v1/industries`, {
      signal: AbortSignal.timeout(3000),
    });
    if (!response.ok) return null;
    const payload = await response.json();
    const channels = Array.isArray(payload?.data) ? payload.data : [];
    if (channels.length === 0) return null;
    return channels.map((channel) => ({
      slug: channel.slug,
      name: channel.name,
      layout: channel.theme_summary?.layout ?? "unknown",
      order: null,
    }));
  } catch {
    return null;
  }
}

/** Offline fallback: every deployment profile's enabled industries. */
function loadProfiles() {
  let files = [];
  try {
    files = readdirSync(PROFILES).filter((name) => name.endsWith(".json"));
  } catch {
    return null;
  }
  const bySlug = new Map();
  for (const file of files) {
    let profile;
    try {
      profile = JSON.parse(readFileSync(resolve(PROFILES, file), "utf8"));
    } catch {
      continue;
    }
    for (const industry of profile?.industries ?? []) {
      if (!industry?.slug || industry.enabled === false) continue;
      if (bySlug.has(industry.slug)) continue;
      bySlug.set(industry.slug, {
        slug: industry.slug,
        name: industry.name ?? industry.slug,
        layout: industry.theme?.layout ?? "unknown",
        order: typeof industry.sort_order === "number" ? industry.sort_order : 0,
      });
    }
  }
  if (bySlug.size === 0) return null;
  return [...bySlug.values()].sort((a, b) => a.order - b.order || a.slug.localeCompare(b.slug));
}

export async function loadChannels() {
  const live = await fetchChannels();
  if (live) return { channels: live, source: "live API (`GET /v1/industries`)" };
  const offline = loadProfiles();
  if (offline) return { channels: offline, source: "deployment profiles (`apps/api/config/deployments/`)" };
  throw new Error("channel inventory: no channels from the API or the deployment profiles");
}

const HOST = "{slug}.<channel-domain>";

export async function buildBlock() {
  const { channels } = await loadChannels();
  const rows = channels.map((channel, index) => {
    const slug = channel.slug;
    return `| ${index + 1} | ${cell(channel.name)} | \`${slug}\` | \`${slug}.<channel-domain>/\` | \`${slug}.<channel-domain>/es\` | ${cell(channel.layout)} |`;
  });

  // Nothing environment-specific in here: no port, no scheme, no default
  // channel. Those are deployment settings, and baking one machine into this
  // file is what made the old inventory impossible to check in CI.
  return [
    BEGIN,
    `**Channels:** ${channels.length} · **Channel host:** \`${HOST}\` (\`SN_CHANNEL_DOMAIN\`: \`localhost\` in dev, \`APP_DOMAIN\` in prd)`,
    "",
    "| # | Channel | Slug | English | Spanish | Layout |",
    "|---|---|---|---|---|---|",
    ...rows,
    "",
    "**Path form:** `/{about|contact|search|briefs|references}` · `/topic/{slug}` · `/article/{id}` · `/feed.xml` · `/es/...` for Spanish",
    "**Compatibility:** `{apex}/{slug}/...` still renders and canonicalises to the channel host. `/admin` is apex-only.",
    "**Root `/`** is the lobby (`/services`, `/privacy`, `/terms` beside it); `SN_DEFAULT_INDUSTRY` now only drives the 404 home link.",
    "**Concrete URLs for this machine:** `./bin/channels.sh --urls`",
    END,
  ].join("\n");
}

function template(block) {
  const today = new Date().toISOString().slice(0, 10);
  return `# Channel inventory

**What this is:** the canonical list of live channels: name, slug, address, layout. The address of a channel is its own subdomain, never a path on the apex.
**Status:** Generated ${today} from the live API or the deployment profiles · **Needs:** nothing manual — \`./bin/start.sh test\` and CI fail when this file is stale.
**Source:** the live API when it answers (it knows channels created from the admin console), the deployment profiles otherwise. The generated block is deliberately environment-free: no port, no scheme, no default channel. Those are deployment settings, and baking one machine into this file is what made the previous inventory impossible to check anywhere but the machine that wrote it.

## Inventory

${block}

## How to keep it updated

It cannot drift silently. Three gates, cheapest first:

1. \`./bin/start.sh migrate\` warns when the file no longer matches the channels in the database.
2. \`./bin/start.sh test\` runs \`./bin/channels.sh --check\` after the API and UI checks.
3. CI runs the same check with no server and no env file — from the deployment profiles — so a profile edit without a regenerated inventory fails the build.

Regenerate, then commit:

\`\`\`bash
./bin/channels.sh --write    # live API first, profiles as fallback
./bin/channels.sh --check    # must print ok
./bin/channels.sh --urls     # concrete URLs for this machine, including the port
\`\`\`

The generated block between the markers is machine-owned. Edit the prose outside them by hand.

## Next action

Nothing while the check is green. On a channel change: \`./bin/channels.sh --write\` and commit.
`;
}

function extractBlock(text) {
  const start = text.indexOf(BEGIN);
  const end = text.indexOf(END);
  if (start === -1 || end === -1 || end < start) return null;
  return text.slice(start, end + END.length);
}

/** Concrete, machine-specific URLs - for a screenshot, an email, a handoff. */
function printUrls() {
  const hosts = DOMAIN
    ? { pattern: (slug) => `${DOMAIN === "localhost" ? "http" : "https"}://${slug}.${DOMAIN}${BASE.match(/:\d+$/)?.[0] ?? ""}`, kind: "channel host" }
    : { pattern: (slug) => `${BASE}/${slug}`, kind: "path (no channel domain configured)" };
  return loadChannels().then(({ channels }) => {
    console.log(`# ${hosts.kind} · base ${BASE} · domain ${DOMAIN || "(none)"}`);
    for (const channel of channels) {
      console.log(`${channel.slug.padEnd(20)} ${hosts.pattern(channel.slug)}/   ${hosts.pattern(channel.slug)}/es`);
    }
  });
}

async function main() {
  const mode = process.argv[2] ?? "--print";

  if (mode === "--urls") {
    await printUrls();
    return;
  }

  const block = await buildBlock();

  if (mode === "--print") {
    process.stdout.write(block + "\n");
    return;
  }

  if (mode === "--write") {
    let current = "";
    try {
      current = readFileSync(DOC, "utf8");
    } catch {
      writeFileSync(DOC, template(block));
      console.log(`channel inventory: wrote ${DOC} (${block.split("\n").length} lines)`);
      return;
    }
    const existing = extractBlock(current);
    if (!existing) {
      throw new Error(`channel inventory: markers missing in ${DOC}; restore the generated block or delete the file`);
    }
    // The status line is machine-owned too, so a regeneration is visible in the diff.
    const { source } = await loadChannels();
    const today = new Date().toISOString().slice(0, 10);
    const status =
      `**Status:** Generated ${today} from ${source} · ` +
      "**Needs:** nothing manual — `./bin/start.sh test` and CI fail when this file is stale.";
    const refreshed = current
      .replace(existing, block)
      .replace(/^\*\*Status:\*\*.*$/m, status);
    if (refreshed === current) {
      console.log("channel inventory: already current");
      return;
    }
    writeFileSync(DOC, refreshed);
    console.log(`channel inventory: updated ${DOC}`);
    return;
  }

  if (mode === "--check") {
    let current = "";
    try {
      current = readFileSync(DOC, "utf8");
    } catch {
      throw new Error(`channel inventory: ${DOC} is missing; run ./bin/channels.sh --write`);
    }
    const existing = extractBlock(current);
    if (!existing) throw new Error(`channel inventory: generated block missing in ${DOC}`);
    if (existing !== block) {
      throw new Error(`channel inventory: ${DOC} is stale; run ./bin/channels.sh --write`);
    }
    console.log("channel inventory: ok");
    return;
  }

  throw new Error(`unknown mode '${mode}' (use --print, --write, --check or --urls)`);
}

const isMain = process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href;
if (isMain) {
  main().catch((error) => {
    console.error(error instanceof Error ? error.message : String(error));
    process.exit(1);
  });
}
