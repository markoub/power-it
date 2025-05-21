import { test, expect } from '@playwright/test';
import { createPresentation, runStepAndWaitForCompletion } from './utils';

test.setTimeout(120000);

test.describe('Wizard Slide Modification', () => {
  test('should request slide modification and apply it', async ({ page }) => {
    const name = `Wizard Test ${Date.now()}`;
    const topic = 'Offline wizard topic';

    const id = await createPresentation(page, name, topic);

    await runStepAndWaitForCompletion(page, 'slides');

    // Select first slide thumbnail
    const firstCard = page.locator('.slide-card').first();
    await firstCard.click();

    // Find wizard textarea and send a prompt
    const textarea = page.getByPlaceholder('Ask the AI wizard for help...');
    await textarea.fill('Improve this slide');
    await textarea.press('Enter');

    // Wait for suggestion box
    await page.getByText('Suggested Changes').waitFor({ timeout: 10000 });

    // Apply changes
    await page.getByRole('button', { name: 'Apply Changes' }).click();

    // Verify slide title updated with "Modified" prefix
    await expect(firstCard).toContainText('Modified');
  });
});
