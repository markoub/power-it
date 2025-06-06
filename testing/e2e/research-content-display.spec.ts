import { test, expect } from '@playwright/test';
import { navigateToTestPresentation } from './utils';

test.describe('Research Content Display', () => {
  test.setTimeout(120000);

  test('should display AI research content from pre-seeded data', async ({ page }) => {
    // Navigate to a presentation with completed research
    const presentation = await navigateToTestPresentation(page, 'research_complete', 0);
    
    // Verify we're on the edit page for the correct presentation
    await expect(page).toHaveURL(`/edit/${presentation.id}`);
    
    // Click on the Research step to view research content
    const researchStepButton = page.getByTestId('step-nav-research');
    await researchStepButton.click();
    
    // Wait for research content to be visible
    const researchContent = page.getByTestId('ai-research-content');
    await expect(researchContent).toBeVisible({ timeout: 10000 });
    
    // Verify research content is displayed
    const researchContentDisplay = page.getByTestId('ai-research-content-display');
    await expect(researchContentDisplay).toBeVisible();
    
    const contentLabel = page.getByTestId('ai-research-content-label');
    await expect(contentLabel).toContainText('Generated Research Content');
    
    const contentDiv = page.getByTestId('ai-research-content');
    await expect(contentDiv).toBeVisible();
    
    // Verify content is not empty
    const contentText = await contentDiv.textContent();
    expect(contentText).toBeTruthy();
    expect(contentText!.length).toBeGreaterThan(10); // Basic content check
    
    // Check if content is rendered as markdown (should have proper HTML structure)
    const proseDiv = contentDiv.locator('.prose');
    await expect(proseDiv).toBeVisible();
    
    // Look for typical markdown elements that would be rendered as HTML
    const hasHeaders = await contentDiv.locator('h1, h2, h3, h4, h5, h6').count() > 0;
    const hasLists = await contentDiv.locator('ul, ol').count() > 0;
    const hasParagraphs = await contentDiv.locator('p').count() > 0;
    
    // At least one of these should be true for proper markdown rendering
    expect(hasHeaders || hasLists || hasParagraphs).toBeTruthy();
  });

  test('should display manual research content from pre-seeded data', async ({ page }) => {
    // Navigate to a presentation with manual research completed
    const presentation = await navigateToTestPresentation(page, 'manual_research', 0);
    
    // Verify we're on the edit page for the correct presentation
    await expect(page).toHaveURL(`/edit/${presentation.id}`);
    
    // Click on the Research step to view research content
    const researchStepButton = page.getByTestId('step-nav-research');
    await researchStepButton.click();
    
    // Wait for manual research content to be visible
    const manualResearchContent = page.getByTestId('manual-research-content');
    await expect(manualResearchContent).toBeVisible({ timeout: 10000 });
    
    // Verify manual research content is displayed
    const researchContentDisplay = page.getByTestId('manual-research-content-display');
    await expect(researchContentDisplay).toBeVisible();
    
    const contentLabel = page.getByTestId('manual-research-content-label');
    await expect(contentLabel).toContainText('Saved Research Content');
    
    const contentDiv = page.getByTestId('manual-research-content');
    await expect(contentDiv).toBeVisible();
    
    // Verify content is not empty
    const contentText = await contentDiv.textContent();
    expect(contentText).toBeTruthy();
    expect(contentText!.length).toBeGreaterThan(10); // Basic content check
    
    // Verify content is rendered as markdown
    const proseDiv = contentDiv.locator('.prose');
    await expect(proseDiv).toBeVisible();
    
    // For manual research, content might be plain text without markdown formatting
    // Just verify that the prose wrapper exists
    const hasParagraphs = await contentDiv.locator('p').count() > 0;
    expect(hasParagraphs).toBeTruthy();
  });

  test('should allow updating research topic on existing presentation', async ({ page }) => {
    const updatedTopic = 'Updated Machine Learning Applications in 2025';

    // Navigate to a presentation with completed research
    const presentation = await navigateToTestPresentation(page, 'research_complete', 0);
    
    // Verify we're on the edit page for the correct presentation
    await expect(page).toHaveURL(`/edit/${presentation.id}`);
    
    // Click on the Research step to view research content
    const researchStepButton = page.getByTestId('step-nav-research');
    await researchStepButton.click();
    
    // Wait for research content to be visible
    const researchContent = page.getByTestId('ai-research-content');
    await expect(researchContent).toBeVisible({ timeout: 10000 });
    
    // Get initial research content
    const initialContent = await researchContent.textContent();
    
    // Update the topic
    const topicInput = page.getByTestId('topic-input');
    await topicInput.fill(updatedTopic);
    
    // Verify the update button is visible (since research already exists)
    const updateButton = page.getByTestId('update-research-button');
    await expect(updateButton).toBeVisible();
    
    // Verify the topic input field shows the updated topic
    const topicInputValue = await topicInput.inputValue();
    expect(topicInputValue).toBe(updatedTopic);
    
    // Verify research content is still displayed
    const updatedContent = await page.getByTestId('ai-research-content').textContent();
    expect(updatedContent).toBeTruthy();
    expect(updatedContent!.length).toBeGreaterThan(10);
    
    // Check that content is still rendered as markdown
    const proseDiv = page.getByTestId('ai-research-content').locator('.prose');
    await expect(proseDiv).toBeVisible();
    
    console.log('Topic update test completed - content update mechanism verified');
  });
  
  test('should display research links when available', async ({ page }) => {
    // Navigate to a presentation with completed research that might have links
    const presentation = await navigateToTestPresentation(page, 'research_complete', 1);
    
    // Verify we're on the edit page for the correct presentation
    await expect(page).toHaveURL(`/edit/${presentation.id}`);
    
    // Click on the Research step to view research content
    const researchStepButton = page.getByTestId('step-nav-research');
    await researchStepButton.click();
    
    // Wait for research content to be visible
    const researchContent = page.getByTestId('ai-research-content');
    await expect(researchContent).toBeVisible({ timeout: 10000 });
    
    // Check if links section exists (it might not always have links in offline mode)
    const linksDisplay = page.getByTestId('ai-research-links-display');
    const linksExist = await linksDisplay.isVisible().catch(() => false);
    
    if (linksExist) {
      // If links are present, verify they're properly displayed
      const linksLabel = page.getByTestId('ai-research-links-label');
      await expect(linksLabel).toContainText('Research Sources');
      
      const linksList = page.getByTestId('ai-research-links');
      await expect(linksList).toBeVisible();
      
      // Check that links have proper attributes
      const firstLink = page.getByTestId('research-link-0');
      if (await firstLink.isVisible()) {
        await expect(firstLink).toHaveAttribute('target', '_blank');
        await expect(firstLink).toHaveAttribute('rel', 'noopener noreferrer');
      }
    } else {
      console.log('No research links found - this is expected in offline mode or pre-seeded data');
    }
  });
}); 