import { test, expect } from '@playwright/test';
import { goToPresentationsPage, waitForNetworkIdle } from './utils';

test.setTimeout(15000); // 15s timeout for offline mode

test.describe('Presentations List Page', () => {
  test('should display the presentations page correctly', async ({ page }) => {
    await goToPresentationsPage(page);
    
    // Check if the page title is correct
    await expect(page).toHaveTitle('AI Presentation Creator');
    
    // Check if the page header is visible
    await expect(page.getByTestId('page-title')).toBeVisible();
    await expect(page.getByTestId('page-title')).toContainText('AI Presentation Creator');
    
    // Check if the "Create New Presentation" button is visible
    await expect(page.getByTestId('ai-research-button')).toBeVisible();
    await expect(page.getByTestId('ai-research-button')).toContainText('Create New Presentation');
    
    // Check if the presentations section is visible
    await expect(page.getByTestId('presentations-container')).toBeVisible();
    await expect(page.getByTestId('presentations-section-title')).toContainText('Your Presentations');
  });
  
  test('should display pre-seeded presentations', async ({ page }) => {
    await goToPresentationsPage(page);
    
    // Wait for presentations to load
    await page.waitForSelector('[data-testid="presentations-loading"]', { state: 'detached', timeout: 5000 })
      .catch(() => console.log('Loading indicator not found or already gone'));
    
    // With pre-seeded data, we should always have presentations
    await expect(page.getByTestId('presentations-grid')).toBeVisible({ timeout: 5000 });
    
    // Verify we have 10 presentations displayed (first page) out of 12 total
    const presentationCards = page.locator('[data-testid^="presentation-card-"]');
    await expect(presentationCards).toHaveCount(10);
    
    // Verify pagination info shows 12 total
    await expect(page.getByText('Showing 1–10 of 12 presentations')).toBeVisible();
    
    // Check that we have the expected presentations from the first page
    // These are ordered by ID descending, so IDs 12, 11, 10... appear first
    await expect(page.getByText('Manual Research Test 1')).toBeVisible();
    await expect(page.getByText('Complete Test Presentation 1')).toBeVisible();
    await expect(page.getByText('Illustrations Complete Test 1')).toBeVisible();
    
    // Verify at least one presentation card has proper structure
    // Cards should have clickable areas for navigation
  });
  
  test('should navigate to create page when clicking create button', async ({ page }) => {
    await goToPresentationsPage(page);
    
    // Click the main create button in the header
    await page.getByTestId('ai-research-button').click();
    
    // Should navigate to the create page
    await expect(page).toHaveURL(/\/create/);
    
    // Verify we're on the create page
    await expect(page.getByRole('heading', { name: 'Create New Presentation' })).toBeVisible();
  });
  
  test('should navigate to edit page when clicking edit button', async ({ page }) => {
    await goToPresentationsPage(page);
    
    // Wait for presentations to load
    await page.waitForSelector('[data-testid="presentations-loading"]', { state: 'detached', timeout: 5000 })
      .catch(() => {});
    
    // Click edit button on one of the complete presentations (ID 11)
    const firstCard = page.getByTestId('presentation-card-11');
    await firstCard.getByTestId('edit-presentation-button').click();
    
    // Should navigate to edit page
    await expect(page).toHaveURL(/\/edit\/\d+/);
    
    // Verify we're on the edit page
    await expect(page.getByTestId('step-nav-research')).toBeVisible();
  });
  
  test('should show delete confirmation when clicking delete button', async ({ page }) => {
    await goToPresentationsPage(page);
    
    // Wait for presentations to load
    await page.waitForSelector('[data-testid="presentations-loading"]', { state: 'detached', timeout: 5000 })
      .catch(() => {});
    
    // Click delete button on one of the presentations on the first page (ID 12)
    const firstCard = page.getByTestId('presentation-card-12');
    await firstCard.getByTestId('delete-presentation-button').click();
    
    // Should show confirmation dialog - use selector for the Radix UI alert dialog
    await expect(page.locator('[role="alertdialog"]')).toBeVisible({ timeout: 5000 });
    
    // Check for confirmation text
    await expect(page.locator('[role="alertdialog"]')).toContainText('Delete Presentation');
    await expect(page.locator('[role="alertdialog"]')).toContainText('Are you sure you want to delete this presentation?');
    
    // Cancel the deletion - find button by text within the dialog
    await page.locator('[role="alertdialog"] button').filter({ hasText: 'Cancel' }).click();
    
    // Dialog should close
    await expect(page.locator('[role="alertdialog"]')).not.toBeVisible();
  });
  
  test('should switch between grid and list views', async ({ page }) => {
    await goToPresentationsPage(page);
    
    // Wait for presentations to load
    await page.waitForSelector('[data-testid="presentations-loading"]', { state: 'detached', timeout: 5000 })
      .catch(() => {});
    
    // Check which view is currently active
    const gridVisible = await page.getByTestId('presentations-grid').isVisible().catch(() => false);
    const tableVisible = await page.getByTestId('presentations-table').isVisible().catch(() => false);
    
    if (gridVisible) {
      // Currently in grid view - switch to list
      await page.getByTestId('view-list-button').click();
      
      // Should switch to list view (table)
      await expect(page.getByTestId('presentations-table')).toBeVisible();
      await expect(page.getByTestId('presentations-grid')).not.toBeVisible();
      
      // Switch back to grid view
      await page.getByTestId('view-grid-button').click();
      await expect(page.getByTestId('presentations-grid')).toBeVisible();
      await expect(page.getByTestId('presentations-table')).not.toBeVisible();
    } else if (tableVisible) {
      // Currently in list view - switch to grid
      await page.getByTestId('view-grid-button').click();
      
      // Should switch to grid view
      await expect(page.getByTestId('presentations-grid')).toBeVisible();
      await expect(page.getByTestId('presentations-table')).not.toBeVisible();
      
      // Switch back to list view
      await page.getByTestId('view-list-button').click();
      await expect(page.getByTestId('presentations-table')).toBeVisible();
      await expect(page.getByTestId('presentations-grid')).not.toBeVisible();
    } else {
      throw new Error('Neither grid nor list view is visible');
    }
  });
});