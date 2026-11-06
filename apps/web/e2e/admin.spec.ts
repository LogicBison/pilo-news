import { expect, test } from "@playwright/test";

const password = process.env.E2E_ADMIN_PASSWORD;
const email = process.env.ADMIN_EMAIL ?? "admin@example.com";

test("admin console requires a session", async ({ page }) => {
  await page.goto("/en/admin");
  await expect(page.getByRole("heading", { name: /sign in/i })).toBeVisible();
});

test("admin sign-in form starts empty", async ({ page }) => {
  await page.goto("/en/admin");
  await expect(page.getByLabel("Email")).toHaveValue("");
  await expect(page.getByLabel("Password")).toHaveValue("");
});

test("admin can sign in and trigger a refresh", async ({ page }) => {
  test.skip(!password, "E2E_ADMIN_PASSWORD is not set");
  await page.goto("/en/admin");
  await page.getByLabel("Email").fill(email);
  await page.getByLabel("Password").fill(password ?? "");
  await page.getByRole("button", { name: /sign in/i }).click();
  await expect(page.getByRole("heading", { name: /editorial console/i })).toBeVisible();
  await page.getByRole("tab", { name: /refresh/i }).first().click();
  await expect(page.getByRole("button", { name: /trigger refresh/i })).toBeVisible();
});

test("admin can manage a channel's cadence and free offers", async ({ page }) => {
  test.skip(!password, "E2E_ADMIN_PASSWORD is not set");
  await page.goto("/en/admin");
  await page.getByLabel("Email").fill(email);
  await page.getByLabel("Password").fill(password ?? "");
  await page.getByRole("button", { name: /sign in/i }).click();
  await page.getByRole("tab", { name: /channels/i }).click();

  await expect(page.getByText(/deployment default: every/i)).toBeVisible();
  const row = page.getByRole("listitem").filter({ hasText: "Legal Services" }).first();
  await row.getByRole("button", { name: /manage/i }).click();

  await expect(row.getByLabel(/automatic fetching/i)).toBeVisible();
  await expect(row.getByRole("radio", { name: /use the deployment default/i })).toBeVisible();
  await expect(row.getByRole("checkbox", { name: /consultation request/i })).toBeVisible();
  await expect(row.getByRole("radio", { name: /weekly brief/i })).toBeVisible();
  await expect(row.getByRole("button", { name: /save channel settings/i })).toBeVisible();
});
