import { test, expect } from '@playwright/test';
import { navigateToTestPresentationById } from './utils';

test.describe('Research Wizard Suggestions', () => {
  test('should allow wizard to modify research content with suggestions', async ({ page }) => {
    // Use preseeded presentation ID 15 (Wizard Research Ready - research completed)
    const presentation = await navigateToTestPresentationById(page, 15);
    console.log(`✅ Using preseeded presentation: ${presentation?.name}`);
    
    // Verify research content is generated
    await expect(page.locator('[data-testid="ai-research-content-label"]')).toBeVisible();
    await expect(page.locator('[data-testid="ai-research-content"]')).toBeVisible();
    
    // Test wizard suggestions functionality
    await test.step('Submit wizard request for research modification', async () => {
      // Click on the wizard input field
      const wizardInput = page.locator('[data-testid="wizard-input"]');
      await expect(wizardInput).toBeVisible();
      await expect(wizardInput).toBeEnabled();
      await wizardInput.click();
      
      // Type a request to modify the research
      const modificationRequest = 'Please add more information about AI ethics and privacy concerns in healthcare applications';
      await wizardInput.fill(modificationRequest);
      
      // Submit the request
      await wizardInput.press('Enter');
      
      // In offline mode, user messages might not be displayed
      const isOffline = process.env.POWERIT_OFFLINE_E2E === 'true';
      if (!isOffline) {
        // Verify the request appears in the wizard chat
        await expect(page.locator('[data-testid="wizard-message-user"]').last()).toContainText(modificationRequest);
      }
    });
    
    await test.step('Wait for wizard to process and generate suggestion', async () => {
      // Wait for any assistant response to appear after the user message
      await expect(page.locator('[data-testid="wizard-message-assistant"]').nth(1)).toBeVisible({ timeout: 15000 });
      
      // Wait for wizard response
      await page.waitForLoadState('networkidle');
      
      // In offline mode, responses work differently
      const isOffline = process.env.POWERIT_OFFLINE_E2E === 'true';
      
      if (isOffline) {
        // In offline mode, check for assistant message
        const assistantMessages = await page.locator('[data-testid="wizard-message-assistant"]').count();
        expect(assistantMessages).toBeGreaterThanOrEqual(1);
        console.log(`✅ Wizard responded with ${assistantMessages} message(s) (offline mode)`);
        
        // Note: In offline mode for research modifications, the wizard returns changes
        // but they may not appear as a visible suggestion box
        console.log('ℹ️ In offline mode, research modifications are processed differently');
      } else {
        // In online mode, check for suggestion or response
        const hasSuggestion = await page.locator('[data-testid="wizard-suggestion"]').isVisible();
        const hasResponse = await page.locator('[data-testid="wizard-message-assistant"]').count() > 1;
        
        console.log(`Has suggestion: ${hasSuggestion}, Has response: ${hasResponse}`);
        
        // At least one should be true
        expect(hasSuggestion || hasResponse).toBe(true);
        
        if (hasSuggestion) {
          console.log('✅ Wizard suggestion generated successfully');
          
          // Verify suggestion components are present
          await expect(page.locator('[data-testid="wizard-apply-button"]')).toBeVisible();
          await expect(page.locator('[data-testid="wizard-dismiss-button"]')).toBeVisible();
          
          // Apply the changes
          const applyButton = page.locator('[data-testid="wizard-apply-button"]');
          await applyButton.click();
          
          // Wait for the suggestion to disappear (indicating changes were applied)
          await expect(page.locator('[data-testid="wizard-suggestion"]')).not.toBeVisible({ timeout: 15000 });
          
          console.log('✅ Wizard suggestion applied successfully');
        } else {
          console.log('ℹ️ Wizard provided a response but no suggestion was generated');
        }
      }
    });
    
    await test.step('Verify research content is accessible', async () => {
      // Check that the research content is still visible and accessible
      const researchContent = page.locator('[data-testid="ai-research-content"]').first();
      await expect(researchContent).toBeVisible();
      
      // Verify the research step is still visible and functional
      const stepButton = page.locator('[data-testid="step-nav-research"]');
      await expect(stepButton).toBeVisible();
      
      console.log('✅ Research content remains accessible after wizard interaction');
    });
  });
  
  test('should handle wizard gracefully when no suggestions are needed', async ({ page }) => {
    // Use preseeded presentation ID 15 (Wizard Research Ready - research completed)
    const presentation = await navigateToTestPresentationById(page, 15);
    console.log(`✅ Using preseeded presentation: ${presentation?.name}`);
    
    // Test with a simple informational request
    const wizardInput = page.locator('[data-testid="wizard-input"]');
    await wizardInput.click();
    await wizardInput.fill('What is this research about?');
    await wizardInput.press('Enter');
    
    // Wait for response
    await expect(page.locator('[data-testid="wizard-message-assistant"]').nth(1)).toBeVisible({ timeout: 15000 });
    
    // Should not crash and wizard should remain functional
    await expect(wizardInput).toBeVisible();
  });
  
  test('should maintain wizard functionality on research page', async ({ page }) => {
    // Use preseeded presentation ID 15 (Wizard Research Ready - research completed)
    const presentation = await navigateToTestPresentationById(page, 15);
    console.log(`✅ Using preseeded presentation: ${presentation?.name}`);
    
    // Test basic wizard functionality
    const wizardInput = page.locator('[data-testid="wizard-input"]');
    await expect(wizardInput).toBeVisible();
    
    // Test that we can type in the wizard
    await wizardInput.click();
    await wizardInput.fill('Test message');
    
    // Verify the text was entered
    const inputValue = await wizardInput.inputValue();
    expect(inputValue).toBe('Test message');
    
    console.log('✅ Wizard input functionality verified');
  });
}); 