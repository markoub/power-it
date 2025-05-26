import { test, expect } from '@playwright/test';
import { createPresentation } from './utils';

test.setTimeout(120000);

test.describe('Research Wizard Context', () => {
  test('should handle research refinement requests', async ({ page }) => {
    const name = `Research Wizard Test ${Date.now()}`;
    const topic = 'Artificial Intelligence in Healthcare';

    // Create presentation and complete research step
    const id = await createPresentation(page, name, topic);
    console.log(`✅ Created presentation with ID: ${id}`);

    // Complete research step
    console.log('🔍 Running research...');
    await page.getByTestId('start-ai-research-button').click();
    await page.waitForTimeout(5000);
    console.log('✅ Research completed');

    // Test research refinement
    console.log('🧙‍♂️ Testing research refinement...');
    
    const wizardInput = page.getByTestId('wizard-input');
    const sendButton = page.getByTestId('wizard-send-button');
    
    // Test research modification request
    await wizardInput.fill('Add more information about AI ethics and privacy concerns');
    await sendButton.click();
    
    // Wait for response
    await page.waitForTimeout(5000);
    
    // Check for suggestion or response
    const hasSuggestion = await page.locator('[data-testid="wizard-suggestion"]').isVisible();
    const hasResponse = await page.locator('[data-testid="wizard-message-assistant"]').count() > 1;
    
    expect(hasSuggestion || hasResponse).toBe(true);
    console.log('✅ Research refinement request processed');

    // Test research question
    await wizardInput.fill('What are the main challenges in AI healthcare implementation?');
    await sendButton.click();
    
    await page.waitForTimeout(3000);
    
    // Should get a conversational response
    const responseMessages = await page.locator('[data-testid="wizard-message-assistant"]').count();
    expect(responseMessages).toBeGreaterThan(1);
    console.log('✅ Research question answered');
  });

  test('should provide research guidance', async ({ page }) => {
    const name = `Research Guidance Test ${Date.now()}`;
    const topic = 'Climate Change Solutions';

    const id = await createPresentation(page, name, topic);
    
    // Complete research step
    await page.getByTestId('start-ai-research-button').click();
    await page.waitForTimeout(5000);

    // Test guidance request
    const wizardInput = page.getByTestId('wizard-input');
    await wizardInput.fill('How can I improve the quality of this research?');
    await wizardInput.press('Enter');
    
    await page.waitForTimeout(3000);
    
    // Should get helpful guidance
    const lastMessage = page.locator('[data-testid="wizard-message-assistant"]').last();
    await expect(lastMessage).toBeVisible();
    console.log('✅ Research guidance provided');
  });
}); 