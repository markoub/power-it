import { test, expect } from '@playwright/test';
import { waitForNetworkIdle } from './utils';

test.describe('Presentation Creation', () => {

  test('should create a new presentation with minimal info', async ({ page }) => {
    // Navigate to the create page directly instead of clicking through
    await page.goto('http://localhost:3000/create');
    
    // Verify we're on the create page
    await expect(page.getByTestId('page-title')).toContainText('Create New Presentation');
    
    // Wait for form to be visible before interacting
    await expect(page.getByTestId('create-presentation-form')).toBeVisible();
    
    // Fill out the form with just name and author (use timestamp for uniqueness)
    const testTitle = `Test Presentation ${Date.now()}-${Math.random()}`;
    await page.getByTestId('presentation-title-input').fill(testTitle);
    await page.getByTestId('presentation-author-input').fill('Test Author');
    
    // Submit the form
    await page.getByTestId('submit-presentation-button').click();
    
    // Verify we are redirected to the edit page
    await expect(page).toHaveURL(/\/edit\/\d+/);
    
    // On the edit page, we should see the research method selection interface
    await expect(page.getByTestId('research-method-selection')).toBeVisible();
    
    // Should see both AI Research and Manual Research options
    await expect(page.getByTestId('ai-research-option')).toBeVisible();
    await expect(page.getByTestId('manual-research-option')).toBeVisible();
  });

  test('should show validation errors for duplicate names', async ({ page }) => {
    // Navigate directly to the create page
    await page.goto('http://localhost:3000/create');
    
    // Verify we're on the create page
    await expect(page.getByTestId('page-title')).toContainText('Create New Presentation');
    
    // Create a presentation with a specific name first
    const duplicateName = `Duplicate Test ${Date.now()}`;
    await page.getByTestId('presentation-title-input').fill(duplicateName);
    await page.getByTestId('presentation-author-input').fill('Test Author');
    await page.getByTestId('submit-presentation-button').click();
    
    // Should redirect to edit page
    await expect(page).toHaveURL(/\/edit\/\d+/);
    
    // Now go back to create page and try to create another with the same name
    await page.goto('http://localhost:3000/create');
    await page.getByTestId('presentation-title-input').fill(duplicateName);
    await page.getByTestId('presentation-author-input').fill('Test Author 2');
    await page.getByTestId('submit-presentation-button').click();
    
    // Should stay on create page and show error message
    await expect(page).toHaveURL(/\/create/);
    await expect(page.getByTestId('error-message')).toBeVisible();
    await expect(page.getByTestId('error-message')).toContainText('already exists');
    
    // Fix the issue by using a different name
    const uniqueName = `${duplicateName} - Fixed`;
    await page.getByTestId('presentation-title-input').fill(uniqueName);
    await page.getByTestId('submit-presentation-button').click();
    
    // Should now redirect to edit page
    await expect(page).toHaveURL(/\/edit\/\d+/);
  });

  test('should allow selecting AI research method and entering topic', async ({ page }) => {
    // Create a presentation first
    await page.goto('http://localhost:3000/create');
    await expect(page.getByTestId('create-presentation-form')).toBeVisible();
    
    const testTitle = `Test AI Research ${Date.now()}-${Math.random()}`;
    await page.getByTestId('presentation-title-input').fill(testTitle);
    await page.getByTestId('presentation-author-input').fill('Test Author');
    await page.getByTestId('submit-presentation-button').click();
    
    // Wait for edit page
    await expect(page).toHaveURL(/\/edit\/\d+/);
    
    // Should see research method selection
    await expect(page.getByTestId('research-method-selection')).toBeVisible();
    
    // Select AI Research
    await page.getByTestId('ai-research-option').click();
    await page.getByTestId('continue-with-method-button').click();
    
    // Should now see AI research interface
    await expect(page.getByTestId('research-method-interface')).toBeVisible();
    await expect(page.getByTestId('ai-research-interface')).toBeVisible();
    
    // Enter a topic
    await page.getByTestId('topic-input').fill('Artificial Intelligence in Healthcare');
    
    // Should see the start research button
    await expect(page.getByTestId('start-ai-research-button')).toBeVisible();
  });

  test('should allow selecting manual research method and entering content', async ({ page }) => {
    // Create a presentation first
    await page.goto('http://localhost:3000/create');
    await expect(page.getByTestId('create-presentation-form')).toBeVisible();
    
    const testTitle = `Test Manual Research ${Date.now()}-${Math.random()}`;
    await page.getByTestId('presentation-title-input').fill(testTitle);
    await page.getByTestId('presentation-author-input').fill('Test Author');
    await page.getByTestId('submit-presentation-button').click();
    
    // Wait for edit page
    await expect(page).toHaveURL(/\/edit\/\d+/);
    
    // Should see research method selection
    await expect(page.getByTestId('research-method-selection')).toBeVisible();
    
    // Select Manual Research
    await page.getByTestId('manual-research-option').click();
    await page.getByTestId('continue-with-method-button').click();
    
    // Should now see manual research interface
    await expect(page.getByTestId('research-method-interface')).toBeVisible();
    await expect(page.getByTestId('manual-research-interface')).toBeVisible();
    
    // Enter research content
    await page.getByTestId('manual-research-input').fill('This is my manual research content for the presentation. It includes key points about the topic and supporting data.');
    
    // Should see the save research button
    await expect(page.getByTestId('save-manual-research-button')).toBeVisible();
  });
}); 