import { test, expect } from '@playwright/test';
import { navigateToTestPresentationById } from './utils';

test.describe('Research Apply Fix', () => {
  test('should apply wizard research modifications correctly', async ({ page }) => {
    // Set viewport to ensure wizard is visible
    await page.setViewportSize({ width: 1400, height: 900 });
    
    // Use preseeded presentation ID 15 (Wizard Research Ready - has research completed)
    const presentation = await navigateToTestPresentationById(page, 15);
    console.log(`✅ Using preseeded presentation: ${presentation?.name}`);
    
    // Wait for page to load and ensure we're on research step
    await page.waitForSelector('[data-testid="wizard-input"]', { timeout: 10000 });
    await page.waitForLoadState('networkidle');
    
    // Check that research content is loaded
    const researchContent = page.locator('[data-testid="ai-research-content"]');
    await expect(researchContent).toBeVisible();
    
    // Get initial research content
    const initialContent = await researchContent.textContent();
    console.log('Initial content length:', initialContent?.length);
    
    // Send a modification request
    const wizardInput = page.locator('[data-testid="wizard-input"]');
    await wizardInput.fill('Add more information about AI ethics and privacy concerns');
    await wizardInput.press('Enter');
    
    // Wait for wizard response - use proper selector
    await page.waitForSelector('[data-testid="wizard-message-assistant"]:last-child', { timeout: 10000 });
    
    // Check if suggestion appeared
    const wizardSuggestion = page.locator('[data-testid="wizard-suggestion"]');
    const hasSuggestion = await wizardSuggestion.isVisible();
    console.log('Has suggestion:', hasSuggestion);
    
    if (hasSuggestion) {
      // Look for apply button
      const applyButton = page.locator('[data-testid="wizard-apply-button"]');
      await expect(applyButton).toBeVisible();
      
      // Click apply
      console.log('Clicking apply button...');
      await applyButton.click();
      
      // Wait for changes to apply
      await page.waitForTimeout(2000);
      
      // Check if research content changed
      const updatedContent = await researchContent.textContent();
      console.log('Updated content length:', updatedContent?.length);
      console.log('Content changed:', initialContent !== updatedContent);
      
      // Check for toast notification
      // Look for any success toast notification
      const toast = page.locator('[role="alert"]').filter({ hasText: /applied|updated|success/i });
      const toastVisible = await toast.isVisible({ timeout: 5000 }).catch(() => false);
      console.log('Toast visible:', toastVisible);
      
      // Check if suggestion disappeared
      const suggestionGone = !(await wizardSuggestion.isVisible());
      console.log('Suggestion removed after apply:', suggestionGone);
      
      // Verify the content actually changed
      expect(updatedContent).not.toBe(initialContent);
      expect(updatedContent?.length).toBeGreaterThan(initialContent?.length || 0);
    } else {
      // No suggestion, check what happened
      const assistantMessages = await page.locator('[data-testid="wizard-message-assistant"]').all();
      for (const msg of assistantMessages) {
        console.log('Assistant message:', await msg.textContent());
      }
      
      throw new Error('No suggestion was generated');
    }
  });
});