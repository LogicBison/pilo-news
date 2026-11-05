import AxeBuilder from "@axe-core/playwright";
import { expect, test } from "@playwright/test";

const pages = ["/legal", "/legal/contact"];

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
