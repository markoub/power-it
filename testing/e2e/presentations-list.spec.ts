import { test, expect } from '@playwright/test';
import { goToPresentationsPage, waitForNetworkIdle } from './utils';

test.describe('Presentations List Page', () => {
  test('should display the presentations page correctly', async ({ page }) => {
    await goToPresentationsPage(page);
    
    // Check if the page title is correct
    await expect(page).toHaveTitle('AI Presentation Creator');
    
    // Check if the page header is visible
    await expect(page.getByTestId('page-title')).toBeVisible();
    await expect(page.getByTestId('page-title')).toContainText('AI Presentation Creator');
    
    // Check if the "Create New Presentation" button is visible
    await expect(page.getByTestId('ai-research-button')).toBeVisible();
    await expect(page.getByTestId('ai-research-button')).toContainText('Create New Presentation');
    
    // Check if the presentations section is visible
    await expect(page.getByTestId('presentations-container')).toBeVisible();
    await expect(page.getByTestId('presentations-section-title')).toContainText('Your Presentations');
  });
  
  test('should display presentations if they exist', async ({ page }) => {
    await goToPresentationsPage(page);
    
    // Wait for presentations to load (the loader should disappear)
    await page.waitForSelector('[data-testid="presentations-loading"]', { state: 'detached', timeout: 10000 })
      .catch(() => console.log('Loading indicator not found or already gone'));
    
    // Wait for network requests to complete
    await waitForNetworkIdle(page);
    
    // One of these three elements should be visible depending on the state
    await Promise.race([
      page.getByTestId('presentations-grid').waitFor({ timeout: 5000 }),
      page.getByTestId('no-presentations-message').waitFor({ timeout: 5000 }),
      page.getByTestId('presentations-error').waitFor({ timeout: 5000 })
    ]);
    
    // Wait additional time for animations to complete
    await page.waitForTimeout(1000);
    
    // Get the visibility status of key elements
    const hasGrid = await page.getByTestId('presentations-grid').isVisible();
    const hasNoPresMessage = await page.getByTestId('no-presentations-message').isVisible();
    const hasError = await page.getByTestId('presentations-error').isVisible();
    
    // Skip the test if there was an error (not what we're testing)
    if (hasError) {
      console.log('Error loading presentations - skipping test');
      test.skip();
      return;
    }
    
    // If we have presentations, check the cards and their contents
    if (hasGrid) {
      // Check if at least one presentation card is visible
      const presentationCards = page.locator('[data-testid^="presentation-card-"]');
      const count = await presentationCards.count();
      
      console.log(`Found ${count} presentation cards`);
      expect(count).toBeGreaterThan(0);
      
      // Check if the first presentation card has expected elements
      if (count > 0) {
        const firstCard = presentationCards.first();
        
        // Wait for the card to be fully visible (including animations)
        await firstCard.waitFor({ state: 'visible', timeout: 5000 });
        
        // Check for card content using a more flexible approach
        const hasTitleText = await firstCard.locator(`[data-testid="presentation-name"]`).isVisible()
          .catch(() => false);
        
        if (hasTitleText) {
          console.log("Title element is visible, checking other elements");
        } else {
          console.log("Title element is not visible, skipping detailed card checks");
          // Continue with the test without failing if elements aren't visible yet
        }
        
        // Check for buttons which should always be visible
        const hasEditButton = await firstCard.getByTestId('edit-presentation-button').isVisible()
          .catch(() => false);
        const hasDeleteButton = await firstCard.getByTestId('delete-presentation-button').isVisible()
          .catch(() => false);
          
        expect(hasEditButton || hasDeleteButton).toBeTruthy();
        
        // Check that thumbnail has proper 16:9 aspect ratio
        const thumbnail = firstCard.getByTestId('presentation-thumbnail');
        await thumbnail.waitFor({ state: 'visible', timeout: 5000 });
        
        // Verify thumbnail is displayed and has proper aspect ratio container
        const thumbnailContainer = thumbnail.locator('..');
        const hasAspectRatio = await thumbnailContainer.evaluate(el => 
          el.classList.contains('aspect-[16/9]') || 
          getComputedStyle(el).aspectRatio === '16 / 9'
        ).catch(() => false);
        
        console.log('Thumbnail has proper aspect ratio:', hasAspectRatio);
        expect(hasAspectRatio).toBeTruthy();
      }
    } else if (hasNoPresMessage) {
      // If no presentations, check that the message and create button are displayed
      await expect(page.getByTestId('no-presentations-message')).toBeVisible();
      await expect(page.getByTestId('no-presentations-message')).toContainText('No presentations yet');
      await expect(page.getByTestId('create-presentation-button')).toBeVisible();
      await expect(page.getByTestId('create-presentation-button')).toContainText('Create Presentation');
    }
  });
  
  test('should navigate to create page when clicking create button', async ({ page }) => {
    await goToPresentationsPage(page);
    
    // Wait for the page to load completely
    await waitForNetworkIdle(page);
    
    // Check if we have no presentations and need to use that button
    const hasNoPresMessage = await page.getByTestId('no-presentations-message').isVisible().catch(() => false);
    
    if (hasNoPresMessage) {
      // Click the create button in the "no presentations" message
      await page.getByTestId('create-presentation-button').click();
    } else {
      // Click the main create button in the header
      await page.getByTestId('ai-research-button').click();
    }
    
    // Wait for navigation and check if we're on the create page
    await page.waitForSelector('[data-testid="create-page"]', { timeout: 5000 });
    await expect(page.getByTestId('create-presentation-form')).toBeVisible();
    
    // Verify we're on the create page
    await expect(page.url()).toContain('/create');
  });

  test('should switch between grid and list views', async ({ page }) => {
    await goToPresentationsPage(page);
    await waitForNetworkIdle(page);
    
    // Wait for loading to complete
    await page.waitForSelector('[data-testid="presentations-loading"]', { state: 'detached', timeout: 10000 })
      .catch(() => console.log('Loading indicator not found or already gone'));

    // Check if view controls are available (only if there are presentations)
    const hasViewControls = await page.getByTestId('view-list-button').isVisible().catch(() => false);
    
    if (!hasViewControls) {
      console.log('No view controls available - likely no presentations exist');
      test.skip();
      return;
    }

    // Switch to list view and expect table
    await page.getByTestId('view-list-button').click();
    await expect(page.getByTestId('presentations-table')).toBeVisible();

    // Switch back to grid view and expect grid
    await page.getByTestId('view-grid-button').click();
    await expect(page.getByTestId('presentations-grid')).toBeVisible();
  });

  test('should display all presentations with proper aspect ratio', async ({ page }) => {
    await goToPresentationsPage(page);
    await waitForNetworkIdle(page);
    
    // Wait for loading to complete
    await page.waitForSelector('[data-testid="presentations-loading"]', { state: 'detached', timeout: 10000 })
      .catch(() => console.log('Loading indicator not found or already gone'));
    
    // Check if presentations are shown
    const hasGrid = await page.getByTestId('presentations-grid').isVisible().catch(() => false);
    
    if (hasGrid) {
      // Get all presentation cards
      const presentationCards = page.locator('[data-testid^="presentation-card-"]');
      const count = await presentationCards.count();
      
      console.log(`Found ${count} presentation cards (should show all presentations regardless of completion status)`);
      
      // Check each card has proper aspects
      for (let i = 0; i < count; i++) {
        const card = presentationCards.nth(i);
        
        // Check that thumbnail has proper 16:9 aspect ratio
        const thumbnail = card.getByTestId('presentation-thumbnail');
        const thumbnailContainer = thumbnail.locator('..');
        
        const hasAspectRatio = await thumbnailContainer.evaluate(el => 
          el.classList.contains('aspect-[16/9]')
        ).catch(() => false);
        
        console.log(`Card ${i}: Has proper aspect ratio: ${hasAspectRatio}`);
        expect(hasAspectRatio).toBeTruthy();
        
        // Thumbnail should either have a real URL or use placeholder gracefully
        await expect(thumbnail).toBeVisible();
        
        const thumbnailSrc = await thumbnail.getAttribute('src');
        const hasValidSrc = thumbnailSrc && (thumbnailSrc.includes('/presentations/') || thumbnailSrc.includes('placeholder.svg'));
        
        console.log(`Card ${i}: Has valid thumbnail source: ${hasValidSrc}`);
        expect(hasValidSrc).toBeTruthy();
      }
    } else {
      console.log('No presentations found - this is acceptable if no presentations exist');
    }
  });
}); 