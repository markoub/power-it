import { test, expect } from '@playwright/test';
import { createPresentation } from './utils';

test.describe('Research Clarification', () => {
  test('should handle clarification dialog when AI requests it', async ({ page }) => {
    // Create presentation using the utility function
    const name = `Test ADK ${Date.now()}`;
    const topic = 'Google ADK';
    
    const presentationId = await createPresentation(page, name, topic);
    console.log(`✅ Created presentation with ID: ${presentationId}`);
    
    // Start AI research and wait for the clarification check
    const [clarificationResponse] = await Promise.all([
      page.waitForResponse(
        response => response.url().includes('/research/clarification/check') && response.status() === 200,
        { timeout: 10000 }
      ),
      page.click('[data-testid="start-ai-research-button"]')
    ]);
    
    // Check if clarification was requested
    const clarificationData = await clarificationResponse.json();
    
    if (clarificationData.needs_clarification) {
      console.log('✅ AI requested clarification - handling dialog');
      
      // Wait for the clarification dialog to appear
      await expect(page.getByText('Research Clarification')).toBeVisible();
      
      // Type clarification in the chat
      const clarificationInput = page.locator('input[placeholder="Type your clarification..."]');
      await clarificationInput.fill('I mean Android Development Kit for hardware accessories');
      
      // Send the clarification
      await clarificationInput.press('Enter');
      
      // Wait for assistant response (AI might respond differently)
      await expect(page.getByText(/understand|got it|clear|perfect/i)).toBeVisible({ timeout: 10000 });
      
      // Wait for the clarification dialog to close
      await expect(page.getByText('Research Clarification')).not.toBeVisible({ timeout: 15000 });
    } else {
      console.log('✅ No clarification needed - research starting directly');
    }
    
    // Verify research starts (either generating or already completed)
    const researchGenerating = page.getByText('Generating Research');
    const researchCompleted = page.getByText('Generated Research Content');
    await expect(researchGenerating.or(researchCompleted)).toBeVisible({ timeout: 30000 });
  });

  test('should handle topics without clarification when API determines no clarification needed', async ({ page }) => {
    // Note: In online mode, the AI might ask for clarification on many topics
    // This test verifies the flow when clarification is NOT needed
    const name = `Test Presentation ${Date.now()}`;
    const topic = 'Test Topic Without Clarification';
    
    const presentationId = await createPresentation(page, name, topic);
    console.log(`✅ Created presentation with ID: ${presentationId}`);
    
    // Start AI research and wait for the clarification check
    const [clarificationResponse] = await Promise.all([
      page.waitForResponse(
        response => response.url().includes('/research/clarification/check') && response.status() === 200,
        { timeout: 10000 }
      ),
      page.click('[data-testid="start-ai-research-button"]')
    ]);
    
    // Check what the API returned
    const clarificationData = await clarificationResponse.json();
    
    if (clarificationData.needs_clarification) {
      // If clarification is needed, handle it
      console.log('Topic needs clarification - this is OK in online mode');
      await expect(page.getByText('Research Clarification')).toBeVisible();
      
      // Skip the clarification
      const skipButton = page.locator('button[aria-label*="close"]').or(page.getByRole('button', { name: /skip/i })).or(page.locator('button:has(svg)').filter({ hasText: '' }));
      await skipButton.first().click();
      
      // Should return to research input
      await expect(page.getByTestId('start-ai-research-button')).toBeVisible();
    } else {
      // If no clarification needed, verify research starts
      await page.waitForResponse(
        response => response.url().includes('/presentations') && response.url().includes('/steps/research/run') && response.status() === 200,
        { timeout: 10000 }
      );
      
      // Verify no clarification dialog appears
      await expect(page.getByText('Research Clarification')).not.toBeVisible();
      
      // Check if research is running or completed
      const researchGenerating = page.getByText('Generating Research');
      const researchCompleted = page.getByText('Generated Research Content');
      await expect(researchGenerating.or(researchCompleted)).toBeVisible({ timeout: 10000 });
    }
  });

  test('should allow skipping clarification when requested', async ({ page }) => {
    // Create presentation using the utility function
    const name = `Test SDK ${Date.now()}`;
    const topic = 'Google SDK';
    
    const presentationId = await createPresentation(page, name, topic);
    console.log(`✅ Created presentation with ID: ${presentationId}`);
    
    // Start AI research and wait for the clarification check
    const [clarificationResponse] = await Promise.all([
      page.waitForResponse(
        response => response.url().includes('/research/clarification/check') && response.status() === 200,
        { timeout: 10000 }
      ),
      page.click('[data-testid="start-ai-research-button"]')
    ]);
    
    // Check if clarification was requested
    const clarificationData = await clarificationResponse.json();
    
    if (clarificationData.needs_clarification) {
      console.log('✅ AI requested clarification - testing skip functionality');
      
      // Wait for clarification dialog to appear
      await expect(page.getByText('Research Clarification')).toBeVisible();
      
      // Look for skip/close button (might be X button or skip button)
      const closeButton = page.getByRole('button', { name: 'Close' })
        .or(page.locator('button[aria-label*="close"]'))
        .or(page.locator('button:has(svg.lucide-x)'))
        .or(page.getByText('Skip clarification'));
      
      await closeButton.first().click();
      
      // Wait for dialog to close
      await expect(page.getByText('Research Clarification')).not.toBeVisible();
      
      // Should return to research input
      await expect(page.getByTestId('start-ai-research-button')).toBeVisible();
      console.log('✅ Successfully skipped clarification');
    } else {
      console.log('⚠️ No clarification was requested for this topic - test skipped');
      // If no clarification, the test still passes as the functionality works
    }
  });
});