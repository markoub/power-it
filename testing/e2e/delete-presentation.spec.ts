import { test, expect } from '@playwright/test';
import { createPresentation, goToPresentationsPage, waitForNetworkIdle } from './utils';

test.describe('Delete Presentation', () => {
  test('should delete a presentation from the list', async ({ page }) => {
    const name = `Delete Test ${Date.now()}`;
    const topic = 'Test Topic';

    const id = await createPresentation(page, name, topic);

    await goToPresentationsPage(page);
    await waitForNetworkIdle(page);

    const card = page.getByTestId(`presentation-card-${id}`);
    await expect(card).toBeVisible();

    // Accept the confirmation dialog
    page.once('dialog', async (dialog) => {
      expect(dialog.message()).toContain('Are you sure');
      await dialog.accept();
    });

    await card.getByTestId('delete-presentation-button').click();

    await expect(card).not.toBeVisible({ timeout: 5000 });
  });

  test('should delete multiple presentations at once', async ({ page }) => {
    const id1 = await createPresentation(page, `Multi Delete 1 ${Date.now()}`, 'Topic A');
    const id2 = await createPresentation(page, `Multi Delete 2 ${Date.now()}`, 'Topic B');

    await goToPresentationsPage(page);
    await waitForNetworkIdle(page);

    await page.getByTestId('view-list-button').click();

    const row1 = page.getByTestId(`presentation-row-${id1}`);
    const row2 = page.getByTestId(`presentation-row-${id2}`);
    await expect(row1).toBeVisible();
    await expect(row2).toBeVisible();

    await row1.getByTestId('select-presentation-checkbox').check();
    await row2.getByTestId('select-presentation-checkbox').check();

    page.once('dialog', async (dialog) => {
      await dialog.accept();
    });

    await page.getByTestId('delete-selected-button').click();

    await expect(row1).not.toBeVisible({ timeout: 5000 });
    await expect(row2).not.toBeVisible({ timeout: 5000 });
  });
});
