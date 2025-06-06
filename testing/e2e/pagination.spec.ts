import { test, expect } from '@playwright/test';
import { TEST_CONFIG } from '../test-config';

test.describe('Homepage Pagination', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to the homepage before each test - using test server
    await page.goto(TEST_CONFIG.TEST_FRONTEND_URL);
    await expect(page.getByTestId('presentations-container')).toBeVisible();
  });

  test('should display pagination controls when there are multiple pages', async ({ page }) => {
    // Wait for presentations to load
    await expect(page.getByTestId('presentations-grid')).toBeVisible({ timeout: 3000 });
    
    // Check that pagination is visible
    const pagination = page.locator('nav[role="navigation"][aria-label="pagination"]');
    await expect(pagination).toBeVisible();
    
    // Check that Previous/Next buttons exist
    await expect(page.locator('a[aria-label="Go to previous page"]')).toBeVisible();
    await expect(page.locator('a[aria-label="Go to next page"]')).toBeVisible();
  });

  test('should show proper pagination information', async ({ page }) => {
    // Wait for presentations to load
    await expect(page.getByTestId('presentations-grid')).toBeVisible({ timeout: 3000 });
    
    // Check that the pagination info shows correct information
    // With 32 presentations and 10 per page, first page should show "Showing 1–10 of \d+ presentations"
    const paginationInfo = page.locator('text=/Showing \\d+–\\d+ of \\d+ presentations/');
    await expect(paginationInfo).toBeVisible();
    
    // Verify the format and that we have multiple presentations
    const infoText = await paginationInfo.textContent();
    expect(infoText).toMatch(/Showing 1–10 of \d+ presentations/);
    
    // Extract the total number to verify we have multiple pages worth
    const match = infoText?.match(/of (\d+) presentations/);
    if (match) {
      const total = parseInt(match[1]);
      expect(total).toBeGreaterThan(10); // More than one page of presentations
    }
  });

  test('should disable Previous button on first page', async ({ page }) => {
    // Wait for presentations to load
    await expect(page.getByTestId('presentations-grid')).toBeVisible({ timeout: 3000 });
    
    // Check that Previous button is disabled on first page
    const prevButton = page.locator('a[aria-label="Go to previous page"]');
    await expect(prevButton).toHaveAttribute('data-disabled', 'true');
    await expect(prevButton).toHaveClass(/cursor-not-allowed/);
  });

  test('should navigate to next page when Next button is clicked', async ({ page }) => {
    // Wait for presentations to load
    await expect(page.getByTestId('presentations-grid')).toBeVisible({ timeout: 3000 });
    
    // Get initial pagination info - should be "Showing 1–10 of \d+ presentations"
    const paginationInfo = page.locator('text=/Showing \\d+–\\d+ of \\d+ presentations/');
    const initialInfo = await paginationInfo.textContent();
    expect(initialInfo).toMatch(/Showing 1–10 of \d+ presentations/);
    
    // Click Next button
    const nextButton = page.locator('a[aria-label="Go to next page"]');
    await nextButton.click();
    
    // Wait for page to update
    await page.waitForLoadState('networkidle');
    
    // Check that pagination info has changed to page 2 - should be "Showing 11–20 of \d+ presentations"
    const newInfo = await paginationInfo.textContent();
    expect(newInfo).toMatch(/Showing 11–20 of \d+ presentations/);
    
    // Check that we're now on page 2 (Previous button should be enabled)
    const prevButton = page.locator('a[aria-label="Go to previous page"]');
    await expect(prevButton).toHaveAttribute('data-disabled', 'false');
    await expect(prevButton).toHaveClass(/cursor-pointer/);
    
    // Next button should NOT be disabled since we have 4 pages total
    await expect(nextButton).toHaveAttribute('data-disabled', 'false');
    await expect(nextButton).toHaveClass(/cursor-pointer/);
  });

  test('should navigate back to previous page when Previous button is clicked', async ({ page }) => {
    // Wait for presentations to load
    await expect(page.getByTestId('presentations-grid')).toBeVisible({ timeout: 3000 });
    
    // Go to page 2 first
    const nextButton = page.locator('a[aria-label="Go to next page"]');
    await nextButton.click();
    await page.waitForLoadState('networkidle');
    
    // Verify we're on page 2
    const paginationInfo = page.locator('text=/Showing \\d+–\\d+ of \\d+ presentations/');
    const page2Info = await paginationInfo.textContent();
    expect(page2Info).toMatch(/Showing 11–20 of \d+ presentations/);
    
    // Click Previous button
    const prevButton = page.locator('a[aria-label="Go to previous page"]');
    await prevButton.click();
    await page.waitForLoadState('networkidle');
    
    // Check that we're back to page 1
    const page1Info = await paginationInfo.textContent();
    expect(page1Info).toMatch(/Showing 1–10 of \d+ presentations/);
    
    // Previous button should be disabled again
    await expect(prevButton).toHaveAttribute('data-disabled', 'true');
    await expect(prevButton).toHaveClass(/cursor-not-allowed/);
  });

  test('should navigate to specific page when page number is clicked', async ({ page }) => {
    // Wait for presentations to load
    await expect(page.getByTestId('presentations-grid')).toBeVisible({ timeout: 3000 });
    
    // With 32 presentations and 10 per page, we have 4 pages
    // Look for the page 2 link - it's an anchor tag with text "2"
    const page2Link = page.locator('nav[role="navigation"] a:has-text("2"):not([aria-label])');
    
    // Verify page 2 link is visible
    await expect(page2Link).toBeVisible();
    
    // Get initial pagination info
    const paginationInfo = page.locator('text=/Showing \\d+–\\d+ of \\d+ presentations/');
    const initialInfo = await paginationInfo.textContent();
    expect(initialInfo).toMatch(/Showing 1–10 of \d+ presentations/);
    
    // Click on page 2
    await page2Link.click();
    await page.waitForLoadState('networkidle');
    
    // Check that pagination info has changed to page 2
    const newInfo = await paginationInfo.textContent();
    expect(newInfo).toMatch(/Showing 11–20 of \d+ presentations/);
    
    // Check that page 2 is now active using aria-current attribute
    await expect(page2Link).toHaveAttribute('aria-current', 'page');
  });

  test('should show ellipsis when there are many pages', async ({ page }) => {
    // With 32 presentations and page size of 5, we get 7 pages (32/5 = 6.4)
    // The pagination component shows ellipsis when there are more than 5 pages
    
    await expect(page.getByTestId('presentations-grid')).toBeVisible({ timeout: 3000 });
    
    // Change page size to 5 to create more pages
    const pageSizeSelect = page.locator('[data-testid="page-size-select"]');
    await pageSizeSelect.selectOption('5');
    await page.waitForLoadState('networkidle');
    
    // With 7 pages, there should be ellipsis in the pagination
    const ellipsis = page.locator('nav[role="navigation"] span[aria-hidden] svg');
    const ellipsisCount = await ellipsis.count();
    expect(ellipsisCount).toBeGreaterThan(0);
  });

  test('should change page size and update pagination', async ({ page }) => {
    // Wait for presentations to load
    await expect(page.getByTestId('presentations-grid')).toBeVisible({ timeout: 3000 });
    
    // Get initial pagination info (default 10 per page)
    const paginationInfo = page.locator('text=/Showing \\d+–\\d+ of \\d+ presentations/');
    const initialInfo = await paginationInfo.textContent();
    expect(initialInfo).toMatch(/Showing 1–10 of \d+ presentations/);
    
    // Change page size to 5
    const pageSizeSelect = page.locator('[data-testid="page-size-select"]');
    await pageSizeSelect.selectOption('5');
    await page.waitForLoadState('networkidle');
    
    // Check that pagination info has changed (should show fewer items per page)
    const newInfo = await paginationInfo.textContent();
    expect(newInfo).toMatch(/Showing 1–5 of \d+ presentations/);
    
    // Change page size to 50 (should show all presentations on one page)
    await pageSizeSelect.selectOption('50');
    await page.waitForLoadState('networkidle');
    
    // Check that pagination info shows all presentations
    const allInfo = await paginationInfo.textContent();
    expect(allInfo).toMatch(/Showing 1–\d+ of \d+ presentations/);
    
    // With 32 items and page size 50, pagination controls should not be visible
    const pagination = page.locator('nav[role="navigation"][aria-label="pagination"]');
    await expect(pagination).not.toBeVisible();
  });

  test('should filter presentations and update pagination', async ({ page }) => {
    // Wait for presentations to load
    await expect(page.getByTestId('presentations-grid')).toBeVisible({ timeout: 3000 });
    
    // Get initial pagination info - all presentations
    const paginationInfo = page.locator('text=/Showing \\d+–\\d+ of \\d+ presentations/');
    const initialInfo = await paginationInfo.textContent();
    expect(initialInfo).toMatch(/Showing 1–10 of \d+ presentations/);
    
    // Change status filter to "finished" - according to test data, we should have some finished presentations
    const statusFilter = page.locator('[data-testid="status-filter-select"]');
    await statusFilter.selectOption('finished');
    await page.waitForLoadState('networkidle');
    
    // Check that pagination info has changed (should show fewer total presentations)
    const newInfo = await paginationInfo.textContent();
    expect(newInfo).not.toBe(initialInfo);
    
    // Extract the total number to verify it's less than 32
    const newMatch = newInfo?.match(/of (\d+) presentations/);
    if (newMatch) {
      const newTotal = parseInt(newMatch[1]);
      const initialTotal = initialInfo?.match(/of (\d+) presentations/)?.[1];
      if (initialTotal) {
        expect(newTotal).toBeLessThan(parseInt(initialTotal));
      }
      expect(newTotal).toBeGreaterThan(0); // Should have at least some finished presentations
    }
    
    // Change back to "all" to verify it returns to original state
    await statusFilter.selectOption('all');
    await page.waitForLoadState('networkidle');
    
    const allInfo = await paginationInfo.textContent();
    expect(allInfo).toMatch(/Showing 1–10 of \d+ presentations/);
  });

  test('should maintain proper responsive design', async ({ page }) => {
    // Test desktop view
    await page.setViewportSize({ width: 1200, height: 800 });
    await expect(page.getByTestId('presentations-grid')).toBeVisible({ timeout: 3000 });
    
    // Check that pagination is properly aligned
    const pagination = page.locator('nav[role="navigation"][aria-label="pagination"]');
    await expect(pagination).toBeVisible();
    
    // Test mobile view
    await page.setViewportSize({ width: 375, height: 667 });
    await page.waitForLoadState('domcontentloaded');
    
    // Pagination should still be visible and functional on mobile
    await expect(pagination).toBeVisible();
    
    // Next/Previous buttons should still be clickable
    const nextButton = page.locator('a[aria-label="Go to next page"]');
    await expect(nextButton).toBeVisible();
  });
}); 