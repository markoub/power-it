import { test, expect } from "@playwright/test";
import { navigateToTestPresentation, waitForStepCompletion, getApiUrl } from "./utils";
import { TEST_CATEGORIES } from "../test-config";

test.setTimeout(15000); // 15s timeout for offline mode

test.describe("Slides Display", () => {
  test("generated slides are shown with content using pre-seeded data", async ({ page }) => {
    // Use a presentation that already has research completed
    const presentation = await navigateToTestPresentation(page, TEST_CATEGORIES.RESEARCH_COMPLETE, 0);
    
    console.log(`📋 Testing with: ${presentation.name}`);
    console.log(`📚 Topic: ${presentation.topic}`);
    console.log(`🔗 Using API: ${getApiUrl()}`);

    // Navigate to slides step by clicking the step circle (not Continue button)
    console.log("🔍 Navigating to slides step...");
    await page.getByTestId('step-nav-slides').click();
    await page.waitForLoadState('networkidle');
    
    // Verify we're on the slides step page - check for either run or rerun button
    const runButton = page.getByTestId('run-slides-button');
    const rerunButton = page.getByTestId('rerun-slides-button');
    
    // Wait for either button to be visible
    await Promise.race([
      runButton.waitFor({ state: 'visible', timeout: 5000 }).catch(() => null),
      rerunButton.waitFor({ state: 'visible', timeout: 5000 }).catch(() => null),
    ]);
    
    console.log("✅ Slides step page loaded");
    
    // Run slides generation - click whichever button is visible
    console.log("🔍 Running slides generation...");
    let button;
    if (await runButton.isVisible()) {
      button = runButton;
      console.log("  Using 'Run Slides' button");
    } else if (await rerunButton.isVisible()) {
      button = rerunButton;
      console.log("  Using 'Rerun Slides' button");
    } else {
      throw new Error("Neither run nor rerun button found");
    }
    
    await expect(button).toBeEnabled();
    await button.click();
    console.log("✅ Slides generation started");
    
    // Wait for slides to be generated - in offline mode this should be fast
    console.log("⏳ Waiting for slides to be generated...");
    
    // Wait for the slides API call to complete
    await page.waitForLoadState('networkidle');
    
    // Now wait for slide thumbnails to appear
    const slideThumbnails = page.locator('[data-testid^="slide-thumbnail-"]');
    await expect(slideThumbnails.first()).toBeVisible({ timeout: 10000 });
    
    console.log("✅ Slides generated successfully");
    
    // Verify we have multiple slides
    const slideCount = await page.locator('[data-testid^="slide-thumbnail-"]').count();
    expect(slideCount).toBeGreaterThan(0);
    console.log(`✅ Generated ${slideCount} slides successfully`);
    
    // Verify slides step is now marked as completed
    const slidesCompleted = await waitForStepCompletion(page, 'slides', 30000);
    expect(slidesCompleted).toBe(true);
    console.log("✅ Slides step marked as completed");
  });
});
