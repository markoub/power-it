import { test, expect } from '@playwright/test';

test.describe('Homepage Pagination', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to the homepage before each test
    await page.goto('http://localhost:3000');
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
    const paginationInfo = page.locator('text=/Showing \\d+ to \\d+ of \\d+ presentations/');
    await expect(paginationInfo).toBeVisible();
    
    // Verify the format matches "Showing X to Y of Z presentations"
    const infoText = await paginationInfo.textContent();
    expect(infoText).toMatch(/Showing \d+ to \d+ of \d+ presentations/);
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
    
    // Get initial pagination info
    const paginationInfo = page.locator('text=/Showing \\d+ to \\d+ of \\d+ presentations/');
    const initialInfo = await paginationInfo.textContent();
    
    // Click Next button
    const nextButton = page.locator('a[aria-label="Go to next page"]');
    await nextButton.click();
    
    // Wait for page to update
    await page.waitForLoadState('networkidle');
    
    // Check that pagination info has changed
    const newInfo = await paginationInfo.textContent();
    expect(newInfo).not.toBe(initialInfo);
    
    // Check that we're now on page 2 (Previous button should be enabled)
    const prevButton = page.locator('a[aria-label="Go to previous page"]');
    await expect(prevButton).toHaveAttribute('data-disabled', 'false');
    await expect(prevButton).toHaveClass(/cursor-pointer/);
  });

  test('should navigate back to previous page when Previous button is clicked', async ({ page }) => {
    // Wait for presentations to load
    await expect(page.getByTestId('presentations-grid')).toBeVisible({ timeout: 10000 });
    
    // Go to page 2 first
    const nextButton = page.locator('a[aria-label="Go to next page"]');
    await nextButton.click();
    await page.waitForLoadState('networkidle');
    
    // Get pagination info on page 2
    const paginationInfo = page.locator('text=/Showing \\d+ to \\d+ of \\d+ presentations/');
    const page2Info = await paginationInfo.textContent();
    
    // Click Previous button
    const prevButton = page.locator('a[aria-label="Go to previous page"]');
    await prevButton.click();
    await page.waitForLoadState('networkidle');
    
    // Check that we're back to page 1
    const page1Info = await paginationInfo.textContent();
    expect(page1Info).not.toBe(page2Info);
    
    // Previous button should be disabled again
    await expect(prevButton).toHaveAttribute('data-disabled', 'true');
    await expect(prevButton).toHaveClass(/cursor-not-allowed/);
  });

  test('should navigate to specific page when page number is clicked', async ({ page }) => {
    // Wait for presentations to load
    await expect(page.getByTestId('presentations-grid')).toBeVisible({ timeout: 10000 });
    
    // Check if page 3 exists (we need at least 3 pages)
    const page3Link = page.locator('a[role="button"]:has-text("3")');
    
    if (await page3Link.isVisible()) {
      // Get initial pagination info
      const paginationInfo = page.locator('text=/Showing \\d+ to \\d+ of \\d+ presentations/');
      const initialInfo = await paginationInfo.textContent();
      
      // Click on page 3
      await page3Link.click();
      await page.waitForLoadState('networkidle');
      
      // Check that pagination info has changed
      const newInfo = await paginationInfo.textContent();
      expect(newInfo).not.toBe(initialInfo);
      
      // Check that page 3 is now active
      await expect(page3Link).toHaveAttribute('data-current', 'page');
    }
  });

  test('should show ellipsis when there are many pages', async ({ page }) => {
    // Wait for presentations to load
    await expect(page.getByTestId('presentations-grid')).toBeVisible({ timeout: 10000 });
    
    // Set page size to 5 to ensure many pages
    const pageSizeSelect = page.locator('[data-testid="page-size-select"]');
    await pageSizeSelect.selectOption('5');
    await page.waitForLoadState('networkidle');
    
    // Try to find page buttons to determine how many pages we have
    const pageButtons = page.locator('nav[role="navigation"] a[role="button"]');
    const pageButtonCount = await pageButtons.count();
    
    // If we don't have enough pages, skip this test
    if (pageButtonCount < 5) {
      console.log(`Skipping ellipsis test: only ${pageButtonCount} page buttons found`);
      return;
    }
    
    // With 5+ page buttons, pagination should include ellipsis
    // The ellipsis is rendered as <span aria-hidden> containing an SVG
    const ellipsis = page.locator('nav[role="navigation"] span[aria-hidden] svg');
    const ellipsisCount = await ellipsis.count();
    
    // We expect at least one ellipsis to be present
    expect(ellipsisCount).toBeGreaterThan(0);
  });

  test('should change page size and update pagination', async ({ page }) => {
    // Wait for presentations to load
    await expect(page.getByTestId('presentations-grid')).toBeVisible({ timeout: 10000 });

    // Get initial pagination info
    const paginationInfo = page.locator('text=/Showing \\d+ to \\d+ of \\d+ presentations/');
    if (!(await paginationInfo.isVisible())) {
      test.skip('Not enough data for pagination');
    }
    const initialInfo = await paginationInfo.textContent();
    
    // Change page size to 50
    const pageSizeSelect = page.locator('[data-testid="page-size-select"]');
    await pageSizeSelect.selectOption('50');
    await page.waitForLoadState('networkidle');
    
    // Check that pagination info has changed (should show more items per page)
    const newInfo = await paginationInfo.textContent();
    expect(newInfo).not.toBe(initialInfo);
    
    // Extract the "to" number from the pagination info to verify it's higher
    const initialMatch = initialInfo?.match(/Showing \d+ to (\d+) of/);
    const newMatch = newInfo?.match(/Showing \d+ to (\d+) of/);
    
    if (initialMatch && newMatch) {
      const initialTo = parseInt(initialMatch[1]);
      const newTo = parseInt(newMatch[1]);
      expect(newTo).toBeGreaterThan(initialTo);
    }
  });

  test('should filter presentations and update pagination', async ({ page }) => {
    // Wait for presentations to load
    await expect(page.getByTestId('presentations-grid')).toBeVisible({ timeout: 10000 });

    // Get initial pagination info
    const paginationInfo = page.locator('text=/Showing \\d+ to \\d+ of \\d+ presentations/');
    if (!(await paginationInfo.isVisible())) {
      test.skip('Not enough data for pagination');
    }
    const initialInfo = await paginationInfo.textContent();
    
    // Change status filter to "finished"
    const statusFilter = page.locator('[data-testid="status-filter-select"]');
    await statusFilter.selectOption('finished');
    await page.waitForLoadState('networkidle');
    
    // Check that pagination info has changed (should show fewer total presentations)
    const newInfo = await paginationInfo.textContent();
    expect(newInfo).not.toBe(initialInfo);
    
    // Extract the total number to verify it's changed
    const initialMatch = initialInfo?.match(/of (\d+) presentations/);
    const newMatch = newInfo?.match(/of (\d+) presentations/);
    
    if (initialMatch && newMatch) {
      const initialTotal = parseInt(initialMatch[1]);
      const newTotal = parseInt(newMatch[1]);
      // The filtered total should be different (likely smaller)
      expect(newTotal).not.toBe(initialTotal);
    }
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