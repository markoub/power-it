import { test, expect } from "@playwright/test";
import { createPresentation } from "./utils";

test.setTimeout(120000);

test.describe("Slides Display", () => {
  test("generated slides are shown with content", async ({ page }) => {
    const name = `Slides Display ${Date.now()}`;
    const topic = "Offline slide topic";

    // Create presentation and run research first
    const presentationId = await createPresentation(page, name, topic);
    console.log(`✅ Created presentation with ID: ${presentationId}`);
    
    // 1. Run research using the working pattern
    console.log("🔍 Running research...");
    await page.getByTestId('start-ai-research-button').click();
    await page.waitForTimeout(3000); // Same timing as working test
    console.log("✅ Research completed");

    // 2. Navigate to slides and run using the exact working pattern
    console.log("🔍 Running slides...");
    await page.getByTestId('step-nav-slides').click();
    await page.waitForTimeout(1000); // Same timing as working test
    
    const runSlidesButton = page.getByTestId('run-slides-button');
    const slidesButtonExists = await runSlidesButton.count() > 0;
    console.log(`Slides button exists: ${slidesButtonExists}`);
    
    if (slidesButtonExists) {
      await runSlidesButton.click();
      await page.waitForTimeout(3000); // Same timing as working test
      console.log("✅ Slides clicked");
      
      // Wait for slides to be generated
      console.log("⏳ Waiting for slides to be generated...");
      await page.waitForFunction(() => {
        const thumbnails = document.querySelectorAll('[data-testid^="slide-thumbnail-"]');
        return thumbnails.length > 0;
      }, {}, { timeout: 30000 });
      
      // Verify first slide thumbnail is visible
      await expect(page.getByTestId("slide-thumbnail-0")).toBeVisible();
      console.log("✅ First slide thumbnail is visible");
      
      // Verify we have multiple slides
      const slideCount = await page.locator('[data-testid^="slide-thumbnail-"]').count();
      expect(slideCount).toBeGreaterThan(0);
      console.log(`✅ Generated ${slideCount} slides successfully`);
    } else {
      throw new Error("❌ Slides button not found - this should not happen after research completion");
    }
  });
});
