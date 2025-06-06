import { test, expect } from '@playwright/test';
import { navigateToTestPresentationById } from './utils';

test.setTimeout(120000);

test.describe('Research Wizard Context', () => {
  test('should handle research refinement requests', async ({ page }) => {
    // Use preseeded presentation ID 15 (Wizard Research Ready - research completed)
    const presentation = await navigateToTestPresentationById(page, 15);
    console.log(`✅ Using preseeded presentation: ${presentation?.name}`);

    // Test research refinement
    console.log('🧙‍♂️ Testing research refinement...');
    
    const wizardInput = page.getByTestId('wizard-input');
    const sendButton = page.getByTestId('wizard-send-button');
    
    // Test research modification request
    await wizardInput.fill('Add more information about AI ethics and privacy concerns');
    
    // Debug - verify button is enabled
    const isButtonEnabled = await sendButton.isEnabled();
    console.log('Send button enabled:', isButtonEnabled);
    
    // Monitor console for all messages
    page.on('console', msg => {
      console.log(`Browser ${msg.type()}:`, msg.text());
    });
    
    // Monitor for page errors
    page.on('pageerror', error => {
      console.log('Page error:', error.message);
    });
    
    await sendButton.click();
    console.log('✅ Send button clicked');
    
    // Wait for assistant response (should get a second message after welcome)
    const assistantMessage = page.locator('[data-testid="wizard-message-assistant"]').last();
    await expect(assistantMessage).toBeVisible({ timeout: 15000 });
    console.log('✅ Assistant message visible');
    
    // Wait for message count to increase
    await page.waitForFunction(() => {
      const messages = document.querySelectorAll('[data-testid="wizard-message-assistant"]');
      return messages.length >= 2;
    }, { timeout: 15000 });
    
    const messageCount = await page.locator('[data-testid="wizard-message-assistant"]').count();
    console.log('Assistant message count:', messageCount);
    
    // Get the last message content
    const lastMessageContent = await assistantMessage.textContent();
    console.log('Last assistant message:', lastMessageContent?.substring(0, 100) + '...');
    
    // Check for suggestion box - should appear in both online and offline modes
    await expect(page.locator('[data-testid="wizard-suggestion"]')).toBeVisible({ timeout: 10000 });
    console.log('✅ Research refinement suggestion box appeared');
    
    // Verify suggestion components
    await expect(page.locator('[data-testid="wizard-apply-button"]')).toBeVisible();
    await expect(page.locator('[data-testid="wizard-dismiss-button"]')).toBeVisible();
    console.log('✅ Research refinement request processed with suggestion box')

    // Dismiss the suggestion box before testing questions
    await page.locator('[data-testid="wizard-dismiss-button"]').click();
    await expect(page.locator('[data-testid="wizard-suggestion"]')).not.toBeVisible();
    console.log('✅ Suggestion box dismissed');

    // Test research question
    await wizardInput.fill('What are the main challenges in AI healthcare implementation?');
    await sendButton.click();
    
    // Wait for the next wizard response
    await page.waitForSelector('[data-testid="wizard-message-assistant"]', { timeout: 15000 });
    
    // Should get a conversational response (no suggestion box for questions)
    const responseMessages = await page.locator('[data-testid="wizard-message-assistant"]').count();
    expect(responseMessages).toBeGreaterThan(1);
    
    // Verify no suggestion box for questions
    await expect(page.locator('[data-testid="wizard-suggestion"]')).not.toBeVisible();
    console.log('✅ Research question answered without suggestion box')
  });

  test('should provide research guidance', async ({ page }) => {
    // Use preseeded presentation ID 15 again (Wizard Research Ready - research completed)
    const presentation = await navigateToTestPresentationById(page, 15);
    console.log(`✅ Using preseeded presentation: ${presentation?.name}`);

    // Test guidance request
    const wizardInput = page.getByTestId('wizard-input');
    await wizardInput.fill('How can I improve the quality of this research?');
    await wizardInput.press('Enter');
    
    // Wait for wizard response
    await page.waitForSelector('[data-testid="wizard-message-assistant"]:last-child', { timeout: 10000 });
    
    // Should get helpful guidance
    const lastMessage = page.locator('[data-testid="wizard-message-assistant"]').last();
    await expect(lastMessage).toBeVisible();
    console.log('✅ Research guidance provided');
  });
}); 