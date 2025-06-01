import { test, expect } from '@playwright/test';
import { createPresentation, startAIResearch, waitForResearchCompletion } from './utils';

test.describe('Debug Research Apply', () => {
  test('debug why research apply is not working', async ({ page }) => {
    // Override offline mode for this test
    test.slow(); // This test uses real APIs
    
    // Set viewport to ensure wizard is visible
    await page.setViewportSize({ width: 1400, height: 900 });
    
    // Enable console logging
    page.on('console', msg => {
      if (msg.type() === 'log' || msg.type() === 'info') {
        console.log('PAGE LOG:', msg.text());
      }
    });
    
    // Monitor network requests to the wizard endpoint
    page.on('request', request => {
      if (request.url().includes('/wizard')) {
        console.log('🌐 Wizard Request:', {
          url: request.url(),
          method: request.method(),
          postData: request.postData()
        });
      }
    });
    
    page.on('response', async response => {
      if (response.url().includes('/wizard')) {
        try {
          const data = await response.json();
          console.log('🌐 Wizard Response:', JSON.stringify(data, null, 2));
          
          // Store in window for later access
          await page.evaluate((wizardResponse) => {
            (window as any).lastWizardResponse = wizardResponse;
          }, data);
        } catch (e) {
          console.log('🌐 Wizard Response Error:', response.status(), await response.text());
        }
      }
    });
    
    // Create a presentation
    const presentationId = await createPresentation(
      page, 
      'Debug Research Apply Test', 
      'Blockchain Technology Fundamentals'
    );
    
    // Start and complete research
    await startAIResearch(page);
    await waitForResearchCompletion(page);
    
    // Make sure research context is visible
    const researchContext = page.locator('text="Research Context"').first();
    await expect(researchContext).toBeVisible();
    
    // Send a modification request
    console.log('📝 Sending wizard request...');
    const wizardInput = page.locator('[data-testid="wizard-input"]');
    await wizardInput.fill('Add more information about smart contracts and their applications');
    await wizardInput.press('Enter');
    
    // Wait for response
    console.log('⏳ Waiting for wizard response...');
    await page.waitForSelector('[data-testid="wizard-message-assistant"]:last-child', { timeout: 10000 });
    
    // Check if suggestion appeared
    const wizardSuggestion = page.locator('[data-testid="wizard-suggestion"]');
    const hasSuggestion = await wizardSuggestion.isVisible();
    console.log(`📦 Wizard suggestion visible: ${hasSuggestion}`);
    
    if (hasSuggestion) {
      // Check what's in the suggestion
      const suggestionText = await wizardSuggestion.textContent();
      console.log('📄 Suggestion content preview:', suggestionText?.substring(0, 200));
      
      // Look for apply button
      const applyButton = page.locator('[data-testid="wizard-apply-button"]');
      const applyVisible = await applyButton.isVisible();
      console.log(`🔘 Apply button visible: ${applyVisible}`);
      
      if (applyVisible) {
        // Get current research content
        const researchContentBefore = await page.locator('[data-testid="ai-research-content"]').textContent();
        console.log('📖 Research content before (first 200 chars):', researchContentBefore?.substring(0, 200));
        
        // Click apply
        console.log('👆 Clicking apply button...');
        await applyButton.click();
        
        // Wait for changes
        await page.waitForLoadState('networkidle');
        
        // Check if research content changed
        const researchContentAfter = await page.locator('[data-testid="ai-research-content"]').textContent();
        console.log('📖 Research content after (first 200 chars):', researchContentAfter?.substring(0, 200));
        
        // Verify change
        const contentChanged = researchContentBefore !== researchContentAfter;
        console.log(`✅ Content changed: ${contentChanged}`);
        
        // Also check for toast notification
        const toast = page.locator('text="Changes applied"').or(page.locator('text="research has been updated"'));
        const toastVisible = await toast.isVisible().catch(() => false);
        console.log(`🍞 Toast notification visible: ${toastVisible}`);
        
        // Monitor save research API call
        const saveRequests = await page.evaluate(() => {
          return (window as any).saveResearchCalls || [];
        });
        console.log('💾 Save research API calls:', saveRequests);
        
        expect(contentChanged || toastVisible).toBe(true);
      }
    } else {
      // No suggestion, check for error or response
      const assistantMessages = await page.locator('[data-testid="wizard-message-assistant"]').all();
      console.log(`💬 Assistant messages count: ${assistantMessages.length}`);
      
      if (assistantMessages.length > 1) {
        const lastMessage = await assistantMessages[assistantMessages.length - 1].textContent();
        console.log('💬 Last assistant message:', lastMessage);
      }
    }
    
    // Get the last wizard response from window
    const wizardResponse = await page.evaluate(() => (window as any).lastWizardResponse);
    console.log('📊 Final wizard response:', wizardResponse);
    
    // Wait a bit more to see if anything updates
    await page.waitForLoadState('networkidle');
    
    // Check one more time for suggestions
    const finalSuggestionCheck = await page.locator('[data-testid="wizard-suggestion"]').isVisible();
    console.log(`📦 Final suggestion check: ${finalSuggestionCheck}`);
    
    // Take screenshot for debugging
    await page.screenshot({ path: 'wizard-research-apply-debug.png', fullPage: true });
  });
});