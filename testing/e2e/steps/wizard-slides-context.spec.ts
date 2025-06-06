import { test, expect } from '@playwright/test';
import { createPresentation } from '../utils';

test.describe('Wizard Slides Context and Keyboard Navigation', () => {
  
  test('wizard context should update based on slide selection', async ({ page }) => {
    // Create a new presentation instead of relying on existing one
    const name = `Wizard Context Test ${Date.now()}`;
    const topic = 'Test Topic for Wizard';
    const id = await createPresentation(page, name, topic);
    
    // Complete research
    const [researchResponse] = await Promise.all([
      page.waitForResponse(resp => resp.url().includes(`/presentations/${id}/steps/research/run`) && resp.status() === 200),
      page.getByTestId('start-ai-research-button').click()
    ]);
    
    // Wait for research to complete
    await page.waitForSelector('[data-testid="ai-research-content"]', { state: 'visible', timeout: 30000 });
    
    // Navigate to slides
    await page.getByTestId('step-nav-slides').click();
    await page.waitForLoadState('networkidle');
    
    // Generate slides if needed
    const runSlidesButton = page.getByTestId('run-slides-button');
    if (await runSlidesButton.count() > 0) {
      await runSlidesButton.click();
    }
    
    // Wait for slides to load
    await page.waitForSelector('[data-testid="slide-thumbnail-0"]', { timeout: 30000 });
    
    // Check wizard shows overview context initially
    const wizardHeader = page.locator('[data-testid="wizard-header"]');
    await expect(wizardHeader).toBeVisible();
    await expect(wizardHeader).toContainText('All Slides');
    
    // Click on first slide
    await page.click('[data-testid="slide-thumbnail-0"]');
    
    // Wait for single slide view
    await page.waitForSelector('[data-testid="back-to-overview-button"]');
    
    // Verify wizard updated context
    await expect(wizardHeader).toContainText('Single Slide');
    await expect(page.locator('h2.gradient-text')).toBeVisible();
    
    // Verify navigation info is shown
    const navInfo = page.locator('text=/Slide \\d+ of \\d+/');
    await expect(navInfo).toBeVisible();
    
    // Verify keyboard hint
    const keyboardHint = page.locator('text=(Use ← → arrows to navigate)');
    await expect(keyboardHint).toBeVisible();
  });

  test('keyboard navigation should work in single slide view', async ({ page }) => {
    // Create a new presentation
    const name = `Keyboard Nav Test ${Date.now()}`;
    const topic = 'Test Topic for Navigation';
    const id = await createPresentation(page, name, topic);
    
    // Complete research and generate slides
    const [researchResponse] = await Promise.all([
      page.waitForResponse(resp => resp.url().includes(`/presentations/${id}/steps/research/run`) && resp.status() === 200),
      page.getByTestId('start-ai-research-button').click()
    ]);
    await page.waitForSelector('[data-testid="ai-research-content"]', { state: 'visible', timeout: 30000 });
    await page.getByTestId('step-nav-slides').click();
    await page.waitForLoadState('networkidle');
    
    const runSlidesButton = page.getByTestId('run-slides-button');
    if (await runSlidesButton.count() > 0) {
      await runSlidesButton.click();
    }
    
    // Wait for slides and click first one
    await page.waitForSelector('[data-testid="slide-thumbnail-0"]', { timeout: 30000 });
    await page.click('[data-testid="slide-thumbnail-0"]');
    
    // Wait for single slide view
    await page.waitForSelector('[data-testid="back-to-overview-button"]');
    
    // Get initial slide title
    const initialTitle = await page.locator('h2.gradient-text').textContent();
    
    // Press right arrow to go to next slide
    await page.keyboard.press('ArrowRight');
    await page.waitForTimeout(300);
    
    // Verify slide changed
    const nextTitle = await page.locator('h2.gradient-text').textContent();
    expect(nextTitle).not.toBe(initialTitle);
    
    // Press left arrow to go back
    await page.keyboard.press('ArrowLeft');
    await page.waitForTimeout(300);
    
    // Verify we're back to initial slide
    const backTitle = await page.locator('h2.gradient-text').textContent();
    expect(backTitle).toBe(initialTitle);
    
    // Press Escape to return to overview
    await page.keyboard.press('Escape');
    
    // Verify we're back in overview mode
    await page.waitForSelector('[data-testid="add-slide-button"]');
    await expect(page.locator('[data-testid="slide-thumbnail-0"]')).toBeVisible();
  });

  test('wizard should maintain context across slide navigation', async ({ page }) => {
    // Create a new presentation
    const name = `Context Maintain Test ${Date.now()}`;
    const topic = 'Test Topic for Context';
    const id = await createPresentation(page, name, topic);
    
    // Complete research and generate slides
    const [researchResponse] = await Promise.all([
      page.waitForResponse(resp => resp.url().includes(`/presentations/${id}/steps/research/run`) && resp.status() === 200),
      page.getByTestId('start-ai-research-button').click()
    ]);
    await page.waitForSelector('[data-testid="ai-research-content"]', { state: 'visible', timeout: 30000 });
    await page.getByTestId('step-nav-slides').click();
    await page.waitForLoadState('networkidle');
    
    const runSlidesButton = page.getByTestId('run-slides-button');
    if (await runSlidesButton.count() > 0) {
      await runSlidesButton.click();
    }
    
    // Wait for slides
    await page.waitForSelector('[data-testid="slide-thumbnail-0"]', { timeout: 30000 });
    
    // Click on second slide
    await page.click('[data-testid="slide-thumbnail-1"]');
    await page.waitForSelector('[data-testid="back-to-overview-button"]');
    
    // Send a message to wizard
    const wizardTextarea = page.locator('textarea').first();
    await wizardTextarea.fill('Can you help improve this slide?');
    
    const sendButton = page.locator('button:has-text("Send")');
    await sendButton.click();
    
    // Wait for wizard to start processing
    await page.waitForSelector('text=/Processing|Thinking|Generating/', { timeout: 5000 }).catch(() => {
      // If no processing message, that's okay - the response might be instant in test mode
    });
    
    // Navigate to next slide with arrow key
    await page.keyboard.press('ArrowRight');
    await page.waitForTimeout(300);
    
    // Verify wizard is still visible and functional
    const wizardCard = page.locator('.card').filter({ hasText: 'AI Presentation Wizard' });
    await expect(wizardCard).toBeVisible();
    
    // Navigate back
    await page.keyboard.press('ArrowLeft');
    await page.waitForTimeout(300);
    
    // Wizard should still be there with conversation history
    await expect(wizardCard).toBeVisible();
    await expect(wizardTextarea).toBeVisible();
  });
});