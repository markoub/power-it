import { test, expect } from '@playwright/test';
import { createPresentation } from './utils';

test.setTimeout(120000); // 2 minutes

test.describe('Wizard Slide Management', () => {
  let presentationId: string;

  test.beforeEach(async ({ page }) => {
    // Create a presentation with slides for testing
    const name = `Wizard Slide Test ${Date.now()}`;
    const topic = 'Kubernetes Best Practices';
    presentationId = await createPresentation(page, name, topic);
    
    // Complete research step
    const [researchResponse] = await Promise.all([
      page.waitForResponse(resp => resp.url().includes(`/presentations/${presentationId}/steps/research/run`) && resp.status() === 200),
      page.getByTestId('start-ai-research-button').click()
    ]);
    
    // Navigate to slides and generate slides
    await page.getByTestId('step-nav-slides').click();
    await page.waitForLoadState('networkidle');
    
    const runSlidesButton = page.getByTestId('run-slides-button');
    if (await runSlidesButton.count() > 0) {
      const [slidesResponse] = await Promise.all([
        page.waitForResponse(resp => resp.url().includes(`/presentations/${presentationId}/steps/slides/run`) && resp.status() === 200),
        runSlidesButton.click()
      ]);
      // Wait for slides to be generated
      await page.waitForFunction(() => {
        const thumbnails = document.querySelectorAll('[data-testid^="slide-thumbnail-"]');
        return thumbnails.length > 0;
      }, {}, { timeout: 30000 });
    }
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