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

    // Initially should be in overview mode with "All Slides" context
    const wizardHeader = page.locator('[data-testid="wizard-header"]').first();
    await expect(wizardHeader).toContainText('All Slides');
    console.log('✅ Initial context: All Slides (Overview mode)');

    // Select first slide for single slide context
    const firstSlide = page.getByTestId('slide-thumbnail-0');
    await expect(firstSlide).toBeVisible({ timeout: 10000 });
    await firstSlide.click();
    console.log('✅ Selected first slide');

    // Verify context changed to single slide
    await expect(wizardHeader).toContainText('Single Slide');
    console.log('✅ Wizard context updated to single slide');

    // Verify back to overview button is visible
    const backButton = page.getByTestId('back-to-overview-button');
    await expect(backButton).toBeVisible();
    console.log('✅ Back to overview button is visible');

    // Test single slide modification
    console.log('🧙‍♂️ Testing single slide modification...');
    
    const wizardInput = page.getByTestId('wizard-input');
    await wizardInput.fill('Make this slide more engaging and add bullet points');
    await wizardInput.press('Enter');
    
    // Wait for suggestion to be generated
    await page.waitForTimeout(10000);
    
    // Check if suggestion was generated
    const suggestionBox = page.locator('[data-testid="wizard-suggestion"]');
    await expect(suggestionBox).toBeVisible();
    console.log('✅ Single slide suggestion generated');
    
    const applyButton = page.locator('[data-testid="wizard-apply-button"]');
    await expect(applyButton).toBeVisible();
    
    // Wait for the apply button to become enabled (hasChanges() might need time to detect changes)
    await expect(applyButton).toBeEnabled({ timeout: 10000 });
    await applyButton.click();
    
    // Verify suggestion disappeared
    await expect(suggestionBox).not.toBeVisible();
    console.log('✅ Single slide modification applied');

    // Test back to overview functionality
    await backButton.click();
    await page.waitForTimeout(1000);
    
    // Verify context changed back to all slides
    await expect(wizardHeader).toContainText('All Slides');
    console.log('✅ Context switched back to: All Slides (Overview mode)');
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

    // Should start in overview mode
    const wizardHeader = page.locator('[data-testid="wizard-header"]').first();
    await expect(wizardHeader).toContainText('All Slides');
    console.log('✅ Starting in overview mode');

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
    
    // Initially should be "All Slides" context (overview mode)
    await expect(wizardHeader).toContainText('All Slides');
    console.log('✅ Initial context: All Slides (Overview mode)');

    // Verify we're in overview mode by checking for overview-specific elements
    // Wait for slides to be generated and overview to be visible
    await expect(page.locator('h2').filter({ hasText: 'Slides Overview' })).toBeVisible({ timeout: 10000 });
    console.log('✅ Confirmed in overview mode');

    // Select a slide to switch to single slide context
    const firstSlide = page.getByTestId('slide-thumbnail-0');
    await expect(firstSlide).toBeVisible({ timeout: 10000 });
    await firstSlide.click();
    
    // Context should change to single slide
    await expect(wizardHeader).toContainText('Single Slide');
    console.log('✅ Context switched to: Single Slide');

    // Verify we're in single slide mode by checking for single slide-specific elements
    const backButton = page.getByTestId('back-to-overview-button');
    await expect(backButton).toBeVisible();
    console.log('✅ Confirmed in single slide mode');

    // Verify horizontal thumbnails are visible in single slide mode
    const horizontalThumbnail = page.getByTestId('slide-thumbnail-horizontal-0');
    await expect(horizontalThumbnail).toBeVisible();
    console.log('✅ Horizontal thumbnails visible in single slide mode');

    // Click back to overview button to return to overview mode
    await backButton.click();
    await page.waitForTimeout(1000);
    
    // Verify context changed back to all slides
    await expect(wizardHeader).toContainText('All Slides');
    console.log('✅ Context switched back to: All Slides (Overview mode)');

    // Verify we're back in overview mode
    await expect(page.locator('h2').filter({ hasText: 'Slides Overview' })).toBeVisible();
    console.log('✅ Confirmed back in overview mode');
  });

  test('should handle navigation between slides in single slide mode', async ({ page }) => {
    const name = `Slide Navigation Test ${Date.now()}`;
    const topic = 'Technology Innovation';

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

    // Select first slide
    const firstSlide = page.getByTestId('slide-thumbnail-0');
    await expect(firstSlide).toBeVisible({ timeout: 10000 });
    await firstSlide.click();
    console.log('✅ Selected first slide');

    // Verify we're in single slide mode
    const wizardHeader = page.locator('[data-testid="wizard-header"]').first();
    await expect(wizardHeader).toContainText('Single Slide');

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

      // Verify the second slide is now highlighted in horizontal thumbnails
      const secondSlideHighlighted = page.locator('[data-testid="slide-thumbnail-horizontal-1"]');
      await expect(secondSlideHighlighted).toHaveClass(/ring-2 ring-primary-500/);
      console.log('✅ Second slide is highlighted in horizontal thumbnails');
    }

    console.log('✅ Slide navigation test completed');
  });
}); 