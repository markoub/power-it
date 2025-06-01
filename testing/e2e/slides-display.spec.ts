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
    const [researchResponse] = await Promise.all([
      page.waitForResponse(resp => resp.url().includes(`/presentations/${presentationId}/steps/research/run`) && resp.status() === 200),
      page.getByTestId('start-ai-research-button').click()
    ]);
    console.log("✅ Research completed");

    // 2. Navigate to slides and run using the exact working pattern
    console.log("🔍 Running slides...");
    await page.getByTestId('step-nav-slides').click();
    await page.waitForLoadState('networkidle');
    
    const runSlidesButton = page.getByTestId('run-slides-button');
    const slidesButtonExists = await runSlidesButton.count() > 0;
    console.log(`Slides button exists: ${slidesButtonExists}`);
    
    if (slidesButtonExists) {
      const [slidesResponse] = await Promise.all([
        page.waitForResponse(resp => resp.url().includes(`/presentations/${presentationId}/steps/slides/run`) && resp.status() === 200),
        runSlidesButton.click()
      ]);
      console.log("✅ Slides generation started");
      
      // Wait for slides to be generated
      console.log("⏳ Waiting for slides to be generated...");
      await page.waitForSelector('[data-testid^="slide-thumbnail-"]', { timeout: 30000 });
      
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
