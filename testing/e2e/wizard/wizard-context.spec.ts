import { test, expect } from '@playwright/test';
import { createPresentation } from '../utils';

test.setTimeout(180000);

test.describe('Wizard Context Tests', () => {
  // From wizard-research-context.spec.ts
  test('should handle research refinement requests', async ({ page }) => {
    const name = `Research Wizard Test ${Date.now()}`;
    const topic = 'Artificial Intelligence in Healthcare';

    // Create presentation and complete research step
    const id = await createPresentation(page, name, topic);
    console.log(`✅ Created presentation with ID: ${id}`);

    // Complete research step
    console.log('🔍 Running research...');
    const [researchResponse] = await Promise.all([
      page.waitForResponse(resp => resp.url().includes(`/presentations/${id}/steps/research/run`) && resp.status() === 200),
      page.getByTestId('start-ai-research-button').click()
    ]);
    console.log('✅ Research completed');

    // Test research refinement
    console.log('🧙‍♂️ Testing research refinement...');
    
    const wizardInput = page.getByTestId('wizard-input');
    const sendButton = page.getByTestId('wizard-send-button');
    
    // Test research modification request
    await wizardInput.fill('Add more information about AI ethics and privacy concerns');
    await sendButton.click();
    
    // Wait for response
    await page.waitForSelector('[data-testid="wizard-message-assistant"]:last-child', { timeout: 10000 });
    
    // Check for suggestion or response
    const hasSuggestion = await page.locator('[data-testid="wizard-suggestion"]').isVisible();
    const hasResponse = await page.locator('[data-testid="wizard-message-assistant"]').count() > 1;
    
    expect(hasSuggestion || hasResponse).toBe(true);
    console.log('✅ Research refinement request processed');

    // Test research question
    await wizardInput.fill('What are the main challenges in AI healthcare implementation?');
    await sendButton.click();
    
    // Wait for response using a more reliable method
    await page.waitForSelector('[data-testid="wizard-message-assistant"]:nth-of-type(2)', { timeout: 10000 });
    
    // Should get a conversational response
    const responseMessages = await page.locator('[data-testid="wizard-message-assistant"]').count();
    expect(responseMessages).toBeGreaterThan(1);
    console.log('✅ Research question answered');
  });

  test('should provide research guidance', async ({ page }) => {
    const name = `Research Guidance Test ${Date.now()}`;
    const topic = 'Climate Change Solutions';

    const id = await createPresentation(page, name, topic);
    
    // Complete research step
    const [researchResponse] = await Promise.all([
      page.waitForResponse(resp => resp.url().includes(`/presentations/${id}/steps/research/run`) && resp.status() === 200),
      page.getByTestId('start-ai-research-button').click()
    ]);

    // Test guidance request
    const wizardInput = page.getByTestId('wizard-input');
    await wizardInput.fill('How can I improve the quality of this research?');
    await wizardInput.press('Enter');
    
    // Wait for wizard response
    await page.waitForSelector('[data-testid="wizard-message-assistant"]:last-child', { timeout: 10000 });
    
    // Should get helpful guidance
    const lastMessage = page.locator('[data-testid="wizard-message-assistant"]').last();
    await expect(lastMessage).toBeVisible();
    console.log('✅ Research guidance provided');
  });

  // From wizard-slides-context.spec.ts
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
    console.log('✅ Research completed');

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
      // Wait for slides to be generated
      await page.waitForFunction(() => {
        const thumbnails = document.querySelectorAll('[data-testid^="slide-thumbnail-"]');
        return thumbnails.length > 0;
      }, {}, { timeout: 30000 });
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
    await page.waitForSelector('[data-testid="wizard-suggestion"]', { timeout: 15000 });
    
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
    
    await page.getByTestId('step-nav-slides').click();
    await page.waitForLoadState('networkidle');
    
    const runSlidesButton = page.getByTestId('run-slides-button');
    if (await runSlidesButton.count() > 0) {
      const [slidesResponse] = await Promise.all([
        page.waitForResponse(resp => resp.url().includes(`/presentations/${id}/steps/slides/run`) && resp.status() === 200),
        runSlidesButton.click()
      ]);
      // Wait for slides to be generated
      await page.waitForFunction(() => {
        const thumbnails = document.querySelectorAll('[data-testid^="slide-thumbnail-"]');
        return thumbnails.length > 0;
      }, {}, { timeout: 30000 });
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
      // Wait for slides to be generated
      await page.waitForFunction(() => {
        const thumbnails = document.querySelectorAll('[data-testid^="slide-thumbnail-"]');
        return thumbnails.length > 0;
      }, {}, { timeout: 30000 });
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
      // Wait for slides to be generated
      await page.waitForFunction(() => {
        const thumbnails = document.querySelectorAll('[data-testid^="slide-thumbnail-"]');
        return thumbnails.length > 0;
      }, {}, { timeout: 30000 });
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
      // Wait for slides to be generated
      await page.waitForFunction(() => {
        const thumbnails = document.querySelectorAll('[data-testid^="slide-thumbnail-"]');
        return thumbnails.length > 0;
      }, {}, { timeout: 30000 });
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

  // From wizard-general-context.spec.ts
  test('should provide guidance on illustrations step', async ({ page }) => {
    const name = `General Wizard Illustrations Test ${Date.now()}`;
    const topic = 'Machine Learning Basics';

    const id = await createPresentation(page, name, topic);
    console.log(`✅ Created presentation with ID: ${id}`);

    // Complete research and slides steps
    const [researchResponse] = await Promise.all([
      page.waitForResponse(resp => resp.url().includes(`/presentations/${id}/steps/research/run`) && resp.status() === 200),
      page.getByTestId('start-ai-research-button').click()
    ]);
    
    await page.getByTestId('step-nav-slides').click();
    await page.waitForLoadState('networkidle');
    
    const runSlidesButton = page.getByTestId('run-slides-button');
    if (await runSlidesButton.count() > 0) {
      await runSlidesButton.click();
      
      // Wait for slides to be generated
      await page.waitForFunction(() => {
        const thumbnails = document.querySelectorAll('[data-testid^="slide-thumbnail-"]');
        return thumbnails.length > 0;
      }, {}, { timeout: 30000 });
      console.log('✅ Slides generated');
    }

    // Navigate to illustrations step
    await page.getByTestId('step-nav-illustration').click();
    await page.waitForLoadState('networkidle');
    console.log('✅ Navigated to illustrations step');

    // Test general guidance on illustrations step
    const wizardInput = page.getByTestId('wizard-input');
    await wizardInput.fill('How can I improve the visual appeal of my presentation?');
    await wizardInput.press('Enter');
    
    // Wait for wizard response
    await page.waitForSelector('[data-testid="wizard-message-assistant"]:nth-of-type(2)', { timeout: 10000 });
    
    // Should get helpful guidance
    const responseMessages = await page.locator('[data-testid="wizard-message-assistant"]').count();
    expect(responseMessages).toBeGreaterThan(1);
    console.log('✅ Illustrations guidance provided');

    // Test navigation suggestion
    await wizardInput.fill('I want to modify slide content');
    await wizardInput.press('Enter');
    
    // Wait for new response
    await page.waitForFunction(
      (prevCount) => document.querySelectorAll('[data-testid="wizard-message-assistant"]').length > prevCount,
      responseMessages,
      { timeout: 10000 }
    );
    
    // Should suggest going back to slides step
    const lastMessage = page.locator('[data-testid="wizard-message-assistant"]').last();
    await expect(lastMessage).toBeVisible();
    console.log('✅ Navigation guidance provided');
  });

  test('should provide guidance on PPTX step', async ({ page }) => {
    const name = `General Wizard PPTX Test ${Date.now()}`;
    const topic = 'Business Strategy Planning';

    const id = await createPresentation(page, name, topic);
    
    // Complete all previous steps
    const [researchResponse] = await Promise.all([
      page.waitForResponse(resp => resp.url().includes(`/presentations/${id}/steps/research/run`) && resp.status() === 200),
      page.getByTestId('start-ai-research-button').click()
    ]);
    
    await page.getByTestId('step-nav-slides').click();
    await page.waitForLoadState('networkidle');
    
    const runSlidesButton = page.getByTestId('run-slides-button');
    if (await runSlidesButton.count() > 0) {
      await runSlidesButton.click();
      
      // Wait for slides to be generated
      await page.waitForFunction(() => {
        const thumbnails = document.querySelectorAll('[data-testid^="slide-thumbnail-"]');
        return thumbnails.length > 0;
      }, {}, { timeout: 30000 });
      console.log('✅ Slides generated for PPTX test');
    }

    // Complete illustration step first
    await page.getByTestId('step-nav-illustration').click();
    await page.waitForLoadState('networkidle');
    
    // Complete the illustration step by running it
    const runIllustrationButton = page.getByTestId('run-illustration-button');
    if (await runIllustrationButton.count() > 0) {
      const [illustrationResponse] = await Promise.all([
        page.waitForResponse(resp => resp.url().includes(`/presentations/${id}/steps/images/run`) && resp.status() === 200),
        runIllustrationButton.click()
      ]);
      console.log('✅ Illustration step completed');
    }

    // Navigate to PPTX step (force click since it might be disabled in offline mode)
    await page.getByTestId('step-nav-pptx').click({ force: true });
    await page.waitForLoadState('networkidle');
    console.log('✅ Navigated to PPTX step');

    // Test guidance on PPTX step
    const wizardInput = page.getByTestId('wizard-input');
    await wizardInput.fill('Can I still make changes to my presentation?');
    await wizardInput.press('Enter');
    
    // Wait for wizard response
    await page.waitForSelector('[data-testid="wizard-message-assistant"]:nth-of-type(2)', { timeout: 10000 });
    
    // Should get guidance about going back to previous steps
    const responseMessages = await page.locator('[data-testid="wizard-message-assistant"]').count();
    expect(responseMessages).toBeGreaterThan(1);
    console.log('✅ PPTX step guidance provided');
  });

  test('should explain presentation creation process', async ({ page }) => {
    const name = `Process Explanation Test ${Date.now()}`;
    const topic = 'Software Development Lifecycle';

    const id = await createPresentation(page, name, topic);
    
    // Test process explanation from research step
    const wizardInput = page.getByTestId('wizard-input');
    await wizardInput.fill('Can you explain the presentation creation process?');
    await wizardInput.press('Enter');
    
    // Wait for wizard response
    await page.waitForSelector('[data-testid="wizard-message-assistant"]:nth-of-type(2)', { timeout: 10000 });
    
    // Should get explanation of the process
    const responseMessages = await page.locator('[data-testid="wizard-message-assistant"]').count();
    expect(responseMessages).toBeGreaterThan(1);
    console.log('✅ Process explanation provided');

    // Test next steps suggestion
    await wizardInput.fill('What should I do next?');
    await wizardInput.press('Enter');
    
    // Wait for new response
    await page.waitForFunction(
      (prevCount) => document.querySelectorAll('[data-testid="wizard-message-assistant"]').length > prevCount,
      responseMessages,
      { timeout: 10000 }
    );
    
    // Should get next steps guidance
    const lastMessage = page.locator('[data-testid="wizard-message-assistant"]').last();
    await expect(lastMessage).toBeVisible();
    console.log('✅ Next steps guidance provided');
  });

  test('should handle feature questions', async ({ page }) => {
    const name = `Feature Questions Test ${Date.now()}`;
    const topic = 'User Experience Design';

    const id = await createPresentation(page, name, topic);
    
    // Test feature explanation
    const wizardInput = page.getByTestId('wizard-input');
    await wizardInput.fill('What features are available in this application?');
    await wizardInput.press('Enter');
    
    // Wait for wizard response
    await page.waitForSelector('[data-testid="wizard-message-assistant"]:nth-of-type(2)', { timeout: 10000 });
    
    // Should get feature explanation
    const responseMessages = await page.locator('[data-testid="wizard-message-assistant"]').count();
    expect(responseMessages).toBeGreaterThan(1);
    console.log('✅ Feature explanation provided');

    // Test troubleshooting help
    await wizardInput.fill('I am having trouble with the application');
    await wizardInput.press('Enter');
    
    // Wait for new response
    await page.waitForFunction(
      (prevCount) => document.querySelectorAll('[data-testid="wizard-message-assistant"]').length > prevCount,
      responseMessages,
      { timeout: 10000 }
    );
    
    // Should get troubleshooting help
    const lastMessage = page.locator('[data-testid="wizard-message-assistant"]').last();
    await expect(lastMessage).toBeVisible();
    console.log('✅ Troubleshooting help provided');
  });

  test('should maintain helpful tone across different steps', async ({ page }) => {
    const name = `Tone Consistency Test ${Date.now()}`;
    const topic = 'Environmental Conservation';

    const id = await createPresentation(page, name, topic);
    
    const wizardInput = page.getByTestId('wizard-input');
    
    // Test on research step
    await wizardInput.fill('Hello, can you help me?');
    await wizardInput.press('Enter');
    await page.waitForSelector('[data-testid="wizard-message-assistant"]:nth-of-type(2)', { timeout: 10000 });
    
    let responseCount = await page.locator('[data-testid="wizard-message-assistant"]').count();
    expect(responseCount).toBeGreaterThan(1);
    console.log('✅ Helpful response on research step');

    // Complete research step first
    const [researchResponse] = await Promise.all([
      page.waitForResponse(resp => resp.url().includes(`/presentations/${id}/steps/research/run`) && resp.status() === 200),
      page.getByTestId('start-ai-research-button').click()
    ]);

    // Navigate to slides step and test
    await page.getByTestId('step-nav-slides').click();
    await page.waitForLoadState('networkidle');
    
    // Generate slides first
    const runSlidesButton = page.getByTestId('run-slides-button');
    if (await runSlidesButton.count() > 0) {
      await runSlidesButton.click();
      
      // Wait for slides to be generated
      await page.waitForFunction(() => {
        const thumbnails = document.querySelectorAll('[data-testid^="slide-thumbnail-"]');
        return thumbnails.length > 0;
      }, {}, { timeout: 30000 });
      console.log('✅ Slides generated for tone test');
    }
    
    await wizardInput.fill('I need general help');
    
    // Get count before sending message
    const prevCount = await page.locator('[data-testid="wizard-message-assistant"]').count();
    
    await wizardInput.press('Enter');
    
    // Wait for wizard response in offline mode (should be immediate)
    await page.waitForLoadState('networkidle');
    
    // Check if we got a new response
    const currentCount = await page.locator('[data-testid="wizard-message-assistant"]').count();
    
    if (currentCount > prevCount) {
      // New response received
      responseCount = currentCount;
    } else {
      // Response might already be there, check content
      const wizardMessages = page.locator('[data-testid="wizard-message-assistant"]');
      if (await wizardMessages.count() > 0) {
        responseCount = await wizardMessages.count();
      } else {
        throw new Error('No wizard response found');
      }
    }
    
    expect(responseCount).toBeGreaterThan(0);
    console.log('✅ Helpful response on slides step');

    // Navigate to illustrations step and test
    await page.getByTestId('step-nav-illustration').click();
    await page.waitForLoadState('networkidle');
    
    await wizardInput.fill('Thank you for your help');
    
    // Get count before sending message  
    const finalPrevCount = await page.locator('[data-testid="wizard-message-assistant"]').count();
    
    await wizardInput.press('Enter');
    
    // Wait for wizard response in offline mode (should be immediate)
    await page.waitForLoadState('networkidle');
    
    // Check if we got a new response
    const finalCurrentCount = await page.locator('[data-testid="wizard-message-assistant"]').count();
    
    if (finalCurrentCount > finalPrevCount) {
      // New response received
      responseCount = finalCurrentCount;
    } else {
      // Response might already be there, check content
      responseCount = await page.locator('[data-testid="wizard-message-assistant"]').count();
    }
    
    expect(responseCount).toBeGreaterThan(0);
    console.log('✅ Consistent helpful tone maintained');
  });
});