import { test, expect } from "@playwright/test";
import { createPresentation, runStepAndWaitForCompletion } from "./utils";

test.setTimeout(180000);

test.describe("PPTX Preview", () => {
  test("pptx step shows slide images", async ({ page }) => {
    const name = `PPTX Preview ${Date.now()}`;
    const topic = "Offline pptx topic";

    await createPresentation(page, name, topic);
    await runStepAndWaitForCompletion(page, "slides");
    await runStepAndWaitForCompletion(page, "pptx", 120000);

    // Navigate to PPTX step
    const stepButton = page.getByTestId("step-nav-pptx");
    await stepButton.click();

    // Wait for first PPTX slide thumbnail
    const firstThumb = page.getByTestId("pptx-thumb-0");
    await firstThumb.waitFor({ timeout: 10000 });

    // Click first thumbnail to show slide
    await firstThumb.click();

    // Expect preview image to be visible
    await expect(page.getByTestId("pptx-preview-image")).toBeVisible({ timeout: 10000 });
  });
});
