import AxeBuilder from "@axe-core/playwright";
import { expect, test } from "@playwright/test";

const pages = [
  // The apex site (lobby + services + network legal pages).
  "/",
  "/es",
  "/services",
  "/es/services",
  "/privacy",
  "/terms",
  "/legal",
  "/legal/contact",
  "/es/legal/contact",
  "/legal/about",
  "/es/legal/about",
  "/en/admin",
  "/legal/search",
  "/es/legal/search",
  "/legal/privacy",
  "/legal/terms",
  "/es/legal/terms",
  "/legal/briefs",
  "/legal/references",
  "/es/legal/references",
  "/financial",
  "/behavioral-health",
  "/education",
  "/logistics",
  "/cybersecurity",
  "/stem-cell",
  "/manufacturing",
  "/energy",
  "/retail",
  "/health-medicine",
];

for (const path of pages) {
  test(`no critical accessibility violations on ${path}`, async ({ page }) => {
    await page.goto(path);
    await page.waitForSelector('html[data-hydrated="true"]');
    const results = await new AxeBuilder({ page })
      .withTags(["wcag2a", "wcag2aa", "wcag21a", "wcag21aa"])
      .analyze();
    const critical = results.violations.filter((violation) =>
      ["critical", "serious"].includes(violation.impact ?? ""),
    );
    expect(critical, JSON.stringify(critical, null, 2)).toHaveLength(0);
  });
}

// M15-T4: the brand mark is decoration, so the brand link's accessible name
// comes from its aria-label alone — no second name from the emblem's alt text.
const apexBrandPages = ["/", "/es", "/services"];

for (const path of apexBrandPages) {
  test(`apex brand link has one name and a decorative mark on ${path}`, async ({ page }) => {
    await page.goto(path);
    await page.waitForSelector('html[data-hydrated="true"]');

    const brand = page.locator("a.lb-brand");
    await expect(brand).toHaveCount(1);
    const label = await brand.getAttribute("aria-label");
    expect(label?.trim(), "brand link must carry an aria-label").toBeTruthy();

    const emblem = brand.locator("img.lb-brand-emblem");
    await expect(emblem).toHaveCount(1);
    await expect(emblem).toHaveAttribute("alt", "");
    await expect(emblem).toHaveAttribute("aria-hidden", "true");
    expect(
      await emblem.evaluate((img: HTMLImageElement) => img.naturalWidth),
      "brand emblem must load",
    ).toBeGreaterThan(0);

    // No second heading landmark in the footer beside the brand.
    await expect(page.locator("footer h1")).toHaveCount(0);
  });
}
