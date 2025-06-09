import { test, expect } from "@playwright/test";
import { navigateToTestPresentation, waitForStepCompletion, getApiUrl, resetTestDatabase } from "./utils";
import { TEST_CATEGORIES } from "../test-config";

test.setTimeout(15000); // 15s timeout for offline mode

test.describe("Slides Display", () => {
  // Reset database before each test to ensure clean state
  test.beforeEach(async ({ page }) => {
    await resetTestDatabase(page);
  });
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
    
    // Click the button and wait for slides generation API response
    const [slidesResponse] = await Promise.all([
      page.waitForResponse(response => 
        response.url().includes('/presentations') && 
        response.url().includes('/steps/slides/run') && 
        response.status() === 200,
        { timeout: 15000 }
      ),
      button.click()
    ]);
    console.log("✅ Slides generation API responded");
    
    // Wait for slides to be generated - in offline mode this should be fast
    console.log("⏳ Waiting for slides to be rendered...");
    
    // Wait for the page to update
    await page.waitForLoadState('networkidle');
    
    // First check if we need to navigate to the slides view page
    // Some presentations might show a "Generate Slides" button after running
    const generateSlidesBtn = page.getByRole('button', { name: 'Generate Slides' });
    if (await generateSlidesBtn.isVisible({ timeout: 2000 }).catch(() => false)) {
      console.log("📝 Found Generate Slides button - clicking it");
      await generateSlidesBtn.click();
      await page.waitForLoadState('networkidle');
    }
    
    // Now wait for slide thumbnails to appear - they might be in different containers
    const slideThumbnails = page.locator('[data-testid^="slide-thumbnail-"], [data-testid="slides-container"] .slide-preview, .slide-container');
    await expect(slideThumbnails.first()).toBeVisible({ timeout: 15000 });
    
    console.log("✅ Slides generated successfully");
    
    // Verify we have multiple slides
    const slideCount = await slideThumbnails.count();
    expect(slideCount).toBeGreaterThan(0);
    console.log(`✅ Generated ${slideCount} slides successfully`);
    
    // Verify slides step is now marked as completed
    const slidesCompleted = await waitForStepCompletion(page, 'slides', 30000);
    expect(slidesCompleted).toBe(true);
    console.log("✅ Slides step marked as completed");
  });
});
