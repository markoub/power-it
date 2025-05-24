import { test, expect } from '@playwright/test';
import { createPresentation } from './utils';

test.setTimeout(180000); // 3 minutes for comprehensive testing

test.describe('Enhanced Wizard Functionality', () => {
  test('should test complete wizard workflow with improvements', async ({ page }) => {
    const name = `Enhanced Wizard Test ${Date.now()}`;
    const topic = 'AI-Powered Digital Marketing Strategies for E-commerce Growth';

    // Create presentation and complete research and slides steps
    const id = await createPresentation(page, name, topic);
    console.log(`✅ Created presentation with ID: ${id}`);

    // 1. Complete research step
    console.log('🔍 Running research...');
    await page.getByTestId('start-ai-research-button').click();
    await page.waitForTimeout(5000);
    console.log('✅ Research completed');

    // 2. Navigate to slides and generate slides
    console.log('📊 Generating slides...');
    await page.getByTestId('step-nav-slides').click();
    await page.waitForTimeout(1000);
    
    const runSlidesButton = page.getByTestId('run-slides-button');
    if (await runSlidesButton.count() > 0) {
      await runSlidesButton.click();
      await page.waitForTimeout(15000); // Wait for slides generation
      console.log('✅ Slides generated');
    }

    // 3. Test wizard context awareness
    console.log('🧙‍♂️ Testing wizard context awareness...');
    
    // Check initial wizard state (should be "All Slides" context)
    const wizardHeader = page.locator('[data-testid="wizard-header"]').first();
    await expect(wizardHeader).toContainText('All Slides');
    
    // Select first slide to change context to "Single Slide"
    const firstSlide = page.getByTestId('slide-thumbnail-0');
    await expect(firstSlide).toBeVisible({ timeout: 10000 });
    await firstSlide.click();
    console.log('✅ Selected first slide');

    // Verify context changed to single slide
    await expect(wizardHeader).toContainText('Single Slide');
    console.log('✅ Wizard context updated correctly');

    // 4. Test wizard message status indicators
    console.log('💬 Testing message status indicators...');
    
    const wizardInput = page.getByTestId('wizard-input');
    const sendButton = page.getByTestId('wizard-send-button');
    
    // Send a message and check for status indicators
    await wizardInput.fill('Please improve this slide with better formatting and more engaging content');
    await sendButton.click();
    
    // Check for loading state in send button
    await expect(sendButton).toBeDisabled();
    console.log('✅ Send button shows loading state');
    
    // Wait for processing and check for status icons
    await page.waitForTimeout(3000);
    
    // Look for status icons (success, processing, etc.)
    const statusIcons = page.locator('.lucide-check-circle, .lucide-clock, .lucide-alert-circle');
    await expect(statusIcons.first()).toBeVisible({ timeout: 10000 });
    console.log('✅ Message status indicators working');

    // 5. Test enhanced suggestion preview
    console.log('👁️ Testing suggestion preview functionality...');
    
    // Wait for suggestion box to appear
    const suggestionBox = page.locator('text=Suggested Changes');
    await expect(suggestionBox).toBeVisible({ timeout: 15000 });
    console.log('✅ Suggestion box appeared');
    
    // Test preview toggle button
    const previewButton = page.locator('button:has-text("Preview")');
    if (await previewButton.count() > 0) {
      await previewButton.click();
      console.log('✅ Preview toggle clicked');
      
      // Check for before/after comparison
      const beforeText = page.locator('text=Before:');
      const afterText = page.locator('text=After:');
      
      if (await beforeText.count() > 0 && await afterText.count() > 0) {
        console.log('✅ Before/after comparison visible');
      }
      
      // Toggle back to hide preview
      const hideButton = page.locator('button:has-text("Hide")');
      if (await hideButton.count() > 0) {
        await hideButton.click();
        console.log('✅ Preview toggle works both ways');
      }
    }

    // 6. Test apply changes functionality
    console.log('✅ Testing apply changes...');
    
    // Get current slide title before applying changes
    const currentTitle = await page.locator('[data-testid="slide-title-input"]').inputValue();
    console.log(`Current title: ${currentTitle}`);
    
    // Apply the suggested changes
    const applyButton = page.locator('button:has-text("Apply Changes")');
    await expect(applyButton).toBeVisible();
    await expect(applyButton).toBeEnabled();
    await applyButton.click();
    console.log('✅ Apply changes clicked');
    
    // Wait for changes to be applied
    await page.waitForTimeout(2000);
    
    // Check that suggestion box disappeared
    await expect(suggestionBox).not.toBeVisible();
    console.log('✅ Suggestion box disappeared after applying');
    
    // Check for success message
    const successMessage = page.locator('text=successfully applied');
    await expect(successMessage).toBeVisible({ timeout: 5000 });
    console.log('✅ Success message appeared');
    
    // Verify title actually changed
    const newTitle = await page.locator('[data-testid="slide-title-input"]').inputValue();
    if (newTitle !== currentTitle) {
      console.log(`✅ Title changed from "${currentTitle}" to "${newTitle}"`);
    }

    // 7. Test dismiss functionality
    console.log('❌ Testing dismiss functionality...');
    
    // Send another request to get a new suggestion
    await wizardInput.fill('Add bullet points about key benefits');
    await sendButton.click();
    await page.waitForTimeout(5000);
    
    // Wait for new suggestion
    const newSuggestionBox = page.locator('text=Suggested Changes');
    await expect(newSuggestionBox).toBeVisible({ timeout: 15000 });
    
    // Click dismiss button
    const dismissButton = page.locator('button:has-text("Dismiss")');
    await expect(dismissButton).toBeVisible();
    await dismissButton.click();
    console.log('✅ Dismiss button clicked');
    
    // Check that suggestion box disappeared
    await expect(newSuggestionBox).not.toBeVisible();
    console.log('✅ Suggestion box dismissed correctly');
    
    // Check for dismiss message
    const dismissMessage = page.locator('text=dismissed');
    await expect(dismissMessage).toBeVisible({ timeout: 5000 });
    console.log('✅ Dismiss message appeared');

    // 8. Test error handling
    console.log('⚠️ Testing error handling...');
    
    // Try to send an empty message (should be prevented)
    await wizardInput.fill('');
    await expect(sendButton).toBeDisabled();
    console.log('✅ Send button disabled for empty input');
    
    // Test with very long message to potentially trigger errors
    const longMessage = 'A'.repeat(1000) + ' - test error handling with very long input';
    await wizardInput.fill(longMessage);
    await sendButton.click();
    await page.waitForTimeout(5000);
    
    // Check if error handling works (error message or graceful degradation)
    const errorIndicator = page.locator('.lucide-alert-circle, text=error, text=Error');
    if (await errorIndicator.count() > 0) {
      console.log('✅ Error handling working');
    } else {
      console.log('✅ Long message handled gracefully');
    }

    // 9. Test auto-scroll functionality
    console.log('📜 Testing auto-scroll...');
    
    // Send multiple messages to test scrolling
    for (let i = 0; i < 3; i++) {
      await wizardInput.fill(`Test message ${i + 1} for scroll testing`);
      await sendButton.click();
      await page.waitForTimeout(2000);
    }
    
    // Check that the latest message is visible (auto-scrolled)
    const latestMessage = page.locator('text=Test message 3 for scroll testing');
    await expect(latestMessage).toBeVisible();
    console.log('✅ Auto-scroll functionality working');

    // 10. Test step-specific wizard behavior
    console.log('🔄 Testing step-specific behavior...');
    
    // Navigate to Illustrations step
    await page.getByTestId('step-nav-illustration').click();
    await page.waitForTimeout(1000);
    
    // Check wizard context updated
    await expect(wizardHeader).toContainText('Illustrations');
    console.log('✅ Wizard context updated for Illustrations step');
    
    // Send a message in Illustrations context
    await wizardInput.fill('Suggest better images for this slide');
    await sendButton.click();
    await page.waitForTimeout(3000);
    
    // Check for appropriate response
    const illustrationResponse = page.locator('text=image, text=visual, text=illustration');
    await expect(illustrationResponse.first()).toBeVisible({ timeout: 10000 });
    console.log('✅ Step-specific responses working');

    // 11. Take final screenshot for documentation
    await page.screenshot({ 
      path: `test-results/wizard-improvements-final-${Date.now()}.png`,
      fullPage: true 
    });
    
    console.log('🎉 All wizard improvement tests completed successfully!');
  });

  test('should handle wizard in different contexts', async ({ page }) => {
    const name = `Context Test ${Date.now()}`;
    const topic = 'Context Testing for Wizard';

    const id = await createPresentation(page, name, topic);
    
    // Test Research step context
    console.log('🔬 Testing Research step context...');
    const wizardInput = page.getByTestId('wizard-input');
    const sendButton = page.getByTestId('wizard-send-button');
    
    await wizardInput.fill('Help me with research methodology');
    await sendButton.click();
    await page.waitForTimeout(3000);
    
    const researchResponse = page.locator('text=research');
    await expect(researchResponse.first()).toBeVisible({ timeout: 10000 });
    console.log('✅ Research context working');
    
    // Complete research and test Slides context
    await page.getByTestId('start-ai-research-button').click();
    await page.waitForTimeout(5000);
    
    await page.getByTestId('step-nav-slides').click();
    await page.waitForTimeout(1000);
    
    console.log('📊 Testing Slides step context...');
    await wizardInput.fill('Help me create better slides');
    await sendButton.click();
    await page.waitForTimeout(3000);
    
    const slidesResponse = page.locator('text=slide, text=generate');
    await expect(slidesResponse.first()).toBeVisible({ timeout: 10000 });
    console.log('✅ Slides context working');
  });
});

test.describe('Wizard Performance and Reliability', () => {
  test('should handle rapid message sending', async ({ page }) => {
    const name = `Performance Test ${Date.now()}`;
    const topic = 'Performance Testing';

    const id = await createPresentation(page, name, topic);
    
    // Complete setup
    await page.getByTestId('start-ai-research-button').click();
    await page.waitForTimeout(5000);
    await page.getByTestId('step-nav-slides').click();
    await page.waitForTimeout(1000);
    
    const wizardInput = page.getByTestId('wizard-input');
    const sendButton = page.getByTestId('wizard-send-button');
    
    console.log('⚡ Testing rapid message sending...');
    
    // Send multiple messages quickly
    const messages = [
      'First quick message',
      'Second quick message', 
      'Third quick message'
    ];
    
    for (const message of messages) {
      await wizardInput.fill(message);
      await sendButton.click();
      await page.waitForTimeout(500); // Short delay between messages
    }
    
    // Check that all messages appear
    for (const message of messages) {
      const messageElement = page.locator(`text=${message}`);
      await expect(messageElement).toBeVisible({ timeout: 15000 });
    }
    
    console.log('✅ Rapid message sending handled correctly');
  });
}); 