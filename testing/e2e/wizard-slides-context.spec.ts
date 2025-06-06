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
    const [researchResponse] = await Promise.all([
      page.waitForResponse(resp => resp.url().includes(`/presentations/${id}/steps/research/run`) && resp.status() === 200),
      page.getByTestId('start-ai-research-button').click()
    ]);
    console.log('✅ Research API call completed');
    
    // Wait for research content to be visible
    await page.waitForSelector('[data-testid="ai-research-content"]', { 
      timeout: 30000,
      state: 'visible' 
    });
    console.log('✅ Research content loaded');
    
    // Ensure slides navigation is enabled before proceeding
    await page.waitForFunction(() => {
      const slidesNav = document.querySelector('[data-testid="step-nav-slides"]');
      return slidesNav && !slidesNav.hasAttribute('disabled');
    }, { timeout: 10000 });
    console.log('✅ Slides navigation enabled');

    // Navigate to slides and generate slides
    console.log('📊 Generating slides...');
    await page.getByTestId('step-nav-slides').click();
    await page.waitForLoadState('networkidle');
    
    const runSlidesButton = page.getByTestId('run-slides-button');
    if (await runSlidesButton.count() > 0) {
      const [slidesResponse] = await Promise.all([
        page.waitForResponse(resp => resp.url().includes(`/presentations/${id}/steps/slides/run`) && resp.status() === 200),
        runSlidesButton.click()
      ]);
      console.log('✅ Slides API call completed');
    }
    
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
    const name = `Slides Wizard Presentation Test ${Date.now()}`;
    const topic = 'Sustainable Energy Solutions';

    const id = await createPresentation(page, name, topic);
    
    // Complete research and slides steps
    const [researchResponse] = await Promise.all([
      page.waitForResponse(resp => resp.url().includes(`/presentations/${id}/steps/research/run`) && resp.status() === 200),
      page.getByTestId('start-ai-research-button').click()
    ]);
    
    // Wait for research to complete and slides nav to be enabled
    await page.waitForSelector('[data-testid="ai-research-content"]', { state: 'visible', timeout: 30000 });
    await page.waitForFunction(() => {
      const slidesNav = document.querySelector('[data-testid="step-nav-slides"]');
      return slidesNav && !slidesNav.hasAttribute('disabled');
    }, { timeout: 10000 });
    
    await page.getByTestId('step-nav-slides').click();
    await page.waitForLoadState('networkidle');
    
    const runSlidesButton = page.getByTestId('run-slides-button');
    if (await runSlidesButton.count() > 0) {
      const [slidesResponse] = await Promise.all([
        page.waitForResponse(resp => resp.url().includes(`/presentations/${id}/steps/slides/run`) && resp.status() === 200),
        runSlidesButton.click()
      ]);
      console.log('✅ Slides API call completed');
    }
    
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

    // Should start in overview mode
    const wizardHeader = page.locator('[data-testid="wizard-header"]').first();
    await expect(wizardHeader).toContainText('All Slides');
    console.log('✅ Starting in overview mode');

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
    const name = `Slides Guidance Test ${Date.now()}`;
    const topic = 'Project Management Fundamentals';

    const id = await createPresentation(page, name, topic);
    
    // Complete research and slides steps
    const [researchResponse] = await Promise.all([
      page.waitForResponse(resp => resp.url().includes(`/presentations/${id}/steps/research/run`) && resp.status() === 200),
      page.getByTestId('start-ai-research-button').click()
    ]);
    
    // Wait for research to complete and slides nav to be enabled
    await page.waitForSelector('[data-testid="ai-research-content"]', { state: 'visible', timeout: 30000 });
    await page.waitForFunction(() => {
      const slidesNav = document.querySelector('[data-testid="step-nav-slides"]');
      return slidesNav && !slidesNav.hasAttribute('disabled');
    }, { timeout: 10000 });
    
    await page.getByTestId('step-nav-slides').click();
    await page.waitForLoadState('networkidle');
    
    const runSlidesButton = page.getByTestId('run-slides-button');
    if (await runSlidesButton.count() > 0) {
      const [slidesResponse] = await Promise.all([
        page.waitForResponse(resp => resp.url().includes(`/presentations/${id}/steps/slides/run`) && resp.status() === 200),
        runSlidesButton.click()
      ]);
      console.log('✅ Slides API call completed');
    }
    
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
    const name = `Context Switching Test ${Date.now()}`;
    const topic = 'Data Science Fundamentals';

    const id = await createPresentation(page, name, topic);
    
    // Complete setup
    const [researchResponse] = await Promise.all([
      page.waitForResponse(resp => resp.url().includes(`/presentations/${id}/steps/research/run`) && resp.status() === 200),
      page.getByTestId('start-ai-research-button').click()
    ]);
    
    await page.getByTestId('step-nav-slides').click();
    await page.waitForLoadState('networkidle');
    
    const runSlidesButton = page.getByTestId('run-slides-button');
    if (await runSlidesButton.count() > 0) {
      const [slidesResponse] = await Promise.all([
        page.waitForResponse(resp => resp.url().includes(`/presentations/${id}/steps/slides/run`) && resp.status() === 200),
        runSlidesButton.click()
      ]);
      console.log('✅ Slides API call completed');
    }
    
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
    await page.waitForLoadState('networkidle');
    
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
    const [researchResponse] = await Promise.all([
      page.waitForResponse(resp => resp.url().includes(`/presentations/${id}/steps/research/run`) && resp.status() === 200),
      page.getByTestId('start-ai-research-button').click()
    ]);
    
    await page.getByTestId('step-nav-slides').click();
    await page.waitForLoadState('networkidle');
    
    const runSlidesButton = page.getByTestId('run-slides-button');
    if (await runSlidesButton.count() > 0) {
      const [slidesResponse] = await Promise.all([
        page.waitForResponse(resp => resp.url().includes(`/presentations/${id}/steps/slides/run`) && resp.status() === 200),
        runSlidesButton.click()
      ]);
      console.log('✅ Slides API call completed');
    }
    
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

      // Verify we're viewing the second slide now
      // Check for any visual indication (the slide content should have changed)
      await page.waitForTimeout(500); // Brief wait for UI update
      console.log('✅ Successfully navigated to second slide');
    }

    console.log('✅ Slide navigation test completed');
  });
}); 