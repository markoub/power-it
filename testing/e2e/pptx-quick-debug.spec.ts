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
    
    // Set up response logging
    page.on('response', response => {
      if (response.url().includes('/presentations') && response.url().includes('steps')) {
        console.log(`API Response: ${response.status()} ${response.url()}`);
      }
    });
    
    // Handle potential clarification dialog
    const [clarificationResponse] = await Promise.all([
      page.waitForResponse(
        response => response.url().includes('/research/clarification/check') && response.status() === 200,
        { timeout: 10000 }
      ),
      page.getByTestId('start-ai-research-button').click()
    ]);
    
    const clarificationData = await clarificationResponse.json();
    
    if (clarificationData.needs_clarification) {
      console.log('✅ AI requested clarification - providing simple response');
      await expect(page.getByText('Research Clarification')).toBeVisible();
      
      // Provide a simple clarification
      const clarificationInput = page.locator('input[placeholder="Type your clarification..."]');
      await clarificationInput.fill('Just general debugging information');
      await clarificationInput.press('Enter');
      
      // Wait for dialog to close
      await expect(page.getByText('Research Clarification')).not.toBeVisible({ timeout: 15000 });
    }
    
    // Wait for research to complete (flexible - might be generating or already done)
    const researchGenerating = page.getByText('Generating Research');
    const researchCompleted = page.getByText('Generated Research Content');
    await expect(researchGenerating.or(researchCompleted)).toBeVisible({ timeout: 30000 });
    console.log('✅ Research progress detected');
    
    // Wait for research to actually complete
    await page.waitForTimeout(2000); // Give it a moment
    
    // Check if research completed
    if (await researchCompleted.isVisible()) {
      console.log('✅ Research completed');
    } else {
      // Wait for research to finish
      await expect(researchCompleted).toBeVisible({ timeout: 30000 });
      console.log('✅ Research completed after wait');
    }

    // 2. Navigate to slides and run
    console.log('🔍 Running slides...');
    
    // Wait for slides step to be enabled
    const slidesNavButton = page.getByTestId('step-nav-slides');
    await expect(slidesNavButton).toBeEnabled({ timeout: 10000 });
    await slidesNavButton.click();
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
    
    const runIllustrationButton = page.getByTestId('run-images-button-center');
    const illustrationButtonExists = await runIllustrationButton.count() > 0;
    console.log(`Illustration button exists: ${illustrationButtonExists}`);
    
    if (illustrationButtonExists) {
      const isDisabled = await runIllustrationButton.isDisabled();
      console.log(`Illustration button disabled: ${isDisabled}`);
      
      if (!isDisabled) {
        const [illustrationResponse] = await Promise.all([
          page.waitForResponse(resp => resp.url().includes(`/presentations/${presentationId}/steps/images/run`) && resp.status() === 200),
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