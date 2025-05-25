import { test, expect } from '@playwright/test';

test.describe('Wizard Slide Management', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to a presentation with slides
    await page.goto('http://localhost:3000/edit/68');
    
    // Wait for the page to load
    await page.waitForLoadState('networkidle');
    
    // Navigate to slides step by clicking on the Slides step circle
    await page.locator('text=Slides').first().click();
    await page.waitForTimeout(5000);
  });

  test('should add a new slide via wizard', async ({ page }) => {
    // Click on wizard input
    await page.locator('input[placeholder*="Ask the AI wizard"]').click();
    
    // Type request to add a slide
    await page.locator('input[placeholder*="Ask the AI wizard"]').fill('Add a new slide about Kubernetes security best practices');
    
    // Send the message
    await page.locator('button[type="submit"]').click();
    
    // Wait for AI response
    await page.waitForTimeout(10000);
    
    // Check if suggestion appears with slide count
    await expect(page.locator('text=Modified presentation with')).toBeVisible({ timeout: 20000 });
    
    // Apply the changes
    await page.locator('text=Apply Changes').click();
    await page.waitForTimeout(3000);
    
    // Verify success message
    await expect(page.locator('text=Perfect! I\'ve successfully applied')).toBeVisible();
  });

  test('should remove a slide via wizard', async ({ page }) => {
    // Click on wizard input
    await page.locator('input[placeholder*="Ask the AI wizard"]').click();
    
    // Type request to remove a slide
    await page.locator('input[placeholder*="Ask the AI wizard"]').fill('Remove the introduction slide');
    
    // Send the message
    await page.locator('button[type="submit"]').click();
    
    // Wait for AI response
    await page.waitForTimeout(10000);
    
    // Check if suggestion appears with decreased slide count
    await expect(page.locator('text=Modified presentation with')).toBeVisible({ timeout: 20000 });
    
    // Apply the changes
    await page.locator('text=Apply Changes').click();
    await page.waitForTimeout(3000);
    
    // Verify success message
    await expect(page.locator('text=Perfect! I\'ve successfully applied')).toBeVisible();
  });

  test('should handle multiple slide operations', async ({ page }) => {
    // Test adding multiple slides
    await page.locator('input[placeholder*="Ask the AI wizard"]').click();
    await page.locator('input[placeholder*="Ask the AI wizard"]').fill('Add two new slides: one about Kubernetes monitoring and another about troubleshooting');
    await page.locator('button[type="submit"]').click();
    await page.waitForTimeout(10000);
    
    // Verify suggestion appears
    await expect(page.locator('text=Modified presentation with')).toBeVisible({ timeout: 20000 });
    
    // Apply changes
    await page.locator('text=Apply Changes').click();
    await page.waitForTimeout(3000);
    
    // Verify success
    await expect(page.locator('text=Perfect! I\'ve successfully applied')).toBeVisible();
  });

  test('should show preview of slide changes', async ({ page }) => {
    // Request slide addition
    await page.locator('input[placeholder*="Ask the AI wizard"]').click();
    await page.locator('input[placeholder*="Ask the AI wizard"]').fill('Add a slide about Kubernetes networking');
    await page.locator('button[type="submit"]').click();
    await page.waitForTimeout(8000);
    
    // Verify preview shows slide titles
    await expect(page.locator('text=Modified presentation with')).toBeVisible({ timeout: 15000 });
    
    // Verify we can see slide structure in the suggestion
    await expect(page.locator('text=Understanding Kubernetes')).toBeVisible();
  });

  test('should handle wizard context correctly', async ({ page }) => {
    // Verify wizard shows correct context
    await expect(page.locator('text=Context: Single Slide')).toBeVisible();
    await expect(page.locator('text=Step: Slides')).toBeVisible();
    
    // Test that wizard can handle presentation-level changes
    await page.locator('input[placeholder*="Ask the AI wizard"]').click();
    await page.locator('input[placeholder*="Ask the AI wizard"]').fill('Reorganize the slides to put the introduction first');
    await page.locator('button[type="submit"]').click();
    await page.waitForTimeout(8000);
    
    // Should show modification suggestion
    await expect(page.locator('text=Modified presentation with')).toBeVisible({ timeout: 15000 });
  });
}); 