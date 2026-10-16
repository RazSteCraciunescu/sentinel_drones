import { expect, test } from "@playwright/test";

test("dashboard clearly states the simulation boundary", async ({ page }) => {
  await page.goto("/");

  await expect(page).toHaveTitle("Sentinel UAS Assurance Lab");
  await expect(page.getByText("SIMULATION ONLY")).toBeVisible();
  await expect(page.getByText("No radio, autopilot, or real aircraft connection")).toBeVisible();
});

test("observer can load the assurance view", async ({ page }) => {
  await page.goto("/");
  await page.getByLabel("Local lab token").fill("observer-local-token");
  await page.getByRole("button", { name: "Load assurance view" }).click();

  await expect(page.getByRole("status")).toContainText("Loaded 3 simulated aircraft");
  await expect(page.locator("#service-status")).toHaveText("OK");
  await expect(page.locator("#fleet-total")).toHaveText("3");
  await expect(page.getByRole("cell", { name: "ALPHA-ONE" })).toBeVisible();
});

test("invalid token produces a visible error", async ({ page }) => {
  await page.goto("/");
  await page.getByLabel("Local lab token").fill("not-a-valid-token");
  await page.getByRole("button", { name: "Load assurance view" }).click();

  await expect(page.getByRole("status")).toContainText("Invalid X-Lab-Token");
  await expect(page.locator("#service-status")).toHaveText("ERROR");
});
