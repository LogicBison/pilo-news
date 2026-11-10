import { expect, test } from "@playwright/test";

/** Desks the lobby must show. Add a channel? Bump this and the inventory. */
const DESK_COUNT = 12;

/**
 * The apex site: the lobby directory and the services page. These assertions are
 * about the promises the page makes — every desk, no capture on the lobby,
 * one scope-call form — not about layout pixels (see layout.spec.ts).
 */

test("the lobby lists every desk and links each to its own host", async ({ page }) => {
  await page.goto("/");
  await page.waitForSelector('html[data-hydrated="true"]');

  // Always one h1: the hero, or the honest degraded state if the API did not
  // answer in time (the page must not ship an h1-less document).
  await expect(page.locator("h1")).toContainText(/know what changed|directory is unavailable/i);
  await expect(page.locator(".lb-plate")).toHaveCount(DESK_COUNT);

  const hrefs = await page.locator(".lb-plate").evaluateAll((nodes) =>
    nodes.map((node) => node.getAttribute("href") ?? ""),
  );
  for (const href of hrefs) {
    // Canonical form is the desk's own host; the path form is the fallback on a
    // deployment without a channel domain.
    expect(href).toMatch(/(https?:\/\/[a-z-]+\.localhost:\d+\/?$)|(\/[a-z-]+\/?$)/);
  }
  expect(new Set(hrefs).size).toBe(DESK_COUNT);
});

test("the board shows a cadence and a filed date for every desk", async ({ page }) => {
  await page.goto("/");
  await page.waitForSelector('html[data-hydrated="true"]');
  const rows = page.locator(".lb-board tbody tr");
  await expect(rows).toHaveCount(DESK_COUNT);
  await expect(rows.first()).toContainText(/every \d+ h/i);
  // Languages were deliberately dropped from the board (one value, once per desk).
  await expect(page.locator(".lb-board thead th")).toHaveCount(3);
  await expect(rows.first().locator("td").last()).not.toBeEmpty();
});

test("the lobby has one form: contact, and no reader capture", async ({ page }) => {
  // D-020 supersedes the no-capture clause of D-017: the apex carries a contact
  // form, but every free reader offer still lives on its desk.
  await page.goto("/");
  await page.waitForSelector('html[data-hydrated="true"]');
  await expect(page.locator("form")).toHaveCount(1);

  let body: Record<string, unknown> | null = null;
  await page.route("**/api/proxy/v1/contact", async (route) => {
    body = route.request().postDataJSON() as Record<string, unknown>;
    await route.fulfill({ status: 200, contentType: "application/json", body: "{}" });
  });

  await page.getByLabel(/^name$/i).fill("Grace Hopper");
  await page.getByLabel(/work email/i).fill("grace@example.com");
  await page.getByLabel(/what do you need/i).fill("Which desk covers grid interconnection?");
  await page.getByLabel(/i agree to be contacted/i).check();
  await page.getByRole("button", { name: /send message/i }).click();

  await expect(page.locator(".lb-status-ok")).toBeVisible();
  expect(body).not.toBeNull();
  expect(body).not.toHaveProperty("industry");
  expect(body).toMatchObject({ name: "Grace Hopper", locale: "en", source_page: "/" });
});

test("the Spanish lobby renders as Spanish and keeps the switch on-page", async ({ page }) => {
  await page.goto("/es");
  await page.waitForSelector('html[data-hydrated="true"]');
  await expect(page.locator("html")).toHaveAttribute("lang", "es");
  await expect(page.locator("h1")).toContainText(/sepa qué cambió/i);
  await expect(page.locator(".lb-plate")).toHaveCount(DESK_COUNT);
  await expect(page.locator('a[hreflang], .lb-lang a[aria-current="true"]').first()).toBeVisible();
});

test("the language switch keeps you on the same page", async ({ page }) => {
  await page.goto("/services");
  await page.waitForSelector('html[data-hydrated="true"]');
  await page.locator(".lb-lang a", { hasText: "ES" }).click();
  await expect(page).toHaveURL(/\/es\/services$/);
  await expect(page.locator("html")).toHaveAttribute("lang", "es");
});

test("the services page has one scope-call form and it validates before sending", async ({
  page,
}) => {
  await page.goto("/services");
  await page.waitForSelector('html[data-hydrated="true"]');
  await expect(page.locator("form")).toHaveCount(1);

  let attempted = false;
  await page.route("**/api/proxy/v1/contact", async (route) => {
    attempted = true;
    await route.fulfill({ status: 200, contentType: "application/json", body: "{}" });
  });

  await page.getByRole("button", { name: /send request/i }).click();
  await expect(page.locator(".lb-field-error").first()).toBeVisible();
  expect(attempted).toBe(false);
});

test("a service inquiry posts without an industry and reports success", async ({ page }) => {
  await page.goto("/services");
  await page.waitForSelector('html[data-hydrated="true"]');

  let body: Record<string, unknown> | null = null;
  await page.route("**/api/proxy/v1/contact", async (route) => {
    body = route.request().postDataJSON() as Record<string, unknown>;
    await route.fulfill({ status: 200, contentType: "application/json", body: "{}" });
  });

  await page.getByLabel(/^name$/i).fill("Ada Lovelace");
  await page.getByLabel(/work email/i).fill("ada@example.com");
  await page
    .getByLabel(/what do you need/i)
    .fill("We need a weekly desk for our association, bilingual, starting in January.");
  await page.getByLabel(/i agree to be contacted/i).check();
  await page.getByRole("button", { name: /send request/i }).click();

  await expect(page.locator(".lb-status-ok")).toBeVisible();
  expect(body).not.toBeNull();
  expect(body).toMatchObject({ name: "Ada Lovelace", email: "ada@example.com", locale: "en" });
  expect(body).not.toHaveProperty("industry");
});

test("the legal pages exist at the apex", async ({ page }) => {
  for (const path of ["/privacy", "/terms", "/es/privacy", "/es/terms"]) {
    const response = await page.goto(path);
    expect(response?.status(), path).toBe(200);
    await expect(page.locator("h1")).toBeVisible();
  }
});

test("the sitemap lists the apex pages", async ({ request }) => {
  const response = await request.get("/sitemap.xml");
  expect(response.status()).toBe(200);
  const xml = await response.text();
  for (const path of ["/services", "/privacy", "/terms"]) {
    expect(xml).toContain(path);
  }
});

test("no message placeholder leaks onto any apex page", async ({ page }) => {
  // A key called without its values renders the literal `{desks}`.
  for (const path of ["/", "/es", "/services", "/es/services", "/privacy", "/terms"]) {
    await page.goto(path);
    await page.waitForSelector('html[data-hydrated="true"]');
    const html = await page.content();
    const leaked = [...new Set(html.match(/\{[a-zA-Z][a-zA-Z0-9]*\}/g) ?? [])];
    expect(leaked, `${path} leaks ${leaked.join(", ")}`).toHaveLength(0);
  }
});

test("the spine and masthead reach the lobby sections from every page", async ({ page }) => {
  // On /services the sections live on the lobby, so the links must be absolute
  // to the lobby root — a bare `#directory` does nothing here.
  await page.goto("/services");
  await page.waitForSelector('html[data-hydrated="true"]');
  await page.locator(".lb-rail a", { hasText: /directory/i }).click();
  await expect(page).toHaveURL(/\/#directory$/);
  await expect(page.locator("#directory")).toBeVisible();

  await page.goto("/services");
  await page.waitForSelector('html[data-hydrated="true"]');
  await page.locator(".lb-nav a", { hasText: /^desks$/i }).click();
  await expect(page.locator("#directory")).toBeVisible();

  await page.goto("/privacy");
  await page.waitForSelector('html[data-hydrated="true"]');
  await page.locator(".lb-rail a", { hasText: /questions/i }).click();
  await expect(page.locator("#questions")).toBeVisible();
});

test("the primary CTA is readable and the form fields are findable", async ({ page }) => {
  await page.goto("/");
  await page.waitForSelector('html[data-hydrated="true"]');
  const cta = page.locator(".lb-hero .lb-btn").first();
  const colours = await cta.evaluate((el) => {
    const cs = getComputedStyle(el);
    return { color: cs.color, background: cs.backgroundColor };
  });
  expect(colours.color).not.toBe(colours.background);

  await page.goto("/services");
  await page.waitForSelector('html[data-hydrated="true"]');
  const field = await page.locator("#lb-email").evaluate((el) => {
    const cs = getComputedStyle(el);
    const card = getComputedStyle(el.closest("form") as HTMLElement);
    return { field: cs.backgroundColor, card: card.backgroundColor, border: cs.borderTopWidth };
  });
  // A field that is the same colour as its card is not a field.
  expect(field.field).not.toBe(field.card);
  expect(field.border).toBe("1px");
});

/**
 * The apex has one layout that must survive every width: the masthead wraps,
 * and the desk board either keeps its four columns or folds into labelled rows.
 * A board cell that ends outside the board is a fact nobody can read.
 */
test("the masthead and the desk board fit the viewport at every width", async ({ page }) => {
  for (const width of [1440, 1309, 1024, 768, 430, 390]) {
    await page.setViewportSize({ width, height: 900 });
    await page.goto("/");
    await page.waitForSelector('html[data-hydrated="true"]');
    // The board only renders when /v1/desks answers; a cold API is not a layout bug.
    await page.waitForSelector(".lb-board", { timeout: 20_000 });

    const pageOverflow = await page.evaluate(
      () => document.documentElement.scrollWidth - document.documentElement.clientWidth,
    );
    expect(pageOverflow, `document overflows at ${width}px`).toBeLessThanOrEqual(1);

    const board = await page.evaluate(() => {
      const box = document.querySelector(".lb-board")?.getBoundingClientRect();
      if (!box) return null;
      const cells = [...document.querySelectorAll(".lb-board tbody td")];
      const clipped = cells.filter((cell) => {
        const rect = cell.getBoundingClientRect();
        return rect.right > box.right + 1 || rect.left < box.left - 1;
      }).length;
      const dates = [...document.querySelectorAll(".lb-board tbody td:last-child")].map(
        (cell) => cell.textContent?.trim() ?? "",
      );
      return { cells: cells.length, clipped, dates };
    });

    expect(board, `no board at ${width}px`).not.toBeNull();
    expect(board!.cells, `board lost cells at ${width}px`).toBe(DESK_COUNT * 3);
    expect(board!.clipped, `board cells clipped at ${width}px`).toBe(0);
    // Every desk keeps a filed date; an empty cell would mean the fold dropped it.
    expect(board!.dates.filter((date) => date.length > 0), `dates missing at ${width}px`).toHaveLength(DESK_COUNT);
  }
});
