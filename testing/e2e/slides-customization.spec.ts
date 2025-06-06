import { test, expect } from '@playwright/test';
import { navigateToTestPresentationById } from './utils';

test.describe.skip('Slides Customization', () => {
  test.beforeEach(async ({ page }) => {
    // Use preseeded presentation ID 26 (Slides Customization Test - research completed)
    const presentation = await navigateToTestPresentationById(page, 26);
    console.log(`✅ Using preseeded presentation: ${presentation?.name}`);
  });

  test('should show customization dialog when clicking customize button', async ({ page }) => {
    // Navigate to slides step
    await page.click('[data-testid="step-nav-slides"]');
    
    // Should see the customize button
    await expect(page.locator('[data-testid="customize-slides-button"]')).toBeVisible();
    
    // Click customize button
    await page.click('[data-testid="customize-slides-button"]');
    
    // Should see customization dialog
    await expect(page.locator('dialog[open]')).toBeVisible();
    await expect(page.locator('text=Customize Slides Generation')).toBeVisible();
    
    // Should see all customization fields
    await expect(page.locator('#target_slides')).toBeVisible();
    await expect(page.locator('text=Target Audience')).toBeVisible();
    await expect(page.locator('text=Content Density')).toBeVisible();
    await expect(page.locator('#presentation_duration')).toBeVisible();
    await expect(page.locator('#custom_prompt')).toBeVisible();
  });

  test('should allow customizing slides generation parameters', async ({ page }) => {
    // Navigate to slides step
    await page.click('[data-testid="step-nav-slides"]');
    
    // Open customization dialog
    await page.click('[data-testid="customize-slides-button"]');
    
    // Customize parameters
    await page.fill('#target_slides', '8');
    
    // Select target audience
    await page.click('button:has-text("Select audience")');
    await page.click('text=Technical Team');
    
    // Select content density
    await page.click('button:has-text("Select density")');
    await page.click('text=High (Detailed information)');
    
    await page.fill('#presentation_duration', '25');
    await page.fill('#custom_prompt', 'Focus on implementation challenges and technical architecture');
    
    // Close dialog
    await page.keyboard.press('Escape');
    
    // Verify parameters are saved by reopening dialog
    await page.click('[data-testid="customize-slides-button"]');
    await expect(page.locator('#target_slides')).toHaveValue('8');
    await expect(page.locator('#presentation_duration')).toHaveValue('25');
    await expect(page.locator('#custom_prompt')).toHaveValue('Focus on implementation challenges and technical architecture');
  });

  test('should generate slides with custom parameters', async ({ page }) => {
    // Navigate to slides step
    await page.click('[data-testid="step-nav-slides"]');
    
    // Open customization dialog and set parameters
    await page.click('[data-testid="customize-slides-button"]');
    await page.fill('#target_slides', '6');
    
    // Select executives audience
    await page.click('button:has-text("Select audience")');
    await page.click('text=Executives');
    
    // Select low density
    await page.click('button:has-text("Select density")');
    await page.click('text=Low (Minimal text, visual focus)');
    
    await page.fill('#presentation_duration', '12');
    await page.fill('#custom_prompt', 'Focus on business value and ROI');
    await page.keyboard.press('Escape');
    
    // Generate slides
    await page.click('[data-testid="run-slides-button"]');
    
    // Wait for slides generation to complete
    await page.waitForSelector('[data-testid="slides-completed"]', { timeout: 60000 });
    
    // Verify slides were generated
    const slideCount = await page.locator('[data-testid^="slide-thumbnail-"]').count();
    expect(slideCount).toBeGreaterThan(0);
    
    // Should have approximately 6 slides (with some tolerance for auto-generated slides)
    expect(slideCount).toBeGreaterThanOrEqual(5);
    expect(slideCount).toBeLessThanOrEqual(10);
  });

  test('should show slides generation in progress with custom parameters', async ({ page }) => {
    // Navigate to slides step
    await page.click('[data-testid="step-nav-slides"]');
    
    // Set custom parameters
    await page.click('[data-testid="customize-slides-button"]');
    await page.fill('#target_slides', '10');
    await page.keyboard.press('Escape');
    
    // Start slides generation
    await page.click('[data-testid="run-slides-button"]');
    
    // Should see generation in progress
    await expect(page.locator('text=Generating Slides...')).toBeVisible();
    await expect(page.locator('[data-testid="slides-generating"]')).toBeVisible();
    
    // Wait for completion
    await page.waitForSelector('[data-testid="slides-completed"]', { timeout: 60000 });
  });

  test('should validate input ranges for numeric fields', async ({ page }) => {
    // Navigate to slides step
    await page.click('[data-testid="step-nav-slides"]');
    
    // Open customization dialog
    await page.click('[data-testid="customize-slides-button"]');
    
    // Test target slides validation
    const targetSlidesInput = page.locator('#target_slides');
    await expect(targetSlidesInput).toHaveAttribute('min', '3');
    await expect(targetSlidesInput).toHaveAttribute('max', '30');
    
    // Test presentation duration validation  
    const durationInput = page.locator('#presentation_duration');
    await expect(durationInput).toHaveAttribute('min', '5');
    await expect(durationInput).toHaveAttribute('max', '120');
  });

  test('should have proper default values in customization dialog', async ({ page }) => {
    // Navigate to slides step
    await page.click('[data-testid="step-nav-slides"]');
    
    // Open customization dialog
    await page.click('[data-testid="customize-slides-button"]');
    
    // Check default values
    await expect(page.locator('#target_slides')).toHaveValue('10');
    await expect(page.locator('#presentation_duration')).toHaveValue('15');
    await expect(page.locator('#custom_prompt')).toHaveValue('');
    
    // Check that select components are present and working
    await expect(page.locator('button:has-text("General Audience")')).toBeVisible();
    await expect(page.locator('button:has-text("Medium (Balanced content)")')).toBeVisible();
  });

});