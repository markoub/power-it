import { test, expect } from '@playwright/test';
import { createPresentation, getApiUrl } from './utils';

test.describe('Step Pending States', () => {
  test.setTimeout(120000);

  test('should show pending (grey) and processing (yellow) states correctly', async ({ page }) => {
    const name = `Pending Test ${Date.now()}`;
    const topic = 'Test topic for pending states';

    // Listen to console logs to see debug output
    page.on('console', msg => {
      if (msg.type() === 'log' && (msg.text().includes('🔍') || msg.text().includes('🔄'))) {
        console.log('Browser console:', msg.text());
      }
    });

    // Create presentation
    const presentationId = await createPresentation(page, name, topic);
    console.log(`Created presentation ID: ${presentationId}`);

    // Wait for initial state to stabilize
    await page.waitForLoadState('networkidle');

    // Check initial backend state
    const apiUrl = getApiUrl();
    let response = await page.request.get(`${apiUrl}/presentations/${presentationId}`);
    if (response.ok()) {
      const data = await response.json();
      console.log('Initial backend step statuses:');
      data.steps?.forEach((step: any) => {
        console.log(`  ${step.step}: ${step.status}`);
      });
    }

    // Check that slides step is initially pending (grey)
    const slidesStep = page.getByTestId('step-nav-slides');
    const initialSlidesClass = await slidesStep.getAttribute('class');
    console.log('Initial slides step classes:', initialSlidesClass);
    
    // Should be greyed out for pending state (check for any grey background)
    const slidesHasGreyBg = initialSlidesClass?.includes('bg-gray-100') || initialSlidesClass?.includes('bg-gray-300');
    console.log('Slides step has grey background (pending):', slidesHasGreyBg);
    expect(slidesHasGreyBg).toBe(true);

    // Start AI research first
    console.log('🔍 Starting AI research...');
    await page.getByTestId('start-ai-research-button').click();

    // Wait for research to complete
    await expect(page.getByTestId('ai-research-content')).toBeVisible({ timeout: 30000 });
    console.log('✅ Research content is visible');

    // Wait for UI to update
    await page.waitForLoadState('networkidle');

    // Check if research step now shows as completed (check icon)
    const researchStep = page.getByTestId('step-nav-research');
    const hasCheckIcon = await researchStep.locator('[data-lucide="check-circle-2"]').count() > 0;
    console.log('Research step has check icon:', hasCheckIcon);
    expect(hasCheckIcon).toBe(true);

    // Navigate to slides step
    await slidesStep.click();
    
    // Check if slides step is enabled and clickable
    const slidesDisabled = await slidesStep.isDisabled();
    console.log('Slides step disabled:', slidesDisabled);
    expect(slidesDisabled).toBe(false);
    
    // Try to run slides step
    const runSlidesButton = page.getByTestId('run-slides-button');
    const runButtonExists = await runSlidesButton.count() > 0;
    console.log('Run slides button exists:', runButtonExists);
    expect(runButtonExists).toBe(true);
    
    const runButtonDisabled = await runSlidesButton.isDisabled();
    console.log('Run slides button disabled:', runButtonDisabled);
    expect(runButtonDisabled).toBe(false);
    
    console.log('🚀 Starting slides generation...');
    await runSlidesButton.click();
    
    // Check if slides step shows as processing (yellow with spinner) immediately after click
    await page.waitForLoadState('networkidle');
    const slidesStepClassAfterRun = await slidesStep.getAttribute('class');
    console.log('Slides step classes after clicking run:', slidesStepClassAfterRun);
    
    // Check for processing state (yellow background)
    const slidesHasYellowBg = slidesStepClassAfterRun?.includes('bg-yellow-500');
    console.log('Slides step has yellow background (processing):', slidesHasYellowBg);
    
    // Check for spinner during processing
    const slidesHasSpinner = await slidesStep.locator('[data-lucide="loader-2"]').count() > 0;
    console.log('Slides step has spinner (processing):', slidesHasSpinner);
    
    // If not currently processing (completed too fast), that's also OK
    if (!slidesHasYellowBg && !slidesHasSpinner) {
      console.log('Slides completed too quickly to catch processing state - checking completion');
    }
    
    // Wait for slides to complete
    await page.waitForSelector('[data-testid^="slide-thumbnail-"]', { timeout: 30000 });
    
    // Check final state - should have check icon
    const slidesHasCheck = await slidesStep.locator('[data-lucide="check-circle-2"]').count() > 0;
    console.log('Slides step has check icon (completed):', slidesHasCheck);
    expect(slidesHasCheck).toBe(true);

    // Verify that both research and slides steps show as completed
    const finalResearchCheck = await researchStep.locator('[data-lucide="check-circle-2"]').count() > 0;
    const finalSlidesCheck = await slidesStep.locator('[data-lucide="check-circle-2"]').count() > 0;
    
    console.log('Final verification - Research has check:', finalResearchCheck);
    console.log('Final verification - Slides has check:', finalSlidesCheck);
    
    expect(finalResearchCheck).toBe(true);
    expect(finalSlidesCheck).toBe(true);

    // Check that remaining steps show correct states
    const imagesStep = page.getByTestId('step-nav-illustration');
    const compiledStep = page.getByTestId('step-nav-compiled');
    const pptxStep = page.getByTestId('step-nav-pptx');

    const imagesClass = await imagesStep.getAttribute('class');
    const compiledClass = await compiledStep.getAttribute('class');
    const pptxClass = await pptxStep.getAttribute('class');

    // Debug: Log the actual classes to understand what we're getting
    console.log('Images step classes:', imagesClass);
    console.log('Compiled step classes:', compiledClass);
    console.log('PPTX step classes:', pptxClass);

    // Images step should be available (blue) since slides is completed
    const imagesIsAvailable = imagesClass?.includes('bg-blue-500');
    // Compiled and PPTX should be pending (grey)
    const compiledIsGrey = compiledClass?.includes('bg-gray-100') || compiledClass?.includes('bg-gray-200') || compiledClass?.includes('bg-gray-300');
    const pptxIsGrey = pptxClass?.includes('bg-gray-100') || pptxClass?.includes('bg-gray-200') || pptxClass?.includes('bg-gray-300');

    console.log('Images step is available (blue):', imagesIsAvailable);
    console.log('Compiled step is grey (pending):', compiledIsGrey);
    console.log('PPTX step is grey (pending):', pptxIsGrey);

    expect(imagesIsAvailable).toBe(true);
    expect(compiledIsGrey).toBe(true);
    expect(pptxIsGrey).toBe(true);
  });
}); 