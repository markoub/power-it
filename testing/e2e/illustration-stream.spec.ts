import { test, expect } from '@playwright/test';
import { createPresentation, runStepAndWaitForCompletion } from './utils';

// Increase timeout for slower environments
test.setTimeout(120000);

test('images appear while generation is in progress', async ({ page }) => {
  const name = `Stream Test ${Date.now()}`;
  const id = await createPresentation(page, name, 'stream topic');

  // Ensure slides exist
  await runStepAndWaitForCompletion(page, 'slides');

  // Start generating images
  const runButton = page.getByTestId('run-images-button');
  await runButton.click();
  await expect(runButton).toBeDisabled();

  // Wait for at least one image to appear
  await page.waitForFunction(() => document.querySelectorAll('img').length > 0, {}, { timeout: 15000 });

  // Button may still be disabled if generation not finished yet
  const stillDisabled = await runButton.isDisabled();
  expect(stillDisabled).toBeTruthy();
});
