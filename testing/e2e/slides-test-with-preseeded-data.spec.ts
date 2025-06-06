import { test, expect } from "@playwright/test";
import { navigateToTestPresentation, verifyPresentationSteps, waitForStepCompletion } from "./utils";
import { TEST_CATEGORIES } from "../test-config";

test.setTimeout(60000);

test.describe("Slides Generation with Pre-seeded Data", () => {
  test("should generate slides from pre-completed research", async ({ page }) => {
    // Navigate to a presentation that already has research completed
    const presentation = await navigateToTestPresentation(page, TEST_CATEGORIES.RESEARCH_COMPLETE, 0);
    
    console.log(`📋 Testing with: ${presentation.name}`);
    console.log(`📚 Topic: ${presentation.topic}`);
    
    // Verify the presentation has the expected step statuses
    await verifyPresentationSteps(page, presentation);
    
    // Navigate to slides step
    console.log("🔍 Navigating to slides step...");
    await page.getByTestId('step-nav-slides').click();
    await page.waitForLoadState('networkidle');
    
    // Verify research content is visible (since research is already completed)
    await expect(page.getByTestId('ai-research-content-label')).toBeVisible();
    await expect(page.getByTestId('ai-research-content')).toBeVisible();
    
    // Run slides generation
    console.log("🔍 Running slides generation...");
    const runSlidesButton = page.getByTestId('run-slides-button');
    await expect(runSlidesButton).toBeVisible();
    await expect(runSlidesButton).toBeEnabled();
    
    const [slidesResponse] = await Promise.all([
      page.waitForResponse(resp => 
        resp.url().includes(`/presentations/${presentation.id}/steps/slides/run`) && 
        resp.status() === 200
      ),
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
    
    // Verify slides step is now marked as completed
    const slidesCompleted = await waitForStepCompletion(page, 'slides', 30000);
    expect(slidesCompleted).toBe(true);
    console.log("✅ Slides step marked as completed");
    
    // Verify that illustration step is now enabled
    const illustrationButton = page.getByTestId('step-nav-illustration');
    await expect(illustrationButton).toBeEnabled({ timeout: 10000 });
    console.log("✅ Illustration step is now enabled");
  });
  
  test("should generate slides from second research-complete presentation", async ({ page }) => {
    // Test with the second research-complete presentation to ensure data variety
    const presentation = await navigateToTestPresentation(page, TEST_CATEGORIES.RESEARCH_COMPLETE, 1);
    
    console.log(`📋 Testing with: ${presentation.name}`);
    console.log(`📚 Topic: ${presentation.topic}`);
    
    // Navigate to slides and run generation
    await page.getByTestId('step-nav-slides').click();
    await page.waitForLoadState('networkidle');
    
    const runSlidesButton = page.getByTestId('run-slides-button');
    await expect(runSlidesButton).toBeVisible();
    await runSlidesButton.click();
    
    // Wait for completion
    await page.waitForSelector('[data-testid^="slide-thumbnail-"]', { timeout: 30000 });
    await expect(page.getByTestId("slide-thumbnail-0")).toBeVisible();
    
    const slideCount = await page.locator('[data-testid^="slide-thumbnail-"]').count();
    expect(slideCount).toBeGreaterThan(0);
    console.log(`✅ Generated ${slideCount} slides for ${presentation.topic}`);
  });
});