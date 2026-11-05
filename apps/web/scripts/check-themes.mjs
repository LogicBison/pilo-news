const API_BASE = process.env.API_INTERNAL_URL ?? "http://api:8080";

function luminance(hex) {
  const value = hex.replace("#", "");
  if (value.length !== 6) return 0;
  const channels = [0, 2, 4].map((index) => {
    const channel = parseInt(value.slice(index, index + 2), 16) / 255;
    return channel <= 0.03928 ? channel / 12.92 : ((channel + 0.055) / 1.055) ** 2.4;
  });
  return 0.2126 * channels[0] + 0.7152 * channels[1] + 0.0722 * channels[2];
}

function ratio(foreground, background) {
  const first = luminance(foreground);
  const second = luminance(background);
  return (Math.max(first, second) + 0.05) / (Math.min(first, second) + 0.05);
}

const response = await fetch(`${API_BASE.replace(/\/$/, "")}/v1/industries`);
if (!response.ok) {
  console.error(`theme check could not reach the API (${response.status})`);
  process.exit(1);
}
const payload = await response.json();
const failures = [];

for (const summary of payload.data) {
  const detailResponse = await fetch(
    `${API_BASE.replace(/\/$/, "")}/v1/industries/${summary.slug}?locale=en`,
  );
  if (!detailResponse.ok) {
    failures.push(`${summary.slug}: detail fetch failed`);
    continue;
  }
  const detail = (await detailResponse.json()).data;
  const theme = detail.theme;
  const checks = [
    ["text", theme.text, theme.bg, 4.5],
    ["muted", theme.muted, theme.bg, 4.5],
    ["text on surface", theme.text, theme.surface, 4.5],
    ["white on primary", "#ffffff", theme.primary, 4.5],
    ["accent", theme.accent, theme.bg, 3.0],
  ];
  for (const [label, fg, bg, minimum] of checks) {
    const value = ratio(fg, bg);
    if (value < minimum) {
      failures.push(`${summary.slug}: ${label} contrast ${value.toFixed(2)} < ${minimum}`);
    }
  }
  if (!["editorial", "professional", "academic"].includes(theme.layout)) {
    failures.push(`${summary.slug}: unknown layout ${theme.layout}`);
  }
}

if (failures.length) {
  console.error(failures.join("\n"));
  process.exit(1);
}
console.log(`themes ok: ${payload.data.length} channels pass contrast checks`);
