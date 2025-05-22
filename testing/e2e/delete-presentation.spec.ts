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
});
