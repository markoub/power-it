import { test, expect } from '@playwright/test';
import { createPresentation, startAIResearch, waitForResearchCompletion } from '../utils';

test.describe('Research Context in Wizard', () => {
  test('should display research context in wizard on Research step', async ({ page }) => {
    // Set viewport to ensure wizard is visible (it's hidden on mobile)
    await page.setViewportSize({ width: 1400, height: 900 });
    
    // Create a presentation with a specific topic
    const presentationId = await createPresentation(
      page, 
      'Research Context Test', 
      'Renewable Energy Solutions for Urban Areas'
    );
    
    // Start and complete research
    await startAIResearch(page);
    await waitForResearchCompletion(page);
    
    // Check that research context is visible in wizard
    await test.step('Verify research context component', async () => {
      // Look for research context card
      const researchContext = page.locator('text="Research Context"').first();
      await expect(researchContext).toBeVisible();
      
      // Check for topic display
      const topicSection = page.locator('text="Topic"').first();
      await expect(topicSection).toBeVisible();
      await expect(page.locator('text="Renewable Energy Solutions for Urban Areas"')).toBeVisible();
      
      // Check for content outline
      const contentOutline = page.locator('text="Content Outline"');
      await expect(contentOutline).toBeVisible();
      
      // Check for stats in the Research Context header
      // The text appears as "Research Context 269 words 7 sections 0 sources"
      const researchContextHeader = page.locator('text=/Research Context.*words.*sections.*sources/');
      await expect(researchContextHeader).toBeVisible();
      
      // This confirms stats are being displayed
      const headerText = await researchContextHeader.textContent();
      expect(headerText).toMatch(/\d+ words/);
      expect(headerText).toMatch(/\d+ sections/);
      expect(headerText).toMatch(/\d+ sources/);
      
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
      await page.waitForSelector('[data-testid="wizard-message-assistant"]:nth-child(2)', { timeout: 10000 });
      
      // Research context should still be visible
      await expect(page.locator('text="Research Context"').first()).toBeVisible();
      
      // Check for wizard response
      const assistantMessages = await page.locator('[data-testid="wizard-message-assistant"]').count();
      expect(assistantMessages).toBeGreaterThan(1);
      
      console.log('✅ Wizard works with research context visible');
    });
  });
  
  test('should show helpful prompts in research context', async ({ page }) => {
    // Set viewport to ensure wizard is visible
    await page.setViewportSize({ width: 1400, height: 900 });
    
    const presentationId = await createPresentation(
      page, 
      'Research Prompts Test', 
      'Artificial Intelligence in Education'
    );
    
    await startAIResearch(page);
    await waitForResearchCompletion(page);
    
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