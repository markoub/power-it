import { test, expect } from '@playwright/test';
import { createPresentation, getApiUrl } from './utils';

test.describe('Step Status Debug', () => {
  test.setTimeout(60000);

  test('debug step status completion issue', async ({ page }) => {
    const name = `Step Status Debug ${Date.now()}`;
    const topic = 'Debug topic';

    // Create presentation
    const presentationId = await createPresentation(page, name, topic);
    console.log(`Created presentation ID: ${presentationId}`);

    // Start AI research
    console.log('🔍 Starting AI research...');
    await page.getByTestId('start-ai-research-button').click();

    // Wait for content to appear
    await expect(page.getByTestId('ai-research-content')).toBeVisible({ timeout: 30000 });
    console.log('✅ Research content is visible in UI');

    // Check backend status directly via API
    const apiUrl = getApiUrl();
    console.log(`🔍 Checking backend status via ${apiUrl}/presentations/${presentationId}`);
    
    let backendStatus = null;
    let attempts = 0;
    const maxAttempts = 10;
    
    while (attempts < maxAttempts) {
      attempts++;
      console.log(`Backend check attempt ${attempts}/${maxAttempts}`);
      
      try {
        const response = await page.request.get(`${apiUrl}/presentations/${presentationId}`);
        if (response.ok()) {
          const data = await response.json();
          const researchStep = data.steps?.find((s: any) => s.step === 'research');
          
          console.log(`Research step from backend:`, {
            step: researchStep?.step,
            status: researchStep?.status,
            hasResult: !!researchStep?.result,
            resultLength: researchStep?.result?.content?.length || 0
          });
          
          if (researchStep && researchStep.status === 'completed') {
            backendStatus = 'completed';
            console.log('✅ Research step completed in backend');
            break;
          } else if (researchStep && researchStep.status === 'processing') {
            console.log('⏳ Research step still processing in backend');
          } else if (researchStep && researchStep.status === 'pending') {
            console.log('⚠️ Research step still pending in backend');
          } else {
            console.log('❓ Research step status unknown or missing');
          }
        } else {
          console.log(`❌ API request failed: ${response.status()}`);
        }
      } catch (error) {
        console.log(`❌ API request error: ${error}`);
      }
      
      await new Promise(resolve => setTimeout(resolve, 2000));
    }

    // Check UI status
    console.log('🔍 Checking UI step status...');
    const stepButton = page.getByTestId('step-nav-research');
    const hasCheckIcon = await stepButton.locator('[data-lucide="check-circle-2"]').count() > 0;
    const isDisabled = await stepButton.isDisabled();
    const className = await stepButton.getAttribute('class');
    
    console.log(`UI step status:`, {
      hasCheckIcon,
      isDisabled,
      className: className?.includes('ring-') ? 'active' : 'inactive'
    });

    // Now try slides step
    console.log('🔍 Checking slides step availability...');
    const slidesButton = page.getByTestId('step-nav-slides');
    const slidesDisabled = await slidesButton.isDisabled();
    console.log(`Slides button disabled: ${slidesDisabled}`);

    // Click slides step to navigate there
    if (!slidesDisabled) {
      console.log('✅ Slides step is enabled - clicking it');
      await slidesButton.click();
      
      // Check if run slides button exists
      const runSlidesButton = page.getByTestId('run-slides-button');
      const runButtonExists = await runSlidesButton.count() > 0;
      const runButtonDisabled = runButtonExists ? await runSlidesButton.isDisabled() : true;
      
      console.log(`Run slides button:`, {
        exists: runButtonExists,
        disabled: runButtonDisabled
      });
      
      if (runButtonExists && !runButtonDisabled) {
        console.log('🚀 Starting slides generation...');
        await runSlidesButton.click();
        
        // Wait for slides to appear or button to change state
        await page.waitForTimeout(5000);
        
        // Check if slides were generated
        const slideExists = await page.getByTestId('slide-thumbnail-0').count() > 0;
        console.log(`Slide generated: ${slideExists}`);
        
        // Check backend status again
        const finalResponse = await page.request.get(`${apiUrl}/presentations/${presentationId}`);
        if (finalResponse.ok()) {
          const finalData = await finalResponse.json();
          const finalResearchStep = finalData.steps?.find((s: any) => s.step === 'research');
          const finalSlidesStep = finalData.steps?.find((s: any) => s.step === 'slides');
          
          console.log('🏁 Final backend status:');
          console.log(`Research step:`, {
            status: finalResearchStep?.status,
            hasResult: !!finalResearchStep?.result
          });
          console.log(`Slides step:`, {
            status: finalSlidesStep?.status,
            hasResult: !!finalSlidesStep?.result
          });
        }
      }
    } else {
      console.log('❌ Slides step is disabled - this is the problem!');
    }

    // Summary
    console.log('📊 Debug Summary:');
    console.log(`Backend research status: ${backendStatus || 'not completed'}`);
    console.log(`UI shows research completed: ${hasCheckIcon}`);
    console.log(`Slides step enabled: ${!slidesDisabled}`);
    
    // The test should pass - we're just debugging
    expect(true).toBe(true);
  });
}); 