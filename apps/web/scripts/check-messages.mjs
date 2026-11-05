import { readFileSync } from "node:fs";

const locales = ["en", "es"];
const catalogs = Object.fromEntries(
  locales.map((locale) => [
    locale,
    JSON.parse(readFileSync(new URL(`../src/messages/${locale}.json`, import.meta.url), "utf8")),
  ]),
);

function flatten(value, prefix = "", out = new Set()) {
  if (value && typeof value === "object" && !Array.isArray(value)) {
    for (const [key, child] of Object.entries(value)) {
      flatten(child, prefix ? `${prefix}.${key}` : key, out);
    }
  } else {
    out.add(prefix);
  }
  return out;
}

const base = flatten(catalogs.en);
const other = flatten(catalogs.es);
const missing = [...base].filter((key) => !other.has(key));
const extra = [...other].filter((key) => !base.has(key));

if (missing.length || extra.length) {
  console.error("Locale catalogs are out of sync.");
  if (missing.length) console.error("missing in es:", missing.join(", "));
  if (extra.length) console.error("extra in es:", extra.join(", "));
  process.exit(1);
}

console.log(`catalogs ok: ${base.size} keys in en and es`);
