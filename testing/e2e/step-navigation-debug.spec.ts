import { test, expect } from '@playwright/test';
import { createPresentation } from './utils';

test.describe('Step Navigation Debug', () => {
  test.setTimeout(60000);

  test('check what step navigation exists', async ({ page }) => {
    const name = `Step Nav Debug ${Date.now()}`;
    const topic = 'Debug topic';

    // Create presentation
    await createPresentation(page, name, topic);
    
    // Run research quickly
    await page.getByTestId('start-ai-research-button').click();
    await page.waitForTimeout(3000);
    
    // Run slides quickly
    await page.getByTestId('step-nav-slides').click();
    await page.waitForTimeout(1000);
    await page.getByTestId('run-slides-button').click();
    await page.waitForTimeout(3000);

    // Now check what step nav elements exist
    console.log('🔍 Checking what step navigation elements exist...');
    
    const allStepTypes = ['research', 'manual_research', 'slides', 'images', 'compiled', 'pptx'];
    
    for (const stepType of allStepTypes) {
      const stepNav = page.getByTestId(`step-nav-${stepType}`);
      const exists = await stepNav.count() > 0;
      console.log(`step-nav-${stepType}: exists=${exists}`);
      
      if (exists) {
        const isVisible = await stepNav.isVisible();
        const isDisabled = await stepNav.isDisabled().catch(() => 'unknown');
        console.log(`  visible=${isVisible}, disabled=${isDisabled}`);
      }
    }
    
    // Also check what elements with 'step-nav-' exist at all
    console.log('🔍 Checking all elements with step-nav- prefix...');
    const allStepNavs = await page.locator('[data-testid^="step-nav-"]').all();
    console.log(`Found ${allStepNavs.length} step-nav elements:`);
    
    for (let i = 0; i < allStepNavs.length; i++) {
      const testId = await allStepNavs[i].getAttribute('data-testid');
      const isVisible = await allStepNavs[i].isVisible();
      const isDisabled = await allStepNavs[i].isDisabled().catch(() => 'unknown');
      console.log(`  ${testId}: visible=${isVisible}, disabled=${isDisabled}`);
    }

    // Take a screenshot for visual debugging
    await page.screenshot({ path: `step-navigation-debug-${Date.now()}.png` });

    expect(true).toBe(true);
  });
}); 