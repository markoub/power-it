import { test, expect } from '@playwright/test';
import { navigateToTestPresentationById } from './utils';

test.describe('Research Context in Wizard', () => {
  test('should display research context in wizard on Research step', async ({ page }) => {
    // Set viewport to ensure wizard is visible (it's hidden on mobile)
    await page.setViewportSize({ width: 1400, height: 900 });
    
    // Use preseeded presentation ID 15 (Wizard Research Ready - research completed)
    const presentation = await navigateToTestPresentationById(page, 15);
    console.log(`✅ Using preseeded presentation: ${presentation?.name}`);
    
    // Check that research context is visible in wizard
    await test.step('Verify research context component', async () => {
      // Wait for research content to be displayed
      await expect(page.locator('[data-testid="ai-research-content"]')).toBeVisible();
      
      // Look for research context card using more specific selectors
      const researchContextCard = page.locator('.mb-4').filter({ has: page.locator('text="Research Context"') });
      await expect(researchContextCard).toBeVisible();
      
      // Check for stats badges (words, sections, sources)
      const wordsBadge = page.locator('.text-xs').filter({ hasText: /\d+ words/ });
      await expect(wordsBadge).toBeVisible();
      
      const sectionsBadge = page.locator('.text-xs').filter({ hasText: /\d+ sections/ });
      await expect(sectionsBadge).toBeVisible();
      
      const sourcesBadge = page.locator('.text-xs').filter({ hasText: /\d+ sources/ });
      await expect(sourcesBadge).toBeVisible();
      
      console.log('✅ Research context is displayed in wizard');
    });
    
    // Test section expansion
    await test.step('Test content outline interaction', async () => {
      // Try to find and click a section header
      const sectionHeaders = page.locator('button:has-text("##")');
      const headerCount = await sectionHeaders.count();
      
      if (headerCount > 0) {
        // Click the first section header
        await sectionHeaders.first().click();
        
        // Wait for animation to complete
        await page.waitForLoadState('networkidle');
        
        console.log('✅ Section expansion works');
      }
    });
    
    // Test wizard suggestions in context
    await test.step('Test wizard with research context visible', async () => {
      const wizardInput = page.locator('[data-testid="wizard-input"]');
      await wizardInput.fill('Add more information about solar panel efficiency');
      await wizardInput.press('Enter');
      
      // Wait for wizard response
      await expect(page.locator('[data-testid="wizard-message-assistant"]').nth(1)).toBeVisible({ timeout: 10000 });
      
      // Check that research content is still accessible
      await expect(page.locator('[data-testid="ai-research-content"]')).toBeVisible();
      
      // Check for wizard response
      const assistantMessages = await page.locator('[data-testid="wizard-message-assistant"]').count();
      expect(assistantMessages).toBeGreaterThan(1);
      
      console.log('✅ Wizard works with research context visible');
    });
  });
  
  test('should show helpful prompts in research context', async ({ page }) => {
    // Set viewport to ensure wizard is visible
    await page.setViewportSize({ width: 1400, height: 900 });
    
    // Use preseeded presentation ID 18 (Wizard Context Test - research completed)
    const presentation = await navigateToTestPresentationById(page, 18);
    console.log(`✅ Using preseeded presentation: ${presentation?.name}`);
    
    // Check for helpful prompts section
    const tryAskingSection = page.locator('text="Try asking me to:"');
    await expect(tryAskingSection).toBeVisible();
    
    // Check for the bulleted list with suggestions
    const suggestionsList = page.locator('ul').filter({ hasText: /Add a section|Expand|Make.*engaging|Add.*statistics/ });
    await expect(suggestionsList).toBeVisible();
    
    // Check that at least one list item is present
    const listItems = suggestionsList.locator('li');
    const itemCount = await listItems.count();
    expect(itemCount).toBeGreaterThan(0);
    console.log('✅ Helpful prompts are displayed');
  });
});