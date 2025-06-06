import { test, expect } from "@playwright/test";
import { navigateToTestPresentation, goToPresentationsPage, waitForNetworkIdle } from "./utils";

test.setTimeout(120000);

test.describe("PPTX Preview", () => {
  test("pptx step shows slide images - with completed presentation", async ({ page }) => {
    // Use presentation ID 11 which has completed PPTX
    const presentation = await navigateToTestPresentation(page, "complete", 0);
    console.log(`✅ Using test presentation: ${presentation.name} (ID: ${presentation.id})`);

    // Navigate directly to PPTX step since it's already completed
    console.log('🔍 Navigating to PPTX step...');
    await page.getByTestId('step-nav-pptx').click();
    await page.waitForTimeout(1000);

    // Check if we have thumbnails (should already be there)
    const thumbnailCount = await page.locator('[data-testid^="pptx-thumb-"]').count();
    console.log(`✅ Found ${thumbnailCount} PPTX thumbnails`);
    
    expect(thumbnailCount).toBeGreaterThan(0);

    // Wait for first PPTX slide thumbnail
    const firstThumb = page.getByTestId("pptx-thumb-0");
    await expect(firstThumb).toBeVisible({ timeout: 10000 });

    // Click first thumbnail to show slide
    await firstThumb.click();

    // Verify slide details are visible
    const slideDetails = page.locator('.slide-details');
    await expect(slideDetails).toBeVisible();

    // Verify the slide image is displayed
    const slideImage = slideDetails.locator('img');
    await expect(slideImage).toBeVisible();

    console.log('✅ PPTX preview test completed successfully!');

    // Navigate back to presentations list and verify thumbnail
    await goToPresentationsPage(page);
    await waitForNetworkIdle(page);
    const card = page.getByTestId(`presentation-card-${presentation.id}`);
    const thumb = card.getByTestId('presentation-thumbnail');
    await expect(thumb).toBeVisible();
    
    // In test mode with offline data, thumbnails might use placeholder images
    // Just verify the thumbnail element exists and is visible
    const thumbSrc = await thumb.getAttribute('src');
    console.log(`✅ Presentation thumbnail visible with src: ${thumbSrc}`);
  });

  test("pptx step requires compiled step to be complete", async ({ page }) => {
    // Use presentation ID 10 which has illustrations but needs compiled step first
    const presentation = await navigateToTestPresentation(page, "illustrations_complete", 0);
    console.log(`✅ Using test presentation: ${presentation.name} (ID: ${presentation.id})`);

    // Check if PPTX step is available
    console.log('🔍 Checking PPTX step availability...');
    const pptxStepButton = page.getByTestId('step-nav-pptx');
    
    // Verify PPTX step is disabled when compiled step is not complete
    await expect(pptxStepButton).toBeDisabled();
    console.log('✅ PPTX step correctly disabled when compiled step is incomplete');
    
    // Also verify the compiled step button state
    const compiledStepButton = page.getByTestId('step-nav-compiled');
    
    // The compiled step might be disabled if illustrations aren't fully ready
    // Or it might be enabled but not yet run - either is acceptable for this test
    const compiledDisabled = await compiledStepButton.isDisabled();
    console.log(`✅ Compiled step button is ${compiledDisabled ? 'disabled' : 'enabled'}`);
    
    // Try to force-click PPTX step to verify it shows appropriate message
    await pptxStepButton.click({ force: true });
    await page.waitForTimeout(1000);
    
    // Verify no PPTX content is shown
    const thumbnailCount = await page.locator('[data-testid^="pptx-thumb-"]').count();
    expect(thumbnailCount).toBe(0);
    console.log('✅ No PPTX thumbnails shown when prerequisites incomplete');
  });

  test("pptx not available when slides incomplete", async ({ page }) => {
    // Use presentation ID 5 which only has research completed
    const presentation = await navigateToTestPresentation(page, "research_complete", 0);
    console.log(`✅ Using test presentation: ${presentation.name} (ID: ${presentation.id})`);

    // Try to navigate to PPTX step
    console.log('🔍 Checking PPTX step availability...');
    const pptxStepButton = page.getByTestId('step-nav-pptx');
    
    // The step button should exist but be disabled
    await expect(pptxStepButton).toBeVisible();
    await expect(pptxStepButton).toBeDisabled();
    
    // Click it anyway to navigate there
    await pptxStepButton.click({ force: true });
    await page.waitForTimeout(1000);
    
    // Verify no PPTX content is available
    const runPptxButton = page.getByTestId('run-pptx-button');
    const pptxButtonExists = await runPptxButton.count() > 0;
    
    // Should either have no button or a disabled button
    if (pptxButtonExists) {
      await expect(runPptxButton).toBeDisabled();
    }
    
    // Verify no thumbnails are shown
    const thumbnailCount = await page.locator('[data-testid^="pptx-thumb-"]').count();
    expect(thumbnailCount).toBe(0);
    
    console.log('✅ Verified PPTX not available when prerequisites incomplete');
  });
});
