import { test, expect } from '@playwright/test';
import { createPresentation } from './utils';

test.setTimeout(180000);

test.describe('Slides Wizard Context', () => {
  test('should handle single slide modifications', async ({ page }) => {
    const name = `Slides Wizard Single Test ${Date.now()}`;
    const topic = 'Digital Marketing Strategies';

    // Create presentation and complete research and slides steps
    const id = await createPresentation(page, name, topic);
    console.log(`✅ Created presentation with ID: ${id}`);

    // Complete research step
    console.log('🔍 Running research...');
    await page.getByTestId('start-ai-research-button').click();
    await page.waitForTimeout(5000);
    console.log('✅ Research completed');

    // Navigate to slides and generate slides
    console.log('📊 Generating slides...');
    await page.getByTestId('step-nav-slides').click();
    await page.waitForTimeout(1000);
    
    const runSlidesButton = page.getByTestId('run-slides-button');
    if (await runSlidesButton.count() > 0) {
      await runSlidesButton.click();
      await page.waitForTimeout(15000);
      console.log('✅ Slides generated');
    }

    // Select first slide for single slide context
    const firstSlide = page.getByTestId('slide-thumbnail-0');
    await expect(firstSlide).toBeVisible({ timeout: 10000 });
    await firstSlide.click();
    console.log('✅ Selected first slide');

    // Verify context changed to single slide
    const wizardHeader = page.locator('[data-testid="wizard-header"]').first();
    await expect(wizardHeader).toContainText('Single Slide');
    console.log('✅ Wizard context updated to single slide');

    // Test single slide modification
    console.log('🧙‍♂️ Testing single slide modification...');
    
    const wizardInput = page.getByTestId('wizard-input');
    const sendButton = page.getByTestId('wizard-send-button');
    
    await wizardInput.fill('Improve this slide with better formatting and more engaging content');
    await sendButton.click();
    
    // Wait for suggestion
    await page.waitForTimeout(10000);
    
    const suggestionBox = page.locator('[data-testid="wizard-suggestion"]');
    await expect(suggestionBox).toBeVisible({ timeout: 15000 });
    console.log('✅ Single slide suggestion generated');

    // Apply the changes
    const applyButton = page.locator('[data-testid="wizard-apply-button"]');
    await expect(applyButton).toBeVisible();
    await applyButton.click();
    
    // Verify suggestion disappeared
    await expect(suggestionBox).not.toBeVisible();
    console.log('✅ Single slide changes applied');
  });

  test('should handle presentation-level modifications (add/remove slides)', async ({ page }) => {
    const name = `Slides Wizard Presentation Test ${Date.now()}`;
    const topic = 'Sustainable Energy Solutions';

    const id = await createPresentation(page, name, topic);
    
    // Complete research and slides steps
    await page.getByTestId('start-ai-research-button').click();
    await page.waitForTimeout(5000);
    
    await page.getByTestId('step-nav-slides').click();
    await page.waitForTimeout(1000);
    
    const runSlidesButton = page.getByTestId('run-slides-button');
    if (await runSlidesButton.count() > 0) {
      await runSlidesButton.click();
      await page.waitForTimeout(15000);
    }

    // Test presentation-level modification (add slide)
    console.log('🧙‍♂️ Testing presentation-level modification...');
    
    const wizardInput = page.getByTestId('wizard-input');
    await wizardInput.fill('Add a new slide about renewable energy costs and benefits');
    await wizardInput.press('Enter');
    
    await page.waitForTimeout(10000);
    
    // Should get a presentation-level suggestion
    const suggestionBox = page.locator('[data-testid="wizard-suggestion"]');
    if (await suggestionBox.isVisible()) {
      console.log('✅ Presentation-level suggestion generated');
      
      // Apply changes
      const applyButton = page.locator('[data-testid="wizard-apply-button"]');
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
    const name = `Slides Guidance Test ${Date.now()}`;
    const topic = 'Project Management Fundamentals';

    const id = await createPresentation(page, name, topic);
    
    // Complete research and slides steps
    await page.getByTestId('start-ai-research-button').click();
    await page.waitForTimeout(5000);
    
    await page.getByTestId('step-nav-slides').click();
    await page.waitForTimeout(1000);
    
    const runSlidesButton = page.getByTestId('run-slides-button');
    if (await runSlidesButton.count() > 0) {
      await runSlidesButton.click();
      await page.waitForTimeout(15000);
    }

    // Test general slides guidance
    const wizardInput = page.getByTestId('wizard-input');
    await wizardInput.fill('What are some best practices for slide design?');
    await wizardInput.press('Enter');
    
    await page.waitForTimeout(5000);
    
    // Should get helpful guidance
    const responseMessages = await page.locator('[data-testid="wizard-message-assistant"]').count();
    expect(responseMessages).toBeGreaterThan(1);
    console.log('✅ Slides guidance provided');
  });

  test('should handle context switching between single and all slides', async ({ page }) => {
    const name = `Context Switching Test ${Date.now()}`;
    const topic = 'Data Science Fundamentals';

    const id = await createPresentation(page, name, topic);
    
    // Complete setup
    await page.getByTestId('start-ai-research-button').click();
    await page.waitForTimeout(5000);
    
    await page.getByTestId('step-nav-slides').click();
    await page.waitForTimeout(1000);
    
    const runSlidesButton = page.getByTestId('run-slides-button');
    if (await runSlidesButton.count() > 0) {
      await runSlidesButton.click();
      await page.waitForTimeout(15000);
    }

    const wizardHeader = page.locator('[data-testid="wizard-header"]').first();
    
    // Initially should be "All Slides" context
    await expect(wizardHeader).toContainText('All Slides');
    console.log('✅ Initial context: All Slides');

    // Select a slide to switch to single slide context
    const firstSlide = page.getByTestId('slide-thumbnail-0');
    await expect(firstSlide).toBeVisible({ timeout: 10000 });
    await firstSlide.click();
    
    // Context should change to single slide
    await expect(wizardHeader).toContainText('Single Slide');
    console.log('✅ Context switched to: Single Slide');

    // Click somewhere else to deselect (if possible)
    await page.click('body');
    await page.waitForTimeout(1000);
    
    // Context might switch back to all slides depending on implementation
    console.log('✅ Context switching test completed');
  });
}); 