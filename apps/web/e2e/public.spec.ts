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
  await form.getByLabel("What do you need?").fill("A compliance question.");
  await form.getByRole("button", { name: /send request/i }).click();
  await expect(page).toHaveURL(/\/legal$/);
  expect(page.url()).not.toContain("reader@example.com");
});

test("contact form shows success without navigating", async ({ page }) => {
  await page.route("**/api/proxy/v1/contact", async (route) => {
    await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ id: "test" }) });
  });
  await page.goto("/legal/contact");
  await page.waitForSelector('html[data-hydrated="true"]');
  await page.getByLabel("Name").fill("Test Reader");
  await page.getByLabel("Email").fill("reader@example.com");
  await page.getByLabel("Message").fill("This is a test correction request.");
  await page.getByRole("button", { name: /send message/i }).click();
  await expect(page.getByRole("status")).toContainText(/message received/i);
});
