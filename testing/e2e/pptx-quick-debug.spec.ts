import { test, expect } from '@playwright/test';
import { createPresentation, getApiUrl } from './utils';

test.describe('PPTX Quick Debug', () => {
  test.setTimeout(60000);

  test('quick debug of step flow', async ({ page }) => {
    const name = `PPTX Quick Debug ${Date.now()}`;
    const topic = 'Quick debug topic';

    // Create presentation
    const presentationId = await createPresentation(page, name, topic);
    console.log(`Created presentation ID: ${presentationId}`);

    // 1. Quick research
    console.log('🔍 Running research...');
    const [researchResponse] = await Promise.all([
      page.waitForResponse(resp => resp.url().includes(`/presentations/${presentationId}/steps/research/run`) && resp.status() === 200),
      page.getByTestId('start-ai-research-button').click()
    ]);
    console.log('✅ Research completed');

    // 2. Navigate to slides and run
    console.log('🔍 Running slides...');
    await page.getByTestId('step-nav-slides').click();
    await page.waitForLoadState('networkidle');
    
    const runSlidesButton = page.getByTestId('run-slides-button');
    const slidesButtonExists = await runSlidesButton.count() > 0;
    console.log(`Slides button exists: ${slidesButtonExists}`);
    
    if (slidesButtonExists) {
      const [slidesResponse] = await Promise.all([
        page.waitForResponse(resp => resp.url().includes(`/presentations/${presentationId}/steps/slides/run`) && resp.status() === 200),
        runSlidesButton.click()
      ]);
      console.log('✅ Slides completed');
    }

    // 3. Navigate to illustration and check what's available
    console.log('🔍 Checking illustration step...');
    await page.getByTestId('step-nav-illustration').click({ force: true });
    await page.waitForLoadState('networkidle');
    
    const runIllustrationButton = page.getByTestId('run-illustration-button');
    const illustrationButtonExists = await runIllustrationButton.count() > 0;
    console.log(`Illustration button exists: ${illustrationButtonExists}`);
    
    if (illustrationButtonExists) {
      const isDisabled = await runIllustrationButton.isDisabled();
      console.log(`Illustration button disabled: ${isDisabled}`);
      
      if (!isDisabled) {
        const [illustrationResponse] = await Promise.all([
          page.waitForResponse(resp => resp.url().includes(`/presentations/${presentationId}/steps/illustration/run`) && resp.status() === 200),
          runIllustrationButton.click()
        ]);
        console.log('✅ Illustration completed');
      }
    }

    // 4. Navigate to compiled and check what's available
    console.log('🔍 Checking compiled step...');
    await page.getByTestId('step-nav-compiled').click({ force: true });
    await page.waitForLoadState('networkidle');
    
    const runCompiledButton = page.getByTestId('run-compiled-button');
    const compiledButtonExists = await runCompiledButton.count() > 0;
    console.log(`Compiled button exists: ${compiledButtonExists}`);

    // 5. Navigate to PPTX and check what's available
    console.log('🔍 Checking PPTX step...');
    await page.getByTestId('step-nav-pptx').click({ force: true });
    await page.waitForLoadState('networkidle');
    
    const runPptxButton = page.getByTestId('run-pptx-button');
    const pptxButtonExists = await runPptxButton.count() > 0;
    console.log(`PPTX button exists: ${pptxButtonExists}`);
    
    if (pptxButtonExists) {
      const isDisabled = await runPptxButton.isDisabled();
      console.log(`PPTX button disabled: ${isDisabled}`);
    }

    // 6. Check backend status
    const apiUrl = getApiUrl();
    try {
      const response = await page.request.get(`${apiUrl}/presentations/${presentationId}`);
      if (response.ok()) {
        const data = await response.json();
        console.log('📊 Backend step statuses:');
        if (data.steps) {
          for (const step of data.steps) {
            console.log(`  ${step.step}: ${step.status}`);
          }
        }
      }
    } catch (error) {
      console.log(`API error: ${error}`);
    }

    // Test passes - we're just debugging
    expect(true).toBe(true);
  });
}); 