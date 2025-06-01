import { test, expect } from '@playwright/test';
import {
  createPresentation,
  startAIResearch,
  waitForResearchCompletion
} from './utils';

test.describe('Test Research Apply Fix', () => {
  test('manually test research apply functionality', async ({ page }) => {
    // Set viewport to ensure wizard is visible
    await page.setViewportSize({ width: 1400, height: 900 });

    // Create a new presentation and generate research content
    await createPresentation(page, 'Research Apply Fix', 'AI for Testing');
    await startAIResearch(page);
    await waitForResearchCompletion(page);
    
    // Ensure the research content is visible
    const researchContent = page.locator('[data-testid="ai-research-content"]');
    await expect(researchContent).toBeVisible();
    
    // Get initial research content
    const initialContent = await researchContent.textContent();
    console.log('Initial content length:', initialContent?.length);
    
    // Send a modification request
    const wizardInput = page.locator('[data-testid="wizard-input"]');
    await wizardInput.fill('Add more information about AI ethics and privacy concerns');
    await wizardInput.press('Enter');
    
    // Wait for wizard response
    await page.waitForTimeout(3000);
    
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
      const toast = page.locator('text="Changes applied"').or(page.locator('text="research has been updated"'));
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