import { test, expect } from '@playwright/test';

test.describe('Homepage Pagination', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to the homepage before each test - using test port 3001
    await page.goto('http://localhost:3001');
    await expect(page.getByTestId('presentations-container')).toBeVisible();
  });

  test('should display pagination controls when there are multiple pages', async ({ page }) => {
    // Wait for presentations to load
    await expect(page.getByTestId('presentations-grid')).toBeVisible({ timeout: 10000 });
    
    // Check that pagination is visible
    const pagination = page.locator('nav[role="navigation"][aria-label="pagination"]');
    await expect(pagination).toBeVisible();
    
    // Check that Previous/Next buttons exist
    await expect(page.locator('a[aria-label="Go to previous page"]')).toBeVisible();
    await expect(page.locator('a[aria-label="Go to next page"]')).toBeVisible();
  });

  test('should show proper pagination information', async ({ page }) => {
    // Wait for presentations to load
    await expect(page.getByTestId('presentations-grid')).toBeVisible({ timeout: 10000 });
    
    // Check that the pagination info shows correct information
    // With 12 presentations and 10 per page, first page should show "Showing 1–10 of 12 presentations"
    const paginationInfo = page.locator('text=/Showing \\d+–\\d+ of \\d+ presentations/');
    await expect(paginationInfo).toBeVisible();
    
    // Verify the exact values for the pre-seeded data
    const infoText = await paginationInfo.textContent();
    expect(infoText).toBe('Showing 1–10 of 12 presentations');
  });

  test('should disable Previous button on first page', async ({ page }) => {
    // Wait for presentations to load
    await expect(page.getByTestId('presentations-grid')).toBeVisible({ timeout: 10000 });
    
    // Check that Previous button is disabled on first page
    const prevButton = page.locator('a[aria-label="Go to previous page"]');
    await expect(prevButton).toHaveAttribute('data-disabled', 'true');
    await expect(prevButton).toHaveClass(/cursor-not-allowed/);
  });

  test('should navigate to next page when Next button is clicked', async ({ page }) => {
    // Wait for presentations to load
    await expect(page.getByTestId('presentations-grid')).toBeVisible({ timeout: 10000 });
    
    // Get initial pagination info - should be "Showing 1–10 of 12 presentations"
    const paginationInfo = page.locator('text=/Showing \\d+–\\d+ of \\d+ presentations/');
    const initialInfo = await paginationInfo.textContent();
    expect(initialInfo).toBe('Showing 1–10 of 12 presentations');
    
    // Click Next button
    const nextButton = page.locator('a[aria-label="Go to next page"]');
    await nextButton.click();
    
    // Wait for page to update
    await page.waitForLoadState('networkidle');
    
    // Check that pagination info has changed to page 2 - should be "Showing 11–12 of 12 presentations"
    const newInfo = await paginationInfo.textContent();
    expect(newInfo).toBe('Showing 11–12 of 12 presentations');
    
    // Check that we're now on page 2 (Previous button should be enabled)
    const prevButton = page.locator('a[aria-label="Go to previous page"]');
    await expect(prevButton).toHaveAttribute('data-disabled', 'false');
    await expect(prevButton).toHaveClass(/cursor-pointer/);
    
    // Also verify that Next button is now disabled since we're on the last page
    await expect(nextButton).toHaveAttribute('data-disabled', 'true');
    await expect(nextButton).toHaveClass(/cursor-not-allowed/);
  });

  test('should navigate back to previous page when Previous button is clicked', async ({ page }) => {
    // Wait for presentations to load
    await expect(page.getByTestId('presentations-grid')).toBeVisible({ timeout: 10000 });
    
    // Go to page 2 first
    const nextButton = page.locator('a[aria-label="Go to next page"]');
    await nextButton.click();
    await page.waitForLoadState('networkidle');
    
    // Verify we're on page 2
    const paginationInfo = page.locator('text=/Showing \\d+–\\d+ of \\d+ presentations/');
    const page2Info = await paginationInfo.textContent();
    expect(page2Info).toBe('Showing 11–12 of 12 presentations');
    
    // Click Previous button
    const prevButton = page.locator('a[aria-label="Go to previous page"]');
    await prevButton.click();
    await page.waitForLoadState('networkidle');
    
    // Check that we're back to page 1
    const page1Info = await paginationInfo.textContent();
    expect(page1Info).toBe('Showing 1–10 of 12 presentations');
    
    // Previous button should be disabled again
    await expect(prevButton).toHaveAttribute('data-disabled', 'true');
    await expect(prevButton).toHaveClass(/cursor-not-allowed/);
  });

  test('should navigate to specific page when page number is clicked', async ({ page }) => {
    // Wait for presentations to load
    await expect(page.getByTestId('presentations-grid')).toBeVisible({ timeout: 10000 });
    
    // With 12 presentations and 10 per page, we only have 2 pages
    // Look for the page 2 link - it's an anchor tag with text "2"
    const page2Link = page.locator('nav[role="navigation"] a:has-text("2"):not([aria-label])');
    
    // Verify page 2 link is visible
    await expect(page2Link).toBeVisible();
    
    // Get initial pagination info
    const paginationInfo = page.locator('text=/Showing \\d+–\\d+ of \\d+ presentations/');
    const initialInfo = await paginationInfo.textContent();
    expect(initialInfo).toBe('Showing 1–10 of 12 presentations');
    
    // Click on page 2
    await page2Link.click();
    await page.waitForLoadState('networkidle');
    
    // Check that pagination info has changed to page 2
    const newInfo = await paginationInfo.textContent();
    expect(newInfo).toBe('Showing 11–12 of 12 presentations');
    
    // Check that page 2 is now active using aria-current attribute
    await expect(page2Link).toHaveAttribute('aria-current', 'page');
  });

  test.skip('should show ellipsis when there are many pages', async ({ page }) => {
    // SKIPPED: With only 12 presentations and minimum page size of 5,
    // we can only get 3 pages maximum (12/5 = 2.4 pages).
    // The pagination component only shows ellipsis when there are more than 5 pages.
    // To properly test ellipsis, we would need either:
    // 1. More than 25 presentations (5 items/page * 5+ pages)
    // 2. Or a smaller page size option (like 2 items/page)
    
    // The test would work like this if we had enough data:
    // await expect(page.getByTestId('presentations-grid')).toBeVisible({ timeout: 10000 });
    // const pageSizeSelect = page.locator('[data-testid="page-size-select"]');
    // await pageSizeSelect.selectOption('5');
    // await page.waitForLoadState('networkidle');
    // const ellipsis = page.locator('nav[role="navigation"] span[aria-hidden] svg');
    // const ellipsisCount = await ellipsis.count();
    // expect(ellipsisCount).toBeGreaterThan(0);
  });

  test('should change page size and update pagination', async ({ page }) => {
    // Wait for presentations to load
    await expect(page.getByTestId('presentations-grid')).toBeVisible({ timeout: 10000 });
    
    // Get initial pagination info (default 10 per page)
    const paginationInfo = page.locator('text=/Showing \\d+–\\d+ of \\d+ presentations/');
    const initialInfo = await paginationInfo.textContent();
    expect(initialInfo).toBe('Showing 1–10 of 12 presentations');
    
    // Change page size to 5
    const pageSizeSelect = page.locator('[data-testid="page-size-select"]');
    await pageSizeSelect.selectOption('5');
    await page.waitForLoadState('networkidle');
    
    // Check that pagination info has changed (should show fewer items per page)
    const newInfo = await paginationInfo.textContent();
    expect(newInfo).toBe('Showing 1–5 of 12 presentations');
    
    // Change page size to 50 (should show all presentations on one page)
    await pageSizeSelect.selectOption('50');
    await page.waitForLoadState('networkidle');
    
    // Check that pagination info shows all presentations
    const allInfo = await paginationInfo.textContent();
    expect(allInfo).toBe('Showing 1–12 of 12 presentations');
    
    // When all items fit on one page, pagination controls should not be visible
    const pagination = page.locator('nav[role="navigation"][aria-label="pagination"]');
    await expect(pagination).not.toBeVisible();
  });

  test('should filter presentations and update pagination', async ({ page }) => {
    // Wait for presentations to load
    await expect(page.getByTestId('presentations-grid')).toBeVisible({ timeout: 10000 });
    
    // Get initial pagination info - all presentations
    const paginationInfo = page.locator('text=/Showing \\d+–\\d+ of \\d+ presentations/');
    const initialInfo = await paginationInfo.textContent();
    expect(initialInfo).toBe('Showing 1–10 of 12 presentations');
    
    // Change status filter to "finished" - according to test data, we should have some finished presentations
    const statusFilter = page.locator('[data-testid="status-filter-select"]');
    await statusFilter.selectOption('finished');
    await page.waitForLoadState('networkidle');
    
    // Check that pagination info has changed (should show fewer total presentations)
    const newInfo = await paginationInfo.textContent();
    expect(newInfo).not.toBe(initialInfo);
    
    // Extract the total number to verify it's less than 12
    const newMatch = newInfo?.match(/of (\d+) presentations/);
    if (newMatch) {
      const newTotal = parseInt(newMatch[1]);
      expect(newTotal).toBeLessThan(12);
      expect(newTotal).toBeGreaterThan(0); // Should have at least some finished presentations
    }
    
    // Change back to "all" to verify it returns to original state
    await statusFilter.selectOption('all');
    await page.waitForLoadState('networkidle');
    
    const allInfo = await paginationInfo.textContent();
    expect(allInfo).toBe('Showing 1–10 of 12 presentations');
  });

  test('should maintain proper responsive design', async ({ page }) => {
    // Test desktop view
    await page.setViewportSize({ width: 1200, height: 800 });
    await expect(page.getByTestId('presentations-grid')).toBeVisible({ timeout: 10000 });
    
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