/**
 * Delete Presentation E2E Tests
 * 
 * These tests verify the deletion functionality for presentations.
 * They use pre-seeded test data from the test database.
 * 
 * IMPORTANT: These tests require proper setup:
 * 1. Start the test backend: cd backend && POWERIT_ENV=test ./venv/bin/python run_api.py
 * 2. Start the test frontend: cd frontend && NEXT_PUBLIC_API_URL=http://localhost:8001 npm run dev -- -p 3001
 * 3. Run tests: PLAYWRIGHT_BASE_URL=http://localhost:3001 npm test e2e/delete-presentation.spec.ts
 * 
 * The database is reset before each test to ensure a clean state.
 * 
 * Test data used:
 * - Fresh Test Presentation 1 (ID: 1) - for single deletion test
 * - Fresh Test Presentation 3 (ID: 3) - for multiple deletion test
 * - Fresh Test Presentation 4 (ID: 4) - for multiple deletion test
 */
import { test, expect } from '@playwright/test';
import { goToPresentationsPage, resetTestDatabase } from './utils';
import { getTestPresentation, TEST_CATEGORIES, getApiUrl } from '../test-config';

test.describe('Delete Presentation', () => {
  // Reset database before each test to ensure clean state
  test.beforeEach(async ({ page }) => {
    // Reset the test database to ensure all test presentations are available
    const apiUrl = getApiUrl();
    try {
      const response = await page.request.post(`${apiUrl}/test/reset-database`);
      if (!response.ok()) {
        console.warn('Failed to reset test database:', response.status());
      }
    } catch (error) {
      console.warn('Error resetting test database:', error);
    }
  });
  test('should delete a presentation from the list', async ({ page }) => {
    // Use Fresh Test Presentation 1 for single deletion
    const testPresentation = getTestPresentation(TEST_CATEGORIES.FRESH, 0); // index 0 = Fresh Test Presentation 1
    if (!testPresentation) {
      throw new Error('Test presentation not found');
    }

    await goToPresentationsPage(page);

    // With 32 presentations (10 per page), Fresh Test Presentation 1 (ID: 1) is on page 4
    // Navigate to the page where the presentation is located
    let card = page.getByTestId(`presentation-card-${testPresentation.id}`);
    let attempts = 0;
    
    // Try to find the presentation, navigating through pages if needed
    while (attempts < 5) {
      try {
        await expect(card).toBeVisible({ timeout: 2000 });
        break; // Found it!
      } catch {
        // Not on this page, try next page
        const nextButton = page.getByLabel('Go to next page');
        if (await nextButton.isEnabled()) {
          await nextButton.click();
          await page.waitForLoadState('networkidle');
          attempts++;
        } else {
          throw new Error(`Presentation ${testPresentation.id} not found after checking all pages`);
        }
      }
    }

    // Click delete button using data-testid
    await card.getByTestId('delete-presentation-button').click();
    
    // Wait for the AlertDialog to appear
    const deleteDialog = page.getByRole('alertdialog');
    await expect(deleteDialog).toBeVisible();
    
    // Verify the dialog content
    await expect(deleteDialog.getByText('Delete Presentation')).toBeVisible();
    await expect(deleteDialog.getByText('Are you sure you want to delete this presentation?')).toBeVisible();
    
    // Click the Delete button in the dialog and wait for the API response
    const [deleteResponse] = await Promise.all([
      page.waitForResponse(resp => resp.url().includes(`/presentations/${testPresentation.id}`) && resp.request().method() === 'DELETE'),
      deleteDialog.getByRole('button', { name: 'Delete' }).click()
    ]);

    // Verify the card is no longer visible
    await expect(card).not.toBeVisible();
  });

  test('should delete multiple presentations at once', async ({ page }) => {
    // Use Fresh Test Presentation 3 and 4 for multiple deletion (not 1 which was deleted in previous test)
    const testPresentation1 = getTestPresentation(TEST_CATEGORIES.FRESH, 2); // index 2 = Fresh Test Presentation 3
    const testPresentation2 = getTestPresentation(TEST_CATEGORIES.FRESH, 3); // index 3 = Fresh Test Presentation 4
    
    if (!testPresentation1 || !testPresentation2) {
      throw new Error('Test presentations not found');
    }

    await goToPresentationsPage(page);

    // Switch to list view to enable multiple selection
    await expect(page.getByTestId('view-list-button')).toBeVisible();
    await page.getByTestId('view-list-button').click();

    // Find presentation rows, navigating through pages if needed
    let row1 = page.getByTestId(`presentation-row-${testPresentation1.id}`);
    let row2 = page.getByTestId(`presentation-row-${testPresentation2.id}`);
    let attempts = 0;
    
    // Try to find both presentations, navigating through pages if needed
    while (attempts < 5) {
      const row1Visible = await row1.isVisible().catch(() => false);
      const row2Visible = await row2.isVisible().catch(() => false);
      
      if (row1Visible && row2Visible) {
        break; // Found both!
      } else {
        // Not on this page, try next page
        const nextButton = page.getByLabel('Go to next page');
        if (await nextButton.isEnabled()) {
          await nextButton.click();
          await page.waitForLoadState('networkidle');
          attempts++;
        } else {
          throw new Error(`Presentations ${testPresentation1.id} and ${testPresentation2.id} not found after checking all pages`);
        }
      }
    }
    
    await expect(row1).toBeVisible();
    await expect(row2).toBeVisible();

    // Select both presentations using data-testid
    await row1.getByTestId('select-presentation-checkbox').check();
    await row2.getByTestId('select-presentation-checkbox').check();

    // Click delete selected button using data-testid
    await page.getByTestId('delete-selected-button').click();
    
    // Wait for the AlertDialog to appear
    const deleteDialog = page.getByRole('alertdialog');
    await expect(deleteDialog).toBeVisible();
    
    // Verify the dialog content
    await expect(deleteDialog.getByText('Delete Selected Presentations')).toBeVisible();
    await expect(deleteDialog.getByText('Are you sure you want to delete 2 selected presentations?')).toBeVisible();
    
    // Click the Delete button in the dialog and wait for the API response
    const [deleteResponse] = await Promise.all([
      page.waitForResponse(resp => resp.url().includes('/presentations') && resp.request().method() === 'DELETE'),
      deleteDialog.getByRole('button', { name: 'Delete 2 Presentations' }).click()
    ]);

    // Verify both rows are no longer visible
    await expect(row1).not.toBeVisible();
    await expect(row2).not.toBeVisible();
  });
});
