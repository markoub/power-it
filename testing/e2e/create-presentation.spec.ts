import { test, expect } from '@playwright/test';
import { waitForNetworkIdle, goToPresentationsPage } from './utils';

test.describe('Presentation Creation', () => {

  test('should create a new presentation with AI research method', async ({ page }) => {
    // Navigate to the home page
    await page.goto('http://localhost:3000');
    await waitForNetworkIdle(page);

    // Click on create new presentation button
    await page.getByRole('link', { name: /create new/i }).click();
    
    // Verify we're on the create page
    await expect(page).toHaveURL(/\/create/);
    await expect(page.getByTestId('page-title')).toContainText('Create New Presentation');
    
    // Fill out the form with AI research method
    const testTitle = `Test AI Presentation ${Date.now()}`;
    await page.getByTestId('presentation-title-input').fill(testTitle);
    await page.getByTestId('author-input').fill('Test Author');
    
    // Ensure AI research option is selected (should be default)
    await page.getByTestId('ai-research-option').click();
    
    // Fill out the AI topic
    await page.getByTestId('ai-topic-input').fill('Artificial Intelligence in Healthcare');
    
    // Submit the form
    await page.getByTestId('submit-presentation-button').click();
    
    // Check for success message
    await expect(page.getByText('Presentation created successfully')).toBeVisible();
    
    // Verify we are redirected to the edit page
    await expect(page).toHaveURL(/\/edit\/\d+/);
  });

  test('should create a new presentation with manual research method', async ({ page }) => {
    // Navigate to the home page
    await page.goto('http://localhost:3000');
    await waitForNetworkIdle(page);

    // Click on create new presentation button
    await page.getByRole('link', { name: /create new/i }).click();
    
    // Verify we're on the create page
    await expect(page).toHaveURL(/\/create/);
    
    // Fill out the form with manual research method
    const testTitle = `Test Manual Presentation ${Date.now()}`;
    await page.getByTestId('presentation-title-input').fill(testTitle);
    await page.getByTestId('author-input').fill('Test Author');
    
    // Select manual research option
    await page.getByTestId('manual-research-option').click();
    
    // Fill out the manual research content
    await page.getByTestId('manual-research-input').fill('This is my manual research content for the presentation. It contains detailed information about the topic.');
    
    // Submit the form
    await page.getByTestId('submit-presentation-button').click();
    
    // Check for success message
    await expect(page.getByText('Presentation created successfully')).toBeVisible();
    
    // Verify we are redirected to the edit page
    await expect(page).toHaveURL(/\/edit\/\d+/);
  });

  test('should show validation errors for missing fields', async ({ page }) => {
    // Navigate to the home page
    await page.goto('http://localhost:3000');
    await waitForNetworkIdle(page);

    // Click on create new presentation button
    await page.getByRole('link', { name: /create new/i }).click();
    
    // Try to submit the form without filling required fields
    await page.getByTestId('submit-presentation-button').click();
    
    // Check for validation error (browser's built-in validation)
    // The form should not be submitted
    await expect(page).toHaveURL(/\/create/);
    
    // Verify that we are still on the create page
    await expect(page.getByTestId('page-title')).toContainText('Create New Presentation');
    
    // Fill only the title
    await page.getByTestId('presentation-title-input').fill('Test Presentation');
    await page.getByTestId('submit-presentation-button').click();
    
    // Should still be on create page as topic is required for AI research
    await expect(page).toHaveURL(/\/create/);
    
    // Fill the topic and try again
    await page.getByTestId('ai-topic-input').fill('Test Topic');
    await page.getByTestId('submit-presentation-button').click();
    
    // Now it should succeed and redirect
    await expect(page.getByText('Presentation created successfully')).toBeVisible();
    await expect(page).toHaveURL(/\/edit\/\d+/);
  });
}); 