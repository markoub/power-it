import { test, expect } from '@playwright/test';
import { createPresentation, goToPresentationsPage } from '../utils';

test.describe('Delete Presentation', () => {
  test('should delete a presentation from the list', async ({ page }) => {
    const name = `Delete Test ${Date.now()}`;
    const topic = 'Test Topic';

    const id = await createPresentation(page, name, topic);

    await goToPresentationsPage(page);

    // All presentations should be visible on the homepage now
    const card = page.getByTestId(`presentation-card-${id}`);
    await expect(card).toBeVisible();

    // Click delete button
    await card.getByTestId('delete-presentation-button').click();
    
    // Wait for the AlertDialog to appear
    const deleteDialog = page.getByRole('alertdialog');
    await expect(deleteDialog).toBeVisible();
    
    // Verify the dialog content
    await expect(deleteDialog.getByText('Delete Presentation')).toBeVisible();
    await expect(deleteDialog.getByText('Are you sure you want to delete this presentation?')).toBeVisible();
    
    // Click the Delete button in the dialog and wait for the API response
    const [deleteResponse] = await Promise.all([
      page.waitForResponse(resp => resp.url().includes(`/presentations/${id}`) && resp.request().method() === 'DELETE'),
      deleteDialog.getByRole('button', { name: 'Delete' }).click()
    ]);

    await expect(card).not.toBeVisible();
  });

  test('should delete multiple presentations at once', async ({ page }) => {
    const id1 = await createPresentation(page, `Multi Delete 1 ${Date.now()}`, 'Topic A');
    const id2 = await createPresentation(page, `Multi Delete 2 ${Date.now()}`, 'Topic B');

    await goToPresentationsPage(page);

    // All presentations should be visible and view controls should be available
    await expect(page.getByTestId('view-list-button')).toBeVisible();
    await page.getByTestId('view-list-button').click();

    const row1 = page.getByTestId(`presentation-row-${id1}`);
    const row2 = page.getByTestId(`presentation-row-${id2}`);
    await expect(row1).toBeVisible();
    await expect(row2).toBeVisible();

    await row1.getByTestId('select-presentation-checkbox').check();
    await row2.getByTestId('select-presentation-checkbox').check();

    // Click delete selected button
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

    await expect(row1).not.toBeVisible();
    await expect(row2).not.toBeVisible();
  });
});
