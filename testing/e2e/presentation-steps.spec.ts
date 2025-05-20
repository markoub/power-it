import { test, expect } from '@playwright/test';
import { waitForNetworkIdle, createPresentation, runStepAndWaitForCompletion, verifyStepDependencies, getStepStatus } from './utils';

/**
 * End-to-end test covering the full presentation workflow
 */

test.describe('Presentation Workflow', () => {
  test('should run steps sequentially', async ({ page }) => {
    const name = `E2E Workflow ${Date.now()}`;

    // Navigate to home and ensure page is ready
    await page.goto('http://localhost:3000');
    await waitForNetworkIdle(page);

    // Create a new presentation via the helper
    await createPresentation(page, name, 'Automation testing');

    // Should end up on the edit page
    await expect(page).toHaveURL(/\/edit\/\d+/);

    // Run slides generation step
    await runStepAndWaitForCompletion(page, 'slides', 60000);
    expect(await verifyStepDependencies(page)).toBe(true);
    expect(await getStepStatus(page, 'slides')).toMatch(/completed|processing/);

    // Continue with images step
    await page.getByTestId('continue-button').click();
    await runStepAndWaitForCompletion(page, 'images', 60000);
    expect(await verifyStepDependencies(page)).toBe(true);
    expect(await getStepStatus(page, 'images')).toMatch(/completed|processing/);

    // Continue to compiled step
    await page.getByTestId('continue-button').click();
    await page.waitForTimeout(1000);
    expect(await getStepStatus(page, 'compiled')).toMatch(/pending|processing|completed/);

    // Continue to PPTX step
    await page.getByTestId('continue-button').click();
    await page.waitForTimeout(1000);
    await expect(page.getByTestId('export-pptx-button')).toBeVisible();
  });
});
