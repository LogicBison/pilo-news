#!/usr/bin/env node
/**
 * Channel inventory generator/check.
 *
 * Source of truth: GET /v1/industries + APP_BASE_URL + SN_DEFAULT_INDUSTRY.
 * The generated block lives in docs/channel-inventory.md between markers so the
 * surrounding prose stays hand-authored.
 *
 * Usage:
 *   node apps/web/scripts/channel-inventory.mjs           # print the block
 *   node apps/web/scripts/channel-inventory.mjs --write   # update the doc
 *   node apps/web/scripts/channel-inventory.mjs --check   # fail when stale
 *
 * The wrapper ./bin/channels.sh supplies the dev env (ports, base URL, default
 * channel) and is what `./bin/start.sh test` runs.
 */
import { readFileSync, writeFileSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";

const ROOT = resolve(dirname(fileURLToPath(import.meta.url)), "../../..");
const DOC = resolve(ROOT, "docs/channel-inventory.md");
const BEGIN = "<!-- CHANNEL_INVENTORY_BEGIN -->";
const END = "<!-- CHANNEL_INVENTORY_END -->";

const API_URL = (process.env.API_URL || process.env.API_INTERNAL_URL || "http://127.0.0.1:46105").replace(/\/$/, "");
const BASE = (process.env.APP_BASE_URL || "http://localhost:43991").replace(/\/$/, "");
const DEFAULT = process.env.SN_DEFAULT_INDUSTRY || "";
const API_PUBLIC =
  process.env.API_PUBLIC_URL ||
  (process.env.API_PORT ? `http://localhost:${process.env.API_PORT}` : API_URL);

function cell(value) {
  return String(value).replaceAll("|", "\\|");
}

async function fetchChannels() {
  const response = await fetch(`${API_URL}/v1/industries`);
  if (!response.ok) {
    throw new Error(`channel inventory: GET ${API_URL}/v1/industries returned ${response.status}`);
  }
  const payload = await response.json();
  const channels = Array.isArray(payload?.data) ? payload.data : [];
  if (channels.length === 0) throw new Error("channel inventory: API returned no channels");
  return channels;
}

export async function buildBlock() {
  const channels = await fetchChannels();
  const defaultSlug = DEFAULT || channels[0].slug;
  const rows = channels.map((channel, index) => {
    const slug = channel.slug;
    const isDefault = slug === defaultSlug ? "root" : "";
    return `| ${index + 1} | ${cell(channel.name)} | \`${slug}\` | ${BASE}/${slug} | ${BASE}/es/${slug} | ${cell(channel.theme_summary?.layout ?? "unknown")} | ${isDefault} |`;
  });

  return [
    BEGIN,
    `**Base URL:** ${BASE} · **Default channel:** \`/${defaultSlug}\` (root \`/\` redirects) · **Admin:** ${BASE}/admin · **API health:** ${API_PUBLIC}/v1/health`,
    `**Channels:** ${channels.length}`,
    "",
    "| # | Channel | Slug | English | Spanish | Layout | Default |",
    "|---|---|---|---|---|---|---|",
    ...rows,
    "",
    "**Patterns:** `/{slug}/search` · `/{slug}/about` · `/{slug}/contact` · `/{slug}/article/{id}` · `/es/{slug}/...`",
    END,
  ].join("\n");
}

function template(block) {
  return `# Channel inventory

**What this is:** the canonical list of live channels, slugs, localized URLs, layout and the default channel.
**Status:** Generated ${new Date().toISOString().slice(0, 10)} · **Needs:** re-generate after any channel change; a stale file fails the local test gate.
**Source:** \`GET /v1/industries\` + \`APP_BASE_URL\` + \`SN_DEFAULT_INDUSTRY\`. The committed file reflects the environment base used at generation time; regenerate with the production base for a production inventory.

## Inventory

${block}

## How to keep it updated

1. Add or remove a channel (profile import or admin console).
2. Run \`./bin/channels.sh --write\` with the stack up.
3. Run \`./bin/channels.sh --check\` (or \`./bin/start.sh test\`); it fails when this file is stale.
4. Commit the regenerated file with the channel change.

The generated block is the only machine-owned part — edit the prose outside the markers by hand.

## Next action

\`./bin/channels.sh --write\` after any channel change.
`;
}

function extractBlock(text) {
  const start = text.indexOf(BEGIN);
  const end = text.indexOf(END);
  if (start === -1 || end === -1 || end < start) return null;
  return text.slice(start, end + END.length);
}

async function main() {
  const mode = process.argv[2] ?? "--print";
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
    writeFileSync(DOC, current.replace(existing, block));
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

  throw new Error(`unknown mode '${mode}' (use --print, --write or --check)`);
}

const isMain = process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href;
if (isMain) {
  main().catch((error) => {
    console.error(error instanceof Error ? error.message : String(error));
    process.exit(1);
  });
}
