#!/usr/bin/env node
/**
 * Offer inventory generator/check.
 *
 * Joins the live channel payload (offers, cta.asset, cta.kind) with the
 * checked-in offer catalog. The catalog is the recommendation; the API is
 * today's capture state. The two are shown side by side so the inventory
 * cannot claim an offer that the site does not actually capture.
 *
 * Usage:
 *   node .work.biz/scripts/offer-inventory.mjs           # print the block
 *   node .work.biz/scripts/offer-inventory.mjs --write   # update the doc
 *   node .work.biz/scripts/offer-inventory.mjs --check   # fail when stale
 *
 * The wrapper .work.biz/scripts/offers.sh supplies the dev env.
 */
import { existsSync, readFileSync, writeFileSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";

const BIZ = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const DOC = resolve(BIZ, "strategy/offer-inventory.md");
const CATALOG_PATH = resolve(BIZ, "strategy/offers/catalog.json");
const BEGIN = "<!-- OFFER_INVENTORY_BEGIN -->";
const END = "<!-- OFFER_INVENTORY_END -->";

const API_URL = (process.env.API_URL || "http://127.0.0.1:46105").replace(/\/$/, "");
const today = new Date().toISOString().slice(0, 10);

function cell(value) {
  return String(value).replaceAll("|", "\\|");
}

function loadCatalog() {
  const catalog = JSON.parse(readFileSync(CATALOG_PATH, "utf8"));
  if (!catalog?.channels || typeof catalog.channels !== "object") {
    throw new Error("offer inventory: catalog.channels is missing");
  }
  return catalog;
}

async function fetchChannels() {
  const response = await fetch(`${API_URL}/v1/industries`);
  if (!response.ok) {
    throw new Error(`offer inventory: GET ${API_URL}/v1/industries returned ${response.status}`);
  }
  const payload = await response.json();
  const channels = Array.isArray(payload?.data) ? payload.data : [];
  if (channels.length === 0) throw new Error("offer inventory: API returned no channels");
  return channels;
}

async function fetchChannel(slug) {
  const response = await fetch(`${API_URL}/v1/industries/${encodeURIComponent(slug)}`);
  if (!response.ok) {
    throw new Error(`offer inventory: GET /v1/industries/${slug} returned ${response.status}`);
  }
  return (await response.json()).data;
}

function captureState(detail) {
  const offers = detail?.offers ?? {};
  const asset = detail?.cta?.asset;
  if (offers.asset && asset) return `asset waitlist \`${asset}\``;
  if (offers.brief) return "brief signup";
  if (asset) return `asset configured, offer off \`${asset}\``;
  return "none";
}

function statusLabel(item) {
  if (item.offer_type === "brief") return "brief, live capture";
  if (item.status === "waitlist") return "asset, waitlist";
  return "asset, planned";
}

export async function buildBlock() {
  const catalog = loadCatalog();
  const channels = await fetchChannels();
  const known = new Set(Object.keys(catalog.channels));
  const live = new Set(channels.map((channel) => channel.slug));
  const missing = [...live].filter((slug) => !known.has(slug)).sort();
  const orphaned = [...known].filter((slug) => !live.has(slug)).sort();
  if (missing.length) throw new Error(`offer inventory: catalog missing channel(s): ${missing.join(", ")}`);
  if (orphaned.length) throw new Error(`offer inventory: catalog has unknown channel(s): ${orphaned.join(", ")}`);

  const rows = [];
  let assets = 0;
  let briefs = 0;
  let waitlists = 0;
  let planned = 0;
  let captureAssets = 0;
  let captureBriefs = 0;

  for (const channel of channels) {
    const item = catalog.channels[channel.slug];
    const guidePath = resolve(BIZ, "strategy", item.guide);
    if (!existsSync(guidePath)) {
      throw new Error(`offer inventory: guide missing for ${channel.slug}: ${item.guide}`);
    }
    const detail = await fetchChannel(channel.slug);
    const capture = captureState(detail);
    if (capture.startsWith("asset waitlist")) captureAssets += 1;
    if (capture === "brief signup") captureBriefs += 1;
    if (item.offer_type === "asset") {
      assets += 1;
      if (item.status === "waitlist") waitlists += 1;
      if (item.status === "planned") planned += 1;
    } else {
      briefs += 1;
    }
    rows.push(
      `| ${rows.length + 1} | ${cell(channel.name)} | \`${channel.slug}\` | ${cell(item.offer_name)} | ${item.offer_type} | ${statusLabel(item)} | ${cell(item.cadence)} | ${cell(item.scope)} | ${cell(item.ai_scope.split(";")[0])} | ${capture} | [guide](${item.guide}) |`,
    );
  }

  const tiers = [0, 1, 2, 3].map((tier) => {
    const names = Object.entries(catalog.channels)
      .filter(([, item]) => item.tier === tier)
      .map(([slug, item]) => `\`${slug}\` (${item.offer_type}, ${item.status})`);
    return `| T${tier} | ${names.join(" · ") || "-"} |`;
  });

  return [
    BEGIN,
    `**API:** ${API_URL} · **Channels:** ${channels.length} · **Plan:** ${assets} reference (${waitlists} waitlist, ${planned} planned), ${briefs} brief · **Live capture:** ${captureAssets} asset waitlist, ${captureBriefs} brief signup · **Published issues:** 0`,
    "**Reading rule:** the catalog is the recommendation; the API column is what the site captures today. A row with `planned` is not a promise to readers.",
    "",
    "| # | Channel | Slug | Free offer (recommended) | Type | Status | Cadence | Scope | AI draft | Capture today | Guide |",
    "|---|---|---|---|---|---|---|---|---|---|---|",
    ...rows,
    "",
    "**Offer rules:** one secondary offer per channel · asset needs a citable source and a named reviewer · every row carries a URL and an issue date · no autopublish · EN is reviewed before ES is translated · no offer promises advice, a rate, a return, or an outcome.",
    "",
    "### Rollout",
    "| Tier | Channels |",
    "|---|---|",
    ...tiers,
    "",
    `**Live delivery:** 0 published issues. Every current offer is capture-only; see the analysis at \`strategy/20261106-ai-offer-system.md\`.`,
    END,
  ].join("\n");
}


function template(block) {
  return `# Offer inventory

**What this is:** the canonical list of free offers per channel: the recommended deliverable, its type and cadence, what the site captures today, and the generation guide.
**Status:** Generated ${today} · **Needs:** re-generate after any offer, channel, or catalog change; a stale file fails the local check.
**Source:** \`GET /v1/industries\` + \`GET /v1/industries/{slug}\` joined with \`strategy/offers/catalog.json\`. The live capture column is evidence; the recommendation column is a plan.

## Inventory

${block}

## Drafts

This table shows the public capture state and the offer plan. It does not show
generated drafts. Legal and cybersecurity drafts are stored in offer_issues;
inspect them with ./bin/offers.sh list and render one with
./bin/offers.sh show <id> --markdown. A draft is not published and has no
reviewer signature.

## How to keep it updated

1. Change the offer plan in \`strategy/offers/catalog.json\`, or change a channel's offers in the admin console.
2. Run \`.work.biz/scripts/offers.sh --write\` with the stack up.
3. Run \`.work.biz/scripts/offers.sh --check\`; it fails when this file is stale or a channel is missing from the catalog.
4. Commit the catalog, the guide, and the regenerated inventory together.

The generated block is the only machine-owned part. Edit the prose outside the markers by hand.

## Next action

\`.work.biz/scripts/offers.sh --write\` after any offer change.
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
      console.log(`offer inventory: wrote ${DOC}`);
      return;
    }
    const existing = extractBlock(current);
    if (!existing) {
      throw new Error(`offer inventory: markers missing in ${DOC}; restore the generated block or delete the file`);
    }
    writeFileSync(DOC, current.replace(existing, block));
    console.log(`offer inventory: updated ${DOC}`);
    return;
  }

  if (mode === "--check") {
    let current = "";
    try {
      current = readFileSync(DOC, "utf8");
    } catch {
      throw new Error(`offer inventory: ${DOC} is missing; run .work.biz/scripts/offers.sh --write`);
    }
    const existing = extractBlock(current);
    if (!existing) throw new Error(`offer inventory: generated block missing in ${DOC}`);
    if (existing !== block) {
      throw new Error(`offer inventory: ${DOC} is stale; run .work.biz/scripts/offers.sh --write`);
    }
    console.log("offer inventory: ok");
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
