import { expect, test } from "@playwright/test";

test("channel home renders stories and a primary CTA", async ({ page }) => {
  await page.goto("/legal");
  await page.waitForSelector('html[data-hydrated="true"]');
  await expect(page.locator("h1")).toBeVisible();
  await expect(page.getByRole("link", { name: /request a consultation/i }).first()).toBeVisible();
  await expect(page.getByText(/news, not legal advice/i).first()).toBeVisible();
  await expect(page.locator("article").first()).toBeVisible();
});

test("locale switch persists and renders Spanish chrome", async ({ page, context }) => {
  await page.goto("/legal");
  await page.waitForSelector('html[data-hydrated="true"]');
  await page.getByRole("link", { name: "Español" }).click();
  await expect(page).toHaveURL(/\/es\/legal$/);
  await expect(page.locator("html")).toHaveAttribute("lang", "es");
  const cookie = (await context.cookies()).find((item) => item.name === "sn_locale");
  expect(cookie?.value).toBe("es");
});

test("article detail links out to the publisher", async ({ page }) => {
  await page.goto("/legal");
  await page.waitForSelector('html[data-hydrated="true"]');
  const firstStory = page.locator("article a").filter({ hasText: /./ }).first();
  await firstStory.click();
  await expect(page).toHaveURL(/\/legal\/article\//);
  await expect(page.locator("h1")).toBeVisible();
  await expect(page.getByRole("link", { name: /read the full story/i })).toBeVisible();
});

test("lead form requires consent and never echoes PII in the URL", async ({ page }) => {
  await page.route("**/api/proxy/v1/leads", async (route) => {
    const body = route.request().postDataJSON();
    expect(body.consent).toBe(false);
    await route.fulfill({ status: 422, contentType: "application/json", body: "{}" });
  });
  await page.goto("/legal");
  await page.waitForSelector('html[data-hydrated="true"]');
  const form = page.locator("#lead-form");
  await form.getByLabel("Name").fill("Test Reader");
  await form.getByLabel("Email").fill("reader@example.com");
  await form.getByLabel(/additional details/i).fill("A compliance question.");
  await form.getByRole("button", { name: /send request/i }).click();
  await expect(page).toHaveURL(/\/legal$/);
  expect(page.url()).not.toContain("reader@example.com");
});

test("contact form shows success without navigating", async ({ page }) => {
  let payload: Record<string, unknown> = {};
  await page.route("**/api/proxy/v1/contact", async (route) => {
    payload = (route.request().postDataJSON() ?? {}) as Record<string, unknown>;
    await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ id: "test" }) });
  });
  await page.goto("/legal/contact?utm_source=test");
  await page.waitForSelector('html[data-hydrated="true"]');
  await page.getByLabel("Name").fill("Test Reader");
  await page.getByLabel("Email").fill("reader@example.com");
  await page.getByLabel("Message").fill("This is a test correction request.");
  await page.getByRole("button", { name: /send message/i }).click();
  await expect(page.getByRole("status")).toContainText(/message received/i);
  expect(payload.source_page).toBe("/legal/contact");
  expect(payload.session_hash).toBeTruthy();
  expect((payload.utm as Record<string, string>).utm_source).toBe("test");
});

test("contact blocks an invalid email before any request", async ({ page }) => {
  let calls = 0;
  await page.route("**/api/proxy/v1/contact", async (route) => {
    calls += 1;
    await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ id: "x" }) });
  });
  await page.goto("/legal/contact");
  await page.waitForSelector('html[data-hydrated="true"]');
  await page.getByLabel("Name").fill("Test Reader");
  await page.getByLabel("Email").fill("not-an-email");
  await page.getByLabel("Message").fill("This is a test correction request.");
  await page.getByRole("button", { name: /send message/i }).click();
  await expect(page.getByText(/valid email/i)).toBeVisible();
  expect(calls).toBe(0);
});

test("contact failure keeps the entered values and offers the desk email", async ({ page }) => {
  await page.route("**/api/proxy/v1/contact", async (route) => {
    await route.fulfill({ status: 500, contentType: "application/json", body: JSON.stringify({ detail: "boom" }) });
  });
  await page.goto("/legal/contact");
  await page.waitForSelector('html[data-hydrated="true"]');
  await page.getByLabel("Name").fill("Test Reader");
  await page.getByLabel("Email").fill("reader@example.com");
  await page.getByLabel("Message").fill("This is a test correction request.");
  await page.getByRole("button", { name: /send message/i }).click();
  await expect(page.getByText(/could not be sent/i)).toBeVisible();
  await expect(page.getByLabel("Name")).toHaveValue("Test Reader");
});

test("about copy carries no stale retention number", async ({ page }) => {
  await page.goto("/legal/about");
  await expect(page.locator("main")).not.toContainText(/seven-day/i);
  await page.goto("/es/legal/about");
  await expect(page.locator("main")).not.toContainText(/siete días/i);
});

test("about suppresses the brief where the channel offers an asset", async ({ page }) => {
  await page.goto("/legal/about");
  await page.waitForSelector('html[data-hydrated="true"]');
  await expect(page.locator("#brief-signup")).toHaveCount(0);
  await page.goto("/education/about");
  await page.waitForSelector('html[data-hydrated="true"]');
  await expect(page.locator("#brief-signup")).toBeVisible();
});

test("channel RSS feed is valid and localized", async ({ request }) => {
  const en = await request.get("/legal/feed.xml");
  expect(en.status()).toBe(200);
  expect(en.headers()["content-type"]).toContain("application/rss+xml");
  const xml = await en.text();
  expect(xml).toContain("<rss");
  expect(xml).toContain("<language>en</language>");
  expect(xml).toContain("/legal/article/");
  expect((xml.match(/<item>/g) ?? []).length).toBeGreaterThan(5);

  const es = await request.get("/es/legal/feed.xml");
  expect(es.status()).toBe(200);
  expect(await es.text()).toContain("<language>es</language>");

  const unknown = await request.get("/nope/feed.xml");
  expect(unknown.status()).toBe(404);
});

test("channel pages advertise their feed", async ({ page }) => {
  await page.goto("/legal");
  const href = await page
    .locator('link[rel="alternate"][type="application/rss+xml"]')
    .getAttribute("href");
  expect(href).toBe("/legal/feed.xml");
  await expect(page.getByRole("link", { name: "RSS" })).toHaveAttribute(
    "href",
    "/legal/feed.xml",
  );
});

test("gated asset cards follow the channel, not a hardcoded slug", async ({ page }) => {
  await page.goto("/cybersecurity");
  await page.waitForSelector('html[data-hydrated="true"]');
  await expect(page.getByRole("heading", { name: /known-exploited vulnerabilities, weekly/i })).toBeVisible();

  await page.locator("article a").filter({ hasText: /./ }).first().click();
  await expect(page).toHaveURL(/\/cybersecurity\/article\//);
  await expect(page.getByRole("heading", { name: /known-exploited vulnerabilities, weekly/i })).toBeVisible();

  await page.goto("/es/cybersecurity");
  await page.waitForSelector('html[data-hydrated="true"]');
  await expect(page.getByRole("heading", { name: /vulnerabilidades explotadas, semanal/i })).toBeVisible();

  await page.goto("/legal");
  await page.waitForSelector('html[data-hydrated="true"]');
  await expect(page.getByRole("heading", { name: /legal regulatory calendar/i })).toBeVisible();
  await expect(page.locator("#brief-signup")).toHaveCount(0);

  await page.goto("/education");
  await page.waitForSelector('html[data-hydrated="true"]');
  await expect(page.getByRole("heading", { name: /legal regulatory calendar/i })).toHaveCount(0);
  await expect(page.getByRole("heading", { name: /known-exploited vulnerabilities/i })).toHaveCount(0);
  await expect(page.locator("#brief-signup")).toBeVisible();
});

test("a gated asset replaces the brief rung on the channels that offer one", async ({ page }) => {
  await page.goto("/cybersecurity");
  await page.waitForSelector('html[data-hydrated="true"]');
  await expect(page.locator("#brief-signup")).toHaveCount(0);
  await expect(page.getByRole("heading", { name: /known-exploited vulnerabilities, weekly/i })).toBeVisible();

  await page.goto("/financial");
  await page.waitForSelector('html[data-hydrated="true"]');
  await expect(page.locator("#brief-signup")).toBeVisible();
  await expect(page.getByRole("heading", { name: /known-exploited vulnerabilities/i })).toHaveCount(0);
});

test("the digital-technology channel renders with its own skin and no asset card", async ({ page }) => {
  await page.goto("/digital-technology");
  await page.waitForSelector('html[data-hydrated="true"]');
  await expect(page).toHaveURL(/\/digital-technology$/);
  await expect(page.locator('[data-skin="datacenter"]').first()).toBeVisible();
  await expect(page.locator("h1")).toBeVisible();
  await expect(page.locator("#brief-signup")).toBeVisible();
  await expect(page.getByRole("heading", { name: /known-exploited vulnerabilities|legal regulatory calendar/i })).toHaveCount(0);
  await expect(page.getByText(/CC BY-SA 3\.0/).first()).toBeVisible();

  await page.goto("/es/digital-technology");
  await page.waitForSelector('html[data-hydrated="true"]');
  await expect(page.locator("html")).toHaveAttribute("lang", "es");
});
