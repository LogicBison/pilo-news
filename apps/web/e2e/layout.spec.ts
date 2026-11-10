import { expect, test } from "@playwright/test";

const CHANNELS = [
  "legal",
  "financial",
  "behavioral-health",
  "education",
  "logistics",
  "cybersecurity",
  "stem-cell",
  "manufacturing",
  "energy",
  "retail",
  "digital-technology",
  "health-medicine",
];

async function hydrated(page: import("@playwright/test").Page, path: string) {
  await page.goto(path);
  await page.waitForSelector('html[data-hydrated="true"]');
}

async function expectNoHorizontalOverflow(page: import("@playwright/test").Page) {
  const { scrollWidth, innerWidth } = await page.evaluate(() => ({
    scrollWidth: document.documentElement.scrollWidth,
    innerWidth: window.innerWidth,
  }));
  expect(scrollWidth, "horizontal overflow").toBeLessThanOrEqual(innerWidth + 1);
}

for (const slug of CHANNELS) {
  test.describe(`${slug} layout`, () => {
    test("coverage columns are balanced", async ({ page }) => {
      await page.setViewportSize({ width: 1280, height: 900 });
      await hydrated(page, `/${slug}`);
      await expectNoHorizontalOverflow(page);

      const columns = await page.locator(".sn-columns > article").evaluateAll((articles) => {
        const groups = new Map<number, { top: number; bottom: number }>();
        for (const article of articles) {
          const rect = article.getBoundingClientRect();
          const key = Math.round(rect.x);
          const group = groups.get(key) ?? { top: rect.top, bottom: rect.bottom };
          group.top = Math.min(group.top, rect.top);
          group.bottom = Math.max(group.bottom, rect.bottom);
          groups.set(key, group);
        }
        return [...groups.values()].sort((a, b) => a.top - b.top);
      });

      const heights = columns.map((column) => column.bottom - column.top);
      if (heights.length < 2) return; // single-column rhythm: no column imbalance
      const spread = Math.max(...heights) - Math.min(...heights);
      expect(spread, `column height spread ${Math.round(spread)}px`).toBeLessThanOrEqual(260);
    });


    test("masthead emblem is visible", async ({ page }) => {
      await page.setViewportSize({ width: 1280, height: 900 });
      await hydrated(page, `/${slug}`);
      const emblem = page.locator(".sn-brandmark svg").first();
      await expect(emblem).toBeVisible();
      const box = await emblem.boundingBox();
      expect(box, "emblem has a box").not.toBeNull();
      expect(box?.width ?? 0).toBeGreaterThan(12);
    });

    test("marketing surfaces are square", async ({ page }) => {
      await page.setViewportSize({ width: 1280, height: 900 });
      await hydrated(page, `/${slug}`);
      const surfaces = await page.evaluate(() => {
        const selectors = [
          ".sn-hero-card",
          ".sn-scene",
          ".sn-proof-band",
          ".sn-convert",
          ".sn-story",
          ".sn-action",
          ".sn-card",
        ];
        return selectors.flatMap((selector) =>
          Array.from(document.querySelectorAll(selector)).map((element) => ({
            selector,
            radius: getComputedStyle(element).borderRadius,
          })),
        );
      });
      for (const surface of surfaces) {
        expect(surface.radius, `${surface.selector} must be square`).toBe("0px");
      }

      const motif = await page
        .locator(".sn-hero-card")
        .first()
        .evaluate((element) => getComputedStyle(element, "::after").display);
      expect(motif, "hero motif overlay removed").toBe("none");
    });
    test("compact CTA stays inside its column on search", async ({ page }) => {
      await page.setViewportSize({ width: 1280, height: 900 });
      await hydrated(page, `/${slug}/search`);
      await expectNoHorizontalOverflow(page);
      expect(await page.locator("main .sn-action").count()).toBe(0);
    });

    test("hero action panel stays inside the viewport", async ({ page }) => {
      await page.setViewportSize({ width: 1280, height: 900 });
      await hydrated(page, `/${slug}`);
      const box = await page.locator(".sn-hero .sn-action").first().boundingBox();
      expect(box, "hero action panel exists").not.toBeNull();
      if (!box) return;
      expect(box.x).toBeGreaterThanOrEqual(-1);
      expect(box.x + box.width).toBeLessThanOrEqual(1281);
    });
  });
}

test.describe("contact and about layout", () => {
  const paths = ["/legal/contact", "/es/legal/contact", "/legal/about", "/es/legal/about"];
  for (const path of paths) {
    test(`${path} has no horizontal overflow`, async ({ page }) => {
      for (const width of [1280, 390]) {
        await page.setViewportSize({ width, height: 900 });
        await hydrated(page, path);
        await expectNoHorizontalOverflow(page);
      }
    });
  }
});
