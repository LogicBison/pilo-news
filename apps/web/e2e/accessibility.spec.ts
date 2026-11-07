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
