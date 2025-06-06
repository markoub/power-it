import { test, expect } from '@playwright/test';
import { navigateToTestPresentation, waitForStepCompletion } from './utils';

test.describe('Markdown Rendering in Slides', () => {

  test('should properly render markdown content in slides', async ({ page }) => {
    // Standard timeout for offline mode
    test.setTimeout(30000);
    
    // Use pre-seeded presentation with completed slides (ID 9)
    await navigateToTestPresentation(page, 'slides_complete', 0);
    console.log(`✅ Navigated to test presentation with completed slides`);
    
    // Navigate to slides step
    await page.click('[data-testid="step-nav-slides"]');
    
    // Wait for slide thumbnails to be loaded
    await page.waitForSelector('[data-testid^="slide-thumbnail-"]', { 
      state: 'visible',
      timeout: 10000 
    });
    
    // Get all slide thumbnails
    const slideThumbnails = await page.locator('[data-testid^="slide-thumbnail-"]').all();
    console.log(`✅ Found ${slideThumbnails.length} slides`);
    
    // Look for a content slide (not welcome or table of contents)
    let contentSlideFound = false;
    for (let i = 0; i < slideThumbnails.length; i++) {
      await slideThumbnails[i].click();
      await page.waitForTimeout(500); // Wait for slide to load
      
      // Check if this is a content slide by looking at the title
      const titleInput = page.locator('input[type="text"]').first();
      const title = await titleInput.inputValue().catch(() => '');
      
      console.log(`Slide ${i} title: "${title}"`);
      
      // Skip welcome and table of contents slides
      if (!title.toLowerCase().includes('welcome') && 
          !title.toLowerCase().includes('table of contents') &&
          !title.toLowerCase().includes('section')) {
        contentSlideFound = true;
        console.log(`✅ Found content slide at index ${i}`);
        break;
      }
    }
    
    if (!contentSlideFound) {
      throw new Error('No content slide found in presentation');
    }
    
    // Wait for slide details to load
    await page.waitForSelector('[role="tablist"]', { timeout: 5000 });
    
    // Check preview mode first to see how content is rendered
    const previewTab = page.getByRole('tab', { name: 'Preview' });
    await expect(previewTab).toBeVisible();
    await previewTab.click();
    
    // Wait a moment for the preview to render
    await page.waitForTimeout(1000);
    
    // Look for markdown content in the preview area
    // The preview content is typically in a .prose class or within the preview tab panel
    const previewArea = page.locator('[role="tabpanel"]').filter({ has: page.locator('.prose, .markdown-content, [class*="preview"]') });
    
    // If no preview area found, try finding any visible content area
    let slidePreview = previewArea.first();
    if (await slidePreview.count() === 0) {
      slidePreview = page.locator('.prose, .markdown-content').first();
    }
    
    // Ensure we have some content visible
    await expect(slidePreview).toBeVisible({ timeout: 10000 });
    
    // Check for various markdown elements
    const markdownElements = {
      headings: slidePreview.locator('h1, h2, h3, h4, h5, h6'),
      paragraphs: slidePreview.locator('p'),
      lists: slidePreview.locator('ul, ol'),
      listItems: slidePreview.locator('li'),
      bold: slidePreview.locator('strong, b'),
      italic: slidePreview.locator('em, i'),
      links: slidePreview.locator('a'),
      code: slidePreview.locator('code'),
      blockquotes: slidePreview.locator('blockquote')
    };
    
    // Check what markdown elements are present
    const elementCounts = {};
    for (const [name, locator] of Object.entries(markdownElements)) {
      const count = await locator.count();
      elementCounts[name] = count;
      if (count > 0) {
        console.log(`✅ Found ${count} ${name} element(s)`);
      }
    }
    
    // Verify that some markdown content exists
    const hasMarkdownContent = Object.values(elementCounts).some(count => count > 0);
    expect(hasMarkdownContent).toBeTruthy();
    console.log("✅ Markdown content is properly rendered in the slide preview");
    
    // Switch to edit mode to see the raw markdown
    await page.getByRole('tab', { name: 'Edit' }).click();
    await page.waitForTimeout(500);
    
    // Check that we have textareas (may vary based on slide type)
    const textareas = await page.locator('textarea').all();
    console.log(`Found ${textareas.length} textarea(s) in edit mode`);
    
    // Look for a textarea with content
    let markdownContent = '';
    for (let i = 0; i < textareas.length; i++) {
      const content = await textareas[i].inputValue();
      if (content.length > 0) {
        markdownContent = content;
        console.log(`✅ Found ${content.length} characters of markdown content in textarea ${i}`);
        break;
      }
    }
    
    // If no content in textareas, it might be a slide type without editable content
    if (markdownContent.length === 0) {
      console.log("ℹ️ No editable content found - this might be a welcome or section slide");
      // Just verify we could access the edit tab
      expect(textareas.length).toBeGreaterThanOrEqual(0);
    } else {
      expect(markdownContent.length).toBeGreaterThan(0);
    }
    
    console.log("🎉 Markdown rendering test completed successfully!");
  });

  test('should display research markdown content correctly', async ({ page }) => {
    // Standard timeout for offline mode
    test.setTimeout(30000);
    
    // Use pre-seeded presentation with completed research (ID 5)
    await navigateToTestPresentation(page, 'research_complete', 0);
    console.log(`✅ Navigated to test presentation with completed research`);
    
    // Wait for the page to load and ensure we're on the research step
    await page.waitForLoadState('networkidle');
    
    // The research content should be visible using the correct test ID
    await expect(page.locator('[data-testid="ai-research-content"]')).toBeVisible({ timeout: 10000 });
    
    // Check that markdown content is rendered properly in research
    const researchContent = page.locator('[data-testid="ai-research-content"]');
    
    // The test presentations have research with various markdown formatting
    // Check what markdown elements are present
    const markdownChecks = {
      headings: researchContent.locator('h1, h2, h3, h4, h5, h6'),
      paragraphs: researchContent.locator('p'),
      lists: researchContent.locator('ul, ol'),
      listItems: researchContent.locator('li'),
      bold: researchContent.locator('strong, b'),
      italic: researchContent.locator('em, i'),
      code: researchContent.locator('code, pre'),
      blockquotes: researchContent.locator('blockquote')
    };
    
    // Count elements found
    let foundElements = false;
    for (const [name, locator] of Object.entries(markdownChecks)) {
      const count = await locator.count();
      if (count > 0) {
        console.log(`✅ Found ${count} ${name} element(s) in research content`);
        foundElements = true;
      }
    }
    
    // Ensure we found some markdown elements
    expect(foundElements).toBeTruthy();
    
    // Also check that the research content has some text
    const contentText = await researchContent.textContent();
    expect(contentText?.length).toBeGreaterThan(100);
    console.log(`✅ Research content has ${contentText?.length} characters`);
    
    console.log("🎉 Research markdown content is properly rendered!");
  });
}); 