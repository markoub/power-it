import { test, expect } from '@playwright/test';
import { createPresentation, getApiUrl } from '../utils';

test.describe('Step States and Synchronization', () => {
  test.setTimeout(60000);

  test('step states should show pending, processing, and completed correctly', async ({ page }) => {
    const name = `Step States Test ${Date.now()}`;
    const topic = 'Test topic for step states';

    // Create presentation
    const presentationId = await createPresentation(page, name, topic);
    const apiUrl = getApiUrl();

    // Check initial backend step statuses
    const initialResponse = await page.request.get(`${apiUrl}/presentations/${presentationId}`);
    const initialData = await initialResponse.json();
    
    console.log('Initial backend step statuses:');
    initialData.steps?.forEach((step: any) => {
      console.log(`  ${step.step}: ${step.status}`);
    });

    // Verify initial UI states - all steps except research should be pending (grey/muted)
    const slidesStep = page.getByTestId('step-nav-slides');
    const slidesStepClass = await slidesStep.getAttribute('class');
    const slidesHasMutedBg = slidesStepClass?.includes('bg-muted');
    expect(slidesHasMutedBg).toBe(true);

    // Start AI research
    await page.getByTestId('start-ai-research-button').click();

    // Wait for research to complete
    await expect(page.getByTestId('ai-research-content')).toBeVisible({ timeout: 30000 });

    // Verify research step shows completed (check icon)
    const researchStep = page.getByTestId('step-nav-research');
    const hasCheckIcon = await researchStep.locator('[data-lucide="check-circle-2"]').count() > 0;
    expect(hasCheckIcon).toBe(true);

    // Verify backend and frontend are synchronized
    const afterResearchResponse = await page.request.get(`${apiUrl}/presentations/${presentationId}`);
    const afterResearchData = await afterResearchResponse.json();
    const researchStepData = afterResearchData.steps?.find((s: any) => s.step === 'research');
    expect(researchStepData?.status).toBe('completed');

    // Navigate to slides and verify it's enabled
    await slidesStep.click();
    await expect(slidesStep).toBeEnabled();
    await expect(page.getByTestId('run-slides-button')).toBeVisible();

    // Generate slides
    await page.getByTestId('run-slides-button').click();
    
    // Wait for slides to complete
    await page.waitForSelector('[data-testid^="slide-thumbnail-"]', { timeout: 30000 });

    // Verify slides step shows completed
    const slidesHasCheck = await slidesStep.locator('[data-lucide="check-circle-2"]').count() > 0;
    expect(slidesHasCheck).toBe(true);

    // Verify subsequent steps are enabled/disabled correctly
    const imagesStep = page.getByTestId('step-nav-illustration');
    const compiledStep = page.getByTestId('step-nav-compiled');
    const pptxStep = page.getByTestId('step-nav-pptx');

    // Images should be available (blue background)
    const imagesClass = await imagesStep.getAttribute('class');
    expect(imagesClass).toContain('bg-blue-500');

    // Compiled and PPTX should still be pending (muted background)
    const compiledClass = await compiledStep.getAttribute('class');
    const pptxClass = await pptxStep.getAttribute('class');
    expect(compiledClass).toContain('bg-muted');
    expect(pptxClass).toContain('bg-muted');
  });

  test('navigation between steps should work correctly', async ({ page }) => {
    const name = `Navigation Test ${Date.now()}`;
    const topic = 'Test step navigation';

    // Create presentation and complete research
    const presentationId = await createPresentation(page, name, topic);
    await page.getByTestId('start-ai-research-button').click();
    await expect(page.getByTestId('ai-research-content')).toBeVisible({ timeout: 30000 });

    // Navigate to slides
    await page.getByTestId('step-nav-slides').click();
    // Verify we're on slides step by checking for the run button
    await expect(page.getByTestId('run-slides-button')).toBeVisible();

    // Navigate back to research
    await page.getByTestId('step-nav-research').click();
    // Verify we're back on research by checking for the content
    await expect(page.getByTestId('ai-research-content')).toBeVisible();

    // Try to navigate to disabled step (should not work)
    const pptxStep = page.getByTestId('step-nav-pptx');
    await expect(pptxStep).toBeDisabled();
    
    // Clicking disabled step should not change URL
    const urlBefore = page.url();
    await pptxStep.click({ force: true });
    const urlAfter = page.url();
    expect(urlAfter).toBe(urlBefore);
  });

  test('backend polling should reflect status transitions', async ({ page }) => {
    const name = `Polling Test ${Date.now()}`;
    const topic = 'Test backend polling';

    // Create presentation
    const presentationId = await createPresentation(page, name, topic);
    const apiUrl = getApiUrl();

    // Start research
    await page.getByTestId('start-ai-research-button').click();

    // Poll backend to track status transitions
    const statusTransitions: string[] = [];
    let completed = false;
    
    for (let i = 0; i < 15 && !completed; i++) {
      const response = await page.request.get(`${apiUrl}/presentations/${presentationId}`);
      if (response.ok()) {
        const data = await response.json();
        const researchStep = data.steps?.find((s: any) => s.step === 'research');
        
        if (researchStep) {
          const currentStatus = researchStep.status;
          
          // Track unique status transitions
          if (statusTransitions.length === 0 || statusTransitions[statusTransitions.length - 1] !== currentStatus) {
            statusTransitions.push(currentStatus);
          }
          
          if (currentStatus === 'completed') {
            completed = true;
          }
        }
      }
      
      if (!completed) {
        await page.waitForTimeout(1000);
      }
    }

    // Should have transitioned through states
    expect(statusTransitions).toContain('completed');
    
    // UI should also show completion
    await expect(page.getByTestId('ai-research-content')).toBeVisible();
  });

  test('step completion should enable next steps progressively', async ({ page }) => {
    const name = `Progressive Enable Test ${Date.now()}`;
    const topic = 'Test progressive step enabling';

    // Create presentation
    const presentationId = await createPresentation(page, name, topic);

    // Initially verify step states
    const steps = [
      { id: 'step-nav-research', shouldBeEnabled: true },
      { id: 'step-nav-slides', shouldBeEnabled: false },
      { id: 'step-nav-illustration', shouldBeEnabled: false },
      { id: 'step-nav-compiled', shouldBeEnabled: false },
      { id: 'step-nav-pptx', shouldBeEnabled: false }
    ];

    for (const step of steps) {
      const element = page.getByTestId(step.id);
      if (step.shouldBeEnabled) {
        await expect(element).toBeEnabled();
      } else {
        await expect(element).toBeDisabled();
      }
    }

    // Complete research
    await page.getByTestId('start-ai-research-button').click();
    await expect(page.getByTestId('ai-research-content')).toBeVisible({ timeout: 30000 });

    // Now slides should be enabled
    await expect(page.getByTestId('step-nav-slides')).toBeEnabled();

    // Complete slides
    await page.getByTestId('step-nav-slides').click();
    await page.getByTestId('run-slides-button').click();
    await page.waitForSelector('[data-testid^="slide-thumbnail-"]', { timeout: 30000 });

    // Now illustration should be enabled
    await expect(page.getByTestId('step-nav-illustration')).toBeEnabled();
    
    // But compiled and pptx should still be disabled
    await expect(page.getByTestId('step-nav-compiled')).toBeDisabled();
    await expect(page.getByTestId('step-nav-pptx')).toBeDisabled();
  });
});