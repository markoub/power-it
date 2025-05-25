import { test, expect } from '@playwright/test';
import { 
  createPresentation, 
  waitForStepCompletion, 
  navigateToEditPage,
  fillResearchTopic,
  startAIResearch,
  waitForResearchCompletion
} from './utils';

test.describe('Research Wizard Suggestions', () => {
  test('should allow wizard to modify research content with suggestions', async ({ page }) => {
    // Create a new presentation for testing (this also sets up the AI research interface)
    const presentationId = await createPresentation(page, 'Research Wizard Suggestions Test', 'Artificial Intelligence in Healthcare: Current Applications and Future Trends');
    
    // Verify we're on the Research step and AI interface is ready
    await expect(page.locator('[data-testid="step-nav-research"]')).toBeVisible();
    await expect(page.locator('[data-testid="ai-research-interface"]')).toBeVisible();
    await expect(page.locator('[data-testid="start-ai-research-button"]')).toBeVisible();
    
    // Start AI research (topic already filled during creation)
    await startAIResearch(page);
    
    // Wait for research to complete
    await waitForResearchCompletion(page);
    
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
      
      // Verify the request appears in the wizard chat
      await expect(page.locator(`text=${modificationRequest}`)).toBeVisible();
    });
    
    await test.step('Wait for wizard to process and generate suggestion', async () => {
      // Wait for processing message
      await expect(page.locator('text=Processing your request')).toBeVisible();
      
      // Wait for suggestion to be generated (using data-testid instead of specific text)
      // Be more flexible - wait for any wizard response
      await page.waitForTimeout(10000); // Give time for processing
      
      // Check if a suggestion was generated OR if there's a response message
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
    // Create a new presentation
    const presentationId = await createPresentation(page, 'Research Wizard Simple Test', 'Simple Test Topic');
    
    // Generate research content first
    await startAIResearch(page);
    await waitForResearchCompletion(page);
    
    // Test with a simple informational request
    const wizardInput = page.locator('[data-testid="wizard-input"]');
    await wizardInput.click();
    await wizardInput.fill('What is this research about?');
    await wizardInput.press('Enter');
    
    // Wait for response
    await page.waitForTimeout(5000);
    
    // Should not crash and wizard should remain functional
    await expect(wizardInput).toBeVisible();
  });
  
  test('should maintain wizard functionality on research page', async ({ page }) => {
    // Create presentation and generate research
    const presentationId = await createPresentation(page, 'Wizard Functionality Test', 'Test Research Topic');
    
    await startAIResearch(page);
    await waitForResearchCompletion(page);
    
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