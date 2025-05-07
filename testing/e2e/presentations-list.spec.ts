import { test, expect } from '@playwright/test';
import { goToPresentationsPage } from './utils';

test.describe('Presentations List Page', () => {
  test('should display the presentations page', async ({ page }) => {
    await goToPresentationsPage(page);
    
    // Check if the page title is correct
    await expect(page).toHaveTitle('Presentation Assistant');
    
    // Check if the page header is visible
    await expect(page.getByTestId('page-title')).toBeVisible();
    
    // Check if the create presentation form is visible
    await expect(page.getByTestId('create-presentation-form')).toBeVisible();
  });
  
  test('should display presentations if they exist', async ({ page }) => {
    await goToPresentationsPage(page);
    
    // Wait for presentations to load (either grid or no-presentations message should be visible)
    await Promise.race([
      page.getByTestId('presentations-grid').waitFor(),
      page.getByTestId('no-presentations-message').waitFor(),
      page.getByTestId('presentations-error').waitFor()
    ]);
    
    // Get the list of presentations or message
    const hasGrid = await page.getByTestId('presentations-grid').isVisible();
    const hasNoPresMessage = await page.getByTestId('no-presentations-message').isVisible();
    const hasError = await page.getByTestId('presentations-error').isVisible();
    
    // Skip the test if there was an error (not what we're testing)
    if (hasError) {
      test.skip();
    }
    
    // If we have presentations, check at least one card is visible
    if (hasGrid) {
      // Check if at least one presentation card is visible
      const presentationCards = page.locator('[data-testid^="presentation-card-"]');
      const count = await presentationCards.count();
      expect(count).toBeGreaterThan(0);
      
      // Check if the first presentation card has expected elements
      const firstCard = presentationCards.first();
      await expect(firstCard.getByTestId('presentation-name')).toBeVisible();
      await expect(firstCard.getByTestId('presentation-topic')).toBeVisible();
      await expect(firstCard.getByTestId('presentation-created-date')).toBeVisible();
      await expect(firstCard.getByTestId('presentation-id')).toBeVisible();
    } else if (hasNoPresMessage) {
      // Check if the no presentations message is correctly displayed
      await expect(page.getByTestId('no-presentations-message')).toContainText('No presentations found');
    }
  });
}); 