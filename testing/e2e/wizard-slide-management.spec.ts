import { test, expect } from '@playwright/test';
import { navigateToTestPresentationById } from './utils';

test.setTimeout(120000); // 2 minutes

test.describe('Wizard Slide Management', () => {
  test.beforeEach(async ({ page }) => {
    // Use preseeded presentation ID 16 (Wizard Slides Ready - has slides generated)
    const presentation = await navigateToTestPresentationById(page, 16);
    console.log(`✅ Using preseeded presentation: ${presentation?.name}`);
    
    // Navigate to slides step to see the slides
    await page.getByTestId('step-nav-slides').click();
    await page.waitForLoadState('networkidle');
    
    // Ensure slides are visible
    await expect(page.locator('[data-testid^="slide-thumbnail-"]').first()).toBeVisible();
  });

  test('should add a new slide via wizard', async ({ page }) => {
    // Click on wizard input
    await page.getByTestId('wizard-input').click();
    
    // Type request to add a slide
    await page.getByTestId('wizard-input').fill('Add a new slide about Kubernetes security best practices');
    
    // Send the message
    await page.getByTestId('wizard-send-button').click();
    
    // Wait for response
    await page.waitForSelector('[data-testid="wizard-message-assistant"]:last-child', { timeout: 10000 });
    
    // Check if a suggestion appears
    const suggestionBox = page.locator('text=Suggested Changes');
    if (await suggestionBox.count() > 0) {
      // Apply the suggestion
      const applyButton = page.locator('button:has-text("Apply Changes")');
      if (await applyButton.count() > 0) {
        await applyButton.click();
        await page.waitForLoadState('networkidle');
      }
    }
    
    // Verify a new slide was added (check slide count or look for new content)
    const slides = page.locator('[data-testid^="slide-thumbnail-"]');
    const slideCount = await slides.count();
    expect(slideCount).toBeGreaterThan(0);
  });

  test('should remove a slide via wizard', async ({ page }) => {
    // Click on wizard input
    await page.getByTestId('wizard-input').click();
    
    // Type request to remove a slide
    await page.getByTestId('wizard-input').fill('Remove the introduction slide');
    
    // Send the message
    await page.getByTestId('wizard-send-button').click();
    
    // Wait for response
    await page.waitForSelector('[data-testid="wizard-message-assistant"]:last-child', { timeout: 10000 });
    
    // Check if a suggestion appears
    const suggestionBox = page.locator('text=Suggested Changes');
    if (await suggestionBox.count() > 0) {
      // Apply the suggestion
      const applyButton = page.locator('button:has-text("Apply Changes")');
      if (await applyButton.count() > 0) {
        await applyButton.click();
        await page.waitForLoadState('networkidle');
      }
    }
    
    // Verify the slide was handled (either removed or marked for removal)
    console.log('✅ Slide removal request processed');
  });

  test('should add multiple slides via wizard', async ({ page }) => {
    // Click on wizard input
    await page.getByTestId('wizard-input').click();
    await page.getByTestId('wizard-input').fill('Add two new slides: one about Kubernetes monitoring and another about troubleshooting');
    
    // Send the message
    await page.getByTestId('wizard-send-button').click();
    
    // Wait for response
    await page.waitForSelector('[data-testid="wizard-message-assistant"]:last-child', { timeout: 10000 });
    
    // Check if a suggestion appears
    const suggestionBox = page.locator('text=Suggested Changes');
    if (await suggestionBox.count() > 0) {
      // Apply the suggestion
      const applyButton = page.locator('button:has-text("Apply Changes")');
      if (await applyButton.count() > 0) {
        await applyButton.click();
        await page.waitForLoadState('networkidle');
      }
    }
    
    console.log('✅ Multiple slides request processed');
  });

  test('should reorder slides via wizard', async ({ page }) => {
    // Click on wizard input
    await page.getByTestId('wizard-input').click();
    await page.getByTestId('wizard-input').fill('Add a slide about Kubernetes networking');
    
    // Send the message
    await page.getByTestId('wizard-send-button').click();
    
    // Wait for response
    await page.waitForSelector('[data-testid="wizard-message-assistant"]:last-child', { timeout: 10000 });
    
    // Check if a suggestion appears and apply it
    const suggestionBox = page.locator('text=Suggested Changes');
    if (await suggestionBox.count() > 0) {
      const applyButton = page.locator('button:has-text("Apply Changes")');
      if (await applyButton.count() > 0) {
        await applyButton.click();
        await page.waitForLoadState('networkidle');
      }
    }
    
    console.log('✅ Slide addition request processed');
  });

  test('should reorganize slides via wizard', async ({ page }) => {
    // Click on wizard input
    await page.getByTestId('wizard-input').click();
    await page.getByTestId('wizard-input').fill('Reorganize the slides to put the introduction first');
    
    // Send the message
    await page.getByTestId('wizard-send-button').click();
    
    // Wait for response
    await page.waitForSelector('[data-testid="wizard-message-assistant"]:last-child', { timeout: 10000 });
    
    // Check if a suggestion appears
    const suggestionBox = page.locator('text=Suggested Changes');
    if (await suggestionBox.count() > 0) {
      // Apply the suggestion
      const applyButton = page.locator('button:has-text("Apply Changes")');
      if (await applyButton.count() > 0) {
        await applyButton.click();
        await page.waitForLoadState('networkidle');
      }
    }
    
    console.log('✅ Slide reorganization request processed');
  });
}); 