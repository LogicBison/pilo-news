import AxeBuilder from "@axe-core/playwright";
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

test("admin can inspect generated offer drafts", async ({ page }) => {
  test.skip(!password, "E2E_ADMIN_PASSWORD is not set");
  await page.goto("/en/admin");
  await page.getByLabel("Email").fill(email);
  await page.getByLabel("Password").fill(password ?? "");
  await page.getByRole("button", { name: /sign in/i }).click();
  await page.getByRole("tab", { name: /offers/i }).click();

  await expect(page.getByText(/generated drafts from public sources/i)).toBeVisible();
  const row = page.getByRole("row").filter({ hasText: "legal-regulatory-calendar" }).first();
  await expect(row).toContainText(/draft/i);
  await row.getByRole("button", { name: /^view$/i }).click();
  await expect(page.getByRole("link", { name: /securities and exchange commission/i }).first()).toBeVisible();
  await row.getByRole("button", { name: /^publish$/i }).click();
  await expect(page.getByLabel(/reviewer name/i)).toBeVisible();
  const results = await new AxeBuilder({ page })
    .withTags(["wcag2a", "wcag2aa", "wcag21a", "wcag21aa"])
    .analyze();
  expect(
    results.violations.filter((violation) =>
      ["critical", "serious"].includes(violation.impact ?? ""),
    ),
  ).toHaveLength(0);
});

test("admin can publish and unpublish a reference issue", async ({ page }) => {
  test.skip(!password, "E2E_ADMIN_PASSWORD is not set");
  await page.goto("/en/admin");
  await page.getByLabel("Email").fill(email);
  await page.getByLabel("Password").fill(password ?? "");
  await page.getByRole("button", { name: /sign in/i }).click();
  await expect(page.getByRole("heading", { name: /editorial console/i })).toBeVisible();

  const listed = await page.request.get("/api/proxy/v1/admin/offers?industry=legal");
  expect(listed.ok()).toBeTruthy();
  const issues = ((await listed.json()) as { data: { id: string; status: string; issue_date: string }[] })
    .data;
  const draft = issues.find((issue) => issue.status === "draft");
  test.skip(!draft, "no legal draft available");
  if (!draft) return;

  const csrf = (await page.context().cookies()).find((cookie) => cookie.name === "sn_csrf")?.value;
  const headers = { "x-csrf-token": csrf ?? "" };
  try {
    const published = await page.request.post(`/api/proxy/v1/admin/offers/${draft.id}/publish`, {
      headers,
      data: { reviewer: "E2E Reviewer" },
    });
    expect(published.ok()).toBeTruthy();

    await page.goto("/legal/references");
    await expect(page.getByRole("heading", { name: /reference issues/i })).toBeVisible();
    await expect(page.getByRole("link", { name: /US Regulatory Calendar/i }).first()).toBeVisible();

    await page.goto(`/legal/references/${draft.issue_date}`);
    await expect(page.getByRole("heading", { name: /US Regulatory Calendar/i })).toBeVisible();
    await expect(page.getByText(/E2E Reviewer/)).toBeVisible();
    await expect(
      page.getByRole("link", { name: /Securities and Exchange Commission/i }).first(),
    ).toBeVisible();

    await page.goto("/legal");
    await expect(page.getByRole("link", { name: /read the latest issue/i }).first()).toBeVisible();

    const results = await new AxeBuilder({ page })
      .withTags(["wcag2a", "wcag2aa", "wcag21a", "wcag21aa"])
      .analyze();
    expect(
      results.violations.filter((violation) =>
        ["critical", "serious"].includes(violation.impact ?? ""),
      ),
    ).toHaveLength(0);
  } finally {
    await page.request.post(`/api/proxy/v1/admin/offers/${draft.id}/unpublish`, { headers });
  }
});
