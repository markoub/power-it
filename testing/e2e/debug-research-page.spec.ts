import { test, expect } from '@playwright/test';
import { navigateToEditPage } from './utils';

test.describe('Debug Research Page', () => {
  test('debug research page state', async ({ page }) => {
    // Navigate directly to create page and create presentation manually
    await page.goto('http://localhost:3000/create');
    
    // Fill out the basic form
    const uniqueName = `Debug Test ${Date.now()}`;
    await page.getByTestId('presentation-title-input').fill(uniqueName);
    await page.getByTestId('presentation-author-input').fill('Test Author');
    
    // Submit the form and wait for navigation
    const [response] = await Promise.all([
      page.waitForResponse(resp => resp.url().includes('/presentations') && resp.status() === 200),
      page.getByTestId('submit-presentation-button').click()
    ]);
    
    // Verify navigation to edit page
    await expect(page).toHaveURL(/\/edit\/\d+/);
    
    // Check if method selection is visible
    const methodSelection = page.locator('[data-testid="research-method-selection"]');
    if (await methodSelection.isVisible()) {
      console.log('Method selection is visible, proceeding with selection...');
      
      // Select AI research method
      await page.getByTestId('ai-research-option').click();
      
      // Wait for continue button and click it
      const continueButton = page.getByTestId('continue-with-method-button');
      await expect(continueButton).toBeEnabled();
      await continueButton.click();
      
      // Wait for method selection to disappear and AI interface to appear
      await expect(methodSelection).not.toBeVisible();
      await expect(page.getByTestId('ai-research-interface')).toBeVisible();
      
      // Fill in topic
      await page.getByTestId('topic-input').fill('Test Topic');
      
      console.log('✅ Successfully navigated to AI research interface');
    }
    
    // Take a screenshot to see what's on the page
    await page.screenshot({ path: 'debug-research-page.png', fullPage: true });
    
    // Log all elements with data-testid
    const testIds = await page.locator('[data-testid]').all();
    console.log('Found elements with data-testid:');
    for (const element of testIds) {
      const testId = await element.getAttribute('data-testid');
      const isVisible = await element.isVisible();
      console.log(`- ${testId}: ${isVisible ? 'visible' : 'hidden'}`);
    }
    
    // Check if we're in the right state
    const aiInterface = page.locator('[data-testid="ai-research-interface"]');
    const manualInterface = page.locator('[data-testid="manual-research-interface"]');
    const methodSelectionFinal = page.locator('[data-testid="research-method-selection"]');
    
    console.log('Interface states:');
    console.log(`- AI interface visible: ${await aiInterface.isVisible()}`);
    console.log(`- Manual interface visible: ${await manualInterface.isVisible()}`);
    console.log(`- Method selection visible: ${await methodSelectionFinal.isVisible()}`);
    
    // Check for buttons
    const startButton = page.locator('[data-testid="start-ai-research-button"]');
    const updateButton = page.locator('[data-testid="update-research-button"]');
    
    console.log('Button states:');
    console.log(`- Start button visible: ${await startButton.isVisible()}`);
    console.log(`- Update button visible: ${await updateButton.isVisible()}`);
    
    // Check topic input
    const topicInput = page.locator('[data-testid="topic-input"]');
    console.log(`- Topic input visible: ${await topicInput.isVisible()}`);
    if (await topicInput.isVisible()) {
      const topicValue = await topicInput.inputValue();
      console.log(`- Topic value: "${topicValue}"`);
    }
  });
}); 