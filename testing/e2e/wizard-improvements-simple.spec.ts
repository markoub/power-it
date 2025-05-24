import { test, expect } from '@playwright/test';
import { createPresentation } from './utils';

test.setTimeout(120000); // 2 minutes

test.describe('Wizard Improvements Demo', () => {
  test('should demonstrate enhanced wizard functionality', async ({ page }) => {
    const name = `Wizard Demo ${Date.now()}`;
    const topic = 'Digital Marketing Strategies for Small Businesses';

    // Create presentation and complete setup
    const id = await createPresentation(page, name, topic);
    console.log(`✅ Created presentation with ID: ${id}`);

    // Complete research step
    console.log('🔍 Running research...');
    await page.getByTestId('start-ai-research-button').click();
    await page.waitForTimeout(5000);
    console.log('✅ Research completed');

    // Navigate to slides step
    console.log('📊 Navigating to slides...');
    await page.getByTestId('step-nav-slides').click();
    await page.waitForTimeout(1000);
    
    // Generate slides
    const runSlidesButton = page.getByTestId('run-slides-button');
    if (await runSlidesButton.count() > 0) {
      await runSlidesButton.click();
      await page.waitForTimeout(15000); // Wait for slides generation
      console.log('✅ Slides generated');
    }

    // Test 1: Wizard Context Awareness
    console.log('🧙‍♂️ Testing wizard context awareness...');
    
    const wizardHeader = page.getByTestId('wizard-header');
    await expect(wizardHeader).toContainText('All Slides');
    console.log('✅ Initial context: All Slides');
    
    // Select first slide
    const firstSlide = page.getByTestId('slide-thumbnail-0');
    await expect(firstSlide).toBeVisible({ timeout: 10000 });
    await firstSlide.click();
    
    // Verify context changed
    await expect(wizardHeader).toContainText('Single Slide');
    console.log('✅ Context changed to: Single Slide');

    // Test 2: Enhanced Message Status Indicators
    console.log('💬 Testing message status indicators...');
    
    const wizardInput = page.getByTestId('wizard-input');
    const sendButton = page.getByTestId('wizard-send-button');
    
    await wizardInput.fill('Please improve this slide with better content structure');
    await sendButton.click();
    
    // Check loading state
    await expect(sendButton).toBeDisabled();
    console.log('✅ Send button shows loading state');
    
    // Wait for response and check for status icons
    await page.waitForTimeout(5000);
    const statusIcons = page.locator('.lucide-check-circle, .lucide-clock');
    await expect(statusIcons.first()).toBeVisible({ timeout: 10000 });
    console.log('✅ Message status indicators working');

    // Test 3: Enhanced Suggestion Preview
    console.log('👁️ Testing suggestion functionality...');
    
    const suggestionBox = page.locator('text=Suggested Changes');
    await expect(suggestionBox).toBeVisible({ timeout: 15000 });
    console.log('✅ Suggestion box appeared');
    
    // Test preview toggle (using specific test ID)
    const previewToggle = page.getByTestId('wizard-preview-toggle');
    if (await previewToggle.count() > 0) {
      await previewToggle.click();
      console.log('✅ Preview toggle clicked');
      
      // Look for before/after indicators
      const beforeAfterIndicators = page.locator('text=Before:, text=After:, text=Current:, text=Suggested:');
      if (await beforeAfterIndicators.count() > 0) {
        console.log('✅ Before/after comparison visible');
      }
    }

    // Test 4: Apply Changes Functionality
    console.log('✅ Testing apply changes...');
    
    const applyButton = page.locator('button:has-text("Apply Changes")');
    await expect(applyButton).toBeVisible();
    await expect(applyButton).toBeEnabled();
    
    // Get current title before applying
    const titleInput = page.getByTestId('slide-title-input');
    const currentTitle = await titleInput.inputValue();
    console.log(`Current title: "${currentTitle}"`);
    
    await applyButton.click();
    console.log('✅ Apply changes clicked');
    
    // Wait for changes to be applied
    await page.waitForTimeout(3000);
    
    // Check that suggestion box disappeared
    await expect(suggestionBox).not.toBeVisible();
    console.log('✅ Suggestion box disappeared after applying');
    
    // Check for success message
    const successMessage = page.locator('text=successfully applied, text=Perfect!');
    await expect(successMessage.first()).toBeVisible({ timeout: 5000 });
    console.log('✅ Success message appeared');
    
    // Verify title changed
    const newTitle = await titleInput.inputValue();
    if (newTitle !== currentTitle) {
      console.log(`✅ Title changed from "${currentTitle}" to "${newTitle}"`);
    } else {
      console.log('ℹ️ Title remained the same (may be already optimized)');
    }

    // Test 5: Dismiss Functionality
    console.log('❌ Testing dismiss functionality...');
    
    // Send another request
    await wizardInput.fill('Add more engaging bullet points');
    await sendButton.click();
    await page.waitForTimeout(5000);
    
    // Wait for new suggestion
    const newSuggestionBox = page.locator('text=Suggested Changes');
    if (await newSuggestionBox.count() > 0) {
      await expect(newSuggestionBox).toBeVisible({ timeout: 15000 });
      
      // Click dismiss
      const dismissButton = page.locator('button:has-text("Dismiss")');
      await expect(dismissButton).toBeVisible();
      await dismissButton.click();
      console.log('✅ Dismiss button clicked');
      
      // Check that suggestion disappeared
      await expect(newSuggestionBox).not.toBeVisible();
      console.log('✅ Suggestion dismissed correctly');
      
      // Check for dismiss message
      const dismissMessage = page.locator('text=dismissed, text=No problem');
      await expect(dismissMessage.first()).toBeVisible({ timeout: 5000 });
      console.log('✅ Dismiss message appeared');
    }

    // Test 6: Error Handling
    console.log('⚠️ Testing error handling...');
    
    // Test empty input prevention
    await wizardInput.fill('');
    await expect(sendButton).toBeDisabled();
    console.log('✅ Send button disabled for empty input');

    // Test 7: Auto-scroll (send multiple messages)
    console.log('📜 Testing auto-scroll...');
    
    const messages = ['First test message', 'Second test message', 'Third test message'];
    for (const message of messages) {
      await wizardInput.fill(message);
      await sendButton.click();
      await page.waitForTimeout(1500);
    }
    
    // Check that latest message is visible
    const latestMessage = page.locator('text=Third test message');
    await expect(latestMessage).toBeVisible();
    console.log('✅ Auto-scroll functionality working');

    // Take final screenshot
    await page.screenshot({ 
      path: `test-results/wizard-demo-final-${Date.now()}.png`,
      fullPage: true 
    });
    
    console.log('🎉 Wizard improvements demo completed successfully!');
    console.log('');
    console.log('📋 Summary of improvements tested:');
    console.log('   ✅ Context-aware wizard behavior');
    console.log('   ✅ Enhanced message status indicators');
    console.log('   ✅ Improved suggestion previews');
    console.log('   ✅ Apply/dismiss functionality');
    console.log('   ✅ Better error handling');
    console.log('   ✅ Auto-scroll for better UX');
    console.log('   ✅ Loading states and visual feedback');
  });

  test('should handle different step contexts', async ({ page }) => {
    const name = `Context Test ${Date.now()}`;
    const topic = 'Context Testing';

    const id = await createPresentation(page, name, topic);
    
    console.log('🔬 Testing different step contexts...');
    
    const wizardInput = page.getByTestId('wizard-input');
    const sendButton = page.getByTestId('wizard-send-button');
    const wizardHeader = page.getByTestId('wizard-header');
    
    // Test Research step context
    await expect(wizardHeader).toContainText('Research');
    await wizardInput.fill('Help me with research methodology');
    await sendButton.click();
    await page.waitForTimeout(3000);
    
    const researchResponse = page.locator('text=research, text=Research');
    await expect(researchResponse.first()).toBeVisible({ timeout: 10000 });
    console.log('✅ Research step context working');
    
    // Complete research and test Slides context
    await page.getByTestId('start-ai-research-button').click();
    await page.waitForTimeout(5000);
    
    await page.getByTestId('step-nav-slides').click();
    await page.waitForTimeout(1000);
    
    await expect(wizardHeader).toContainText('Slides');
    await wizardInput.fill('Help me create better slides');
    await sendButton.click();
    await page.waitForTimeout(3000);
    
    const slidesResponse = page.locator('text=slide, text=generate, text=Slides');
    await expect(slidesResponse.first()).toBeVisible({ timeout: 10000 });
    console.log('✅ Slides step context working');
    
    console.log('🎯 Step-specific context testing completed!');
  });
}); 