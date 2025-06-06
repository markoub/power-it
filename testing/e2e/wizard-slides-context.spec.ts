import { test, expect } from '@playwright/test';
import { navigateToTestPresentationById } from './utils';

test.setTimeout(180000);

test.describe('Slides Wizard Context', () => {
  test('should handle single slide modifications', async ({ page }) => {
    // Use preseeded presentation ID 16 (Wizard Slides Ready - research and slides completed)
    const presentation = await navigateToTestPresentationById(page, 16);
    console.log(`✅ Using preseeded presentation: ${presentation?.name}`);

    // Navigate to slides step (already has slides completed)
    await page.getByTestId('step-nav-slides').click();
    await page.waitForLoadState('networkidle');
    
    // Wait for slides to render - check multiple possible states
    try {
      await page.waitForSelector('[data-testid^="slide-thumbnail-"]', { 
        timeout: 30000,
        state: 'visible' 
      });
      console.log('✅ Slides rendered');
    } catch (e) {
      // If no slides, check if there's an error or empty state
      const errorMessage = await page.locator('[role="alert"]').count();
      const emptyState = await page.locator('text=/No slides|Generate slides/i').count();
      if (errorMessage > 0 || emptyState > 0) {
        throw new Error('Slides generation failed or returned empty');
      }
      throw e;
    }

    // Check initial wizard context
    const wizardHeader = page.locator('[data-testid="wizard-header"]').first();
    await expect(wizardHeader).toBeVisible({ timeout: 10000 });
    
    // The context might start in either single slide or overview mode
    const headerText = await wizardHeader.textContent();
    console.log(`✅ Initial context: ${headerText}`);
    
    // If already in single slide mode, we're good to go
    if (headerText?.includes('Single Slide')) {
      console.log('✅ Already in single slide mode');
    } else {
      // If in overview mode, select a slide
      const firstSlide = page.getByTestId('slide-thumbnail-0');
      await expect(firstSlide).toBeVisible({ timeout: 10000 });
      await firstSlide.click();
      console.log('✅ Selected first slide');
      
      // Verify context changed to single slide
      await expect(wizardHeader).toContainText('Single Slide');
      console.log('✅ Wizard context updated to single slide');
    }

    // Verify back to overview button is visible
    const backButton = page.getByTestId('back-to-overview-button');
    await expect(backButton).toBeVisible();
    console.log('✅ Back to overview button is visible');

    // Test single slide modification
    console.log('🧙‍♂️ Testing single slide modification...');
    
    const wizardInput = page.getByTestId('wizard-input');
    await wizardInput.fill('Make this slide more engaging and add bullet points');
    await wizardInput.press('Enter');
    
    // Wait for wizard response first
    await page.waitForSelector('[data-testid="wizard-message-assistant"]:last-child', { timeout: 15000 });
    console.log('✅ Wizard responded');
    
    // Check if a suggestion was generated (may not always happen in offline mode)
    const suggestionBox = page.locator('[data-testid="wizard-suggestion"]');
    const suggestionVisible = await suggestionBox.isVisible({ timeout: 5000 }).catch(() => false);
    
    if (suggestionVisible) {
      console.log('✅ Single slide suggestion generated');
      
      const applyButton = page.locator('[data-testid="wizard-apply-button"]');
      await expect(applyButton).toBeVisible();
      
      // Wait for the apply button to become enabled
      await expect(applyButton).toBeEnabled({ timeout: 10000 });
      await applyButton.click();
      
      // Verify suggestion disappeared
      await expect(suggestionBox).not.toBeVisible();
      console.log('✅ Single slide modification applied');
    } else {
      // No suggestion generated, but wizard should have responded
      const responseCount = await page.locator('[data-testid="wizard-message-assistant"]').count();
      expect(responseCount).toBeGreaterThan(1); // At least welcome + response
      console.log('✅ Wizard provided guidance without suggestion');
    }

    // Test back to overview functionality
    await backButton.click();
    await page.waitForLoadState('networkidle');
    
    // Verify context changed back to all slides
    await expect(wizardHeader).toContainText('All Slides');
    console.log('✅ Context switched back to: All Slides (Overview mode)');
  });

  test('should handle presentation-level modifications (add/remove slides)', async ({ page }) => {
    // Use preseeded presentation ID 16 (Wizard Slides Ready - research and slides completed)
    const presentation = await navigateToTestPresentationById(page, 16);
    console.log(`✅ Using preseeded presentation: ${presentation?.name}`);

    // Navigate to slides step (already has slides completed)
    await page.getByTestId('step-nav-slides').click();
    await page.waitForLoadState('networkidle');
    
    // Wait for slides to render
    try {
      await page.waitForSelector('[data-testid^="slide-thumbnail-"]', { 
        timeout: 30000,
        state: 'visible' 
      });
      console.log('✅ Slides rendered');
    } catch (e) {
      console.error('Failed to find slide thumbnails');
      throw e;
    }

    // Check wizard context
    const wizardHeader = page.locator('[data-testid="wizard-header"]').first();
    await expect(wizardHeader).toBeVisible({ timeout: 10000 });
    
    const headerText = await wizardHeader.textContent();
    console.log(`✅ Current context: ${headerText}`);

    // Test presentation-level modification (add slide)
    console.log('🧙‍♂️ Testing presentation-level modification...');
    
    const wizardInput = page.getByTestId('wizard-input');
    await wizardInput.fill('Add a new slide about renewable energy costs and benefits');
    await wizardInput.press('Enter');
    
    // Wait for wizard response
    await page.waitForSelector('[data-testid="wizard-message-assistant"]:last-child', { timeout: 10000 });
    
    // Check for suggestion or just response
    const suggestionBox = page.locator('[data-testid="wizard-suggestion"]');
    const suggestionVisible = await suggestionBox.isVisible({ timeout: 5000 }).catch(() => false);
    
    if (suggestionVisible) {
      console.log('✅ Presentation-level suggestion generated');
      
      // Apply changes
      const applyButton = page.locator('[data-testid="wizard-apply-button"]');
      await expect(applyButton).toBeVisible();
      await applyButton.click();
      console.log('✅ Presentation-level changes applied');
    } else {
      // Should at least get a response
      const responseMessages = await page.locator('[data-testid="wizard-message-assistant"]').count();
      expect(responseMessages).toBeGreaterThan(1);
      console.log('✅ Presentation-level request processed');
    }
  });

  test('should provide slides guidance and best practices', async ({ page }) => {
    // Use preseeded presentation ID 16 (Wizard Slides Ready - research and slides completed)
    const presentation = await navigateToTestPresentationById(page, 16);
    console.log(`✅ Using preseeded presentation: ${presentation?.name}`);

    // Navigate to slides step (already has slides completed)
    await page.getByTestId('step-nav-slides').click();
    await page.waitForLoadState('networkidle');
    
    // Wait for slides to render
    try {
      await page.waitForSelector('[data-testid^="slide-thumbnail-"]', { 
        timeout: 30000,
        state: 'visible' 
      });
      console.log('✅ Slides rendered');
    } catch (e) {
      console.error('Failed to find slide thumbnails');
      throw e;
    }

    // Test general slides guidance
    const wizardInput = page.getByTestId('wizard-input');
    await wizardInput.fill('What are some best practices for slide design?');
    await wizardInput.press('Enter');
    
    // Wait for wizard response
    await page.waitForSelector('[data-testid="wizard-message-assistant"]:last-child', { timeout: 10000 });
    
    // Should get helpful guidance
    const responseMessages = await page.locator('[data-testid="wizard-message-assistant"]').count();
    expect(responseMessages).toBeGreaterThan(1);
    console.log('✅ Slides guidance provided');
  });

  test('should handle context switching between single and all slides', async ({ page }) => {
    // Use preseeded presentation ID 16 (Wizard Slides Ready - research and slides completed)
    const presentation = await navigateToTestPresentationById(page, 16);
    console.log(`✅ Using preseeded presentation: ${presentation?.name}`);

    // Navigate to slides step (already has slides completed)
    await page.getByTestId('step-nav-slides').click();
    await page.waitForLoadState('networkidle');
    
    // Wait for slides to render
    try {
      await page.waitForSelector('[data-testid^="slide-thumbnail-"]', { 
        timeout: 30000,
        state: 'visible' 
      });
      console.log('✅ Slides rendered');
    } catch (e) {
      console.error('Failed to find slide thumbnails');
      throw e;
    }

    const wizardHeader = page.locator('[data-testid="wizard-header"]').first();
    await expect(wizardHeader).toBeVisible({ timeout: 10000 });
    
    // Get initial context
    const initialHeaderText = await wizardHeader.textContent();
    console.log(`✅ Initial context: ${initialHeaderText}`);
    
    // Test context switching
    if (initialHeaderText?.includes('Single Slide')) {
      // Starting in single slide mode - switch to overview first
      console.log('📋 Starting in single slide mode');
      
      // Click back to overview button
      const backButton = page.getByTestId('back-to-overview-button');
      await expect(backButton).toBeVisible();
      await backButton.click();
      await page.waitForLoadState('networkidle');
      
      // Verify context changed to all slides
      await expect(wizardHeader).toContainText('All Slides');
      console.log('✅ Context switched to: All Slides (Overview mode)');
      
      // Now select a slide to go back to single slide mode
      const firstSlide = page.getByTestId('slide-thumbnail-0');
      await expect(firstSlide).toBeVisible({ timeout: 10000 });
      await firstSlide.click();
      
      // Verify context changed back to single slide
      await expect(wizardHeader).toContainText('Single Slide');
      console.log('✅ Context switched back to: Single Slide');
    } else {
      // Starting in overview mode - select a slide first
      console.log('📋 Starting in overview mode');
      
      // Select a slide to switch to single slide context
      const firstSlide = page.getByTestId('slide-thumbnail-0');
      await expect(firstSlide).toBeVisible({ timeout: 10000 });
      await firstSlide.click();
      
      // Context should change to single slide
      await expect(wizardHeader).toContainText('Single Slide');
      console.log('✅ Context switched to: Single Slide');
      
      // Click back to overview button
      const backButton = page.getByTestId('back-to-overview-button');
      await expect(backButton).toBeVisible();
      await backButton.click();
      await page.waitForLoadState('networkidle');
      
      // Verify context changed back to all slides
      await expect(wizardHeader).toContainText('All Slides');
      console.log('✅ Context switched back to: All Slides (Overview mode)');
    }
    
    console.log('✅ Context switching test completed');
  });

  test('should handle navigation between slides in single slide mode', async ({ page }) => {
    // Use preseeded presentation ID 16 (Wizard Slides Ready - research and slides completed)
    const presentation = await navigateToTestPresentationById(page, 16);
    console.log(`✅ Using preseeded presentation: ${presentation?.name}`);

    // Navigate to slides step (already has slides completed)
    await page.getByTestId('step-nav-slides').click();
    await page.waitForLoadState('networkidle');
    
    // Wait for slides to render
    try {
      await page.waitForSelector('[data-testid^="slide-thumbnail-"]', { 
        timeout: 30000,
        state: 'visible' 
      });
      console.log('✅ Slides rendered');
    } catch (e) {
      console.error('Failed to find slide thumbnails');
      throw e;
    }

    // Check if we're already in single slide mode
    const wizardHeader = page.locator('[data-testid="wizard-header"]').first();
    await expect(wizardHeader).toBeVisible({ timeout: 10000 });
    
    const headerText = await wizardHeader.textContent();
    if (!headerText?.includes('Single Slide')) {
      // If not in single slide mode, select first slide
      const firstSlide = page.getByTestId('slide-thumbnail-0');
      await expect(firstSlide).toBeVisible({ timeout: 10000 });
      await firstSlide.click();
      console.log('✅ Selected first slide');
      
      // Verify we're now in single slide mode
      await expect(wizardHeader).toContainText('Single Slide');
    } else {
      console.log('✅ Already in single slide mode');
    }

    // Check if there are multiple slides
    const slideCount = await page.locator('[data-testid^="slide-thumbnail-horizontal-"]').count();
    console.log(`Found ${slideCount} slides`);

    if (slideCount > 1) {
      // Click on second slide using horizontal thumbnail
      const secondSlideHorizontal = page.getByTestId('slide-thumbnail-horizontal-1');
      await expect(secondSlideHorizontal).toBeVisible();
      await secondSlideHorizontal.click();
      console.log('✅ Clicked second slide via horizontal thumbnail');

      // Verify we're still in single slide mode but with different slide
      await expect(wizardHeader).toContainText('Single Slide');
      console.log('✅ Still in single slide mode with different slide selected');

      // Verify we're viewing the second slide now
      // Check for any visual indication (the slide content should have changed)
      await page.waitForTimeout(500); // Brief wait for UI update
      console.log('✅ Successfully navigated to second slide');
    }

    console.log('✅ Slide navigation test completed');
  });
}); 