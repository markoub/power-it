import { test, expect } from "@playwright/test";
import { createPresentation, runStepAndWaitForCompletion } from "./utils";

test.setTimeout(120000);

test.describe("Slides Display", () => {
  test("generated slides are shown with content", async ({ page }) => {
    const name = `Slides Display ${Date.now()}`;
    const topic = "Offline slide topic";

    await createPresentation(page, name, topic);
    await runStepAndWaitForCompletion(page, "slides");

    // Wait for first thumbnail and open it
    const firstThumb = page.getByTestId("slide-thumbnail-0");
    await firstThumb.waitFor({ timeout: 10000 });
    await firstThumb.click();

    // Check that welcome subtitle text from offline fixture is visible
    await expect(page.getByTestId("slide-preview")).toContainText(
      "Transforming Industries Through Innovation",
    );
  });
});
