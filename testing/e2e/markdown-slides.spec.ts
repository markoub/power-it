import { test, expect } from "@playwright/test";
import { navigateToTestPresentation, verifyPresentationSteps } from "./utils";

test.describe("Markdown Slides", () => {
  test.setTimeout(60000);
  
  test("slides render markdown content correctly", async ({ page }) => {
    // Use pre-seeded presentation with completed slides
    const presentation = await navigateToTestPresentation(page, "slides_complete");
    console.log(`✅ Using test presentation: ${presentation.name} (ID: ${presentation.id})`);
    
    // Verify the presentation has completed slides
    await verifyPresentationSteps(page, presentation);
    
    // Navigate to slides step to see the existing slides
    const slidesNavButton = page.getByTestId('step-nav-slides');
    await expect(slidesNavButton).toBeVisible();
    await slidesNavButton.click();
    console.log("✅ Navigated to slides step");
    
    // Wait for slide thumbnails to be visible
    await page.waitForSelector('[data-testid^="slide-thumbnail-"]', { timeout: 10000 });
    
    // Click on the first slide to edit it
    await page.getByTestId("slide-thumbnail-0").click();
    console.log("✅ Selected first slide for editing");
    
    // Switch to edit mode
    await page.getByRole('tab', { name: 'Edit' }).click();
    console.log("✅ Switched to edit mode");
    
    // Add markdown content to test
    const markdownContent = `# Main Heading
## Subheading
This is **bold text** and this is *italic text*.

- First bullet point
- Second bullet point
- Third bullet point

1. Numbered list item 1
2. Numbered list item 2

> This is a blockquote

\`\`\`
This is code block
\`\`\``;

    // Clear existing content and add markdown
    const contentTextarea = page.locator('textarea').nth(1); // Second textarea is content
    await contentTextarea.fill(markdownContent);
    console.log("✅ Added markdown content");
    
    // Switch to preview mode to see rendered markdown
    await page.getByRole('tab', { name: 'Preview' }).click();
    console.log("✅ Switched to preview mode");
    
    // Wait for markdown content to be rendered by checking for specific elements
    // Find the main slide preview (not the thumbnail)
    const slidePreview = page.locator('.prose').first();
    await expect(slidePreview.locator('h1')).toContainText('Main Heading');
    
    // Check that headings are rendered
    await expect(slidePreview.locator('h2')).toContainText('Subheading');
    console.log("✅ Headings rendered correctly");
    
    // Check that bold and italic text are rendered
    await expect(slidePreview.locator('strong')).toContainText('bold text');
    await expect(slidePreview.locator('em')).toContainText('italic text');
    console.log("✅ Bold and italic text rendered correctly");
    
    // Check that lists are rendered
    await expect(slidePreview.locator('ul li')).toHaveCount(3);
    await expect(slidePreview.locator('ol li')).toHaveCount(2);
    console.log("✅ Lists rendered correctly");
    
    // Check that blockquote is rendered
    await expect(slidePreview.locator('blockquote')).toContainText('This is a blockquote');
    console.log("✅ Blockquote rendered correctly");
    
    // Check that code block is rendered
    await expect(slidePreview.locator('code')).toContainText('This is code block');
    console.log("✅ Code block rendered correctly");
    
    console.log("🎉 All markdown elements rendered successfully!");
  });
  
  test("markdown works in mini slide previews", async ({ page }) => {
    // Use pre-seeded presentation with completed everything (ID 11)
    const presentation = await navigateToTestPresentation(page, "complete");
    console.log(`✅ Using test presentation: ${presentation.name} (ID: ${presentation.id})`);
    
    // Verify the presentation has all steps completed
    await verifyPresentationSteps(page, presentation);
    
    // Navigate to slides step first to edit a slide
    const slidesNavButton = page.getByTestId('step-nav-slides');
    await slidesNavButton.click();
    console.log("✅ Navigated to slides step");
    
    // Wait for slide thumbnails to be visible
    await page.waitForSelector('[data-testid^="slide-thumbnail-"]', { timeout: 10000 });
    
    // Click on the first slide to edit it
    await page.getByTestId("slide-thumbnail-0").click();
    console.log("✅ Selected first slide for editing");
    
    // Switch to edit mode
    await page.getByRole('tab', { name: 'Edit' }).click();
    
    // Add markdown content to test
    const markdownContent = `# Test Heading
This slide has **bold** and *italic* text for testing mini previews.`;

    // Clear existing content and add markdown
    const contentTextarea = page.locator('textarea').nth(1); // Second textarea is content
    await contentTextarea.fill(markdownContent);
    console.log("✅ Added markdown content to slide");
    
    // Navigate to compiled step to see mini previews
    console.log("🔍 Navigating to compiled step...");
    const compiledButton = page.getByTestId('step-nav-compiled');
    
    // Since this is a complete presentation, compiled step should be accessible
    await expect(compiledButton).toBeVisible();
    await expect(compiledButton).toBeEnabled();
    await compiledButton.click();
    console.log("✅ Navigated to compiled step");
    
    // Verify that we can see slide previews
    await page.waitForSelector('.prose', { timeout: 10000 });
    
    // Verify main slide preview is visible with markdown
    await expect(page.locator('.prose').first()).toBeVisible();
    console.log("✅ Main slide preview with markdown is visible");
    
    // Check if there are any thumbnail previews
    const thumbnails = await page.locator('[data-testid^="compiled-thumbnail-"]').count();
    if (thumbnails > 0) {
      console.log(`✅ Found ${thumbnails} thumbnail previews`);
      
      // Verify that the first thumbnail has markdown rendered
      const firstThumbnail = page.locator('[data-testid="compiled-thumbnail-0"]');
      if (await firstThumbnail.count() > 0) {
        // Thumbnail should contain the heading
        await expect(firstThumbnail.locator('h1')).toContainText('Test Heading');
        console.log("✅ Markdown heading visible in thumbnail");
      }
    } else {
      console.log("ℹ️ No compiled thumbnails found, checking main preview");
      
      // Verify main preview has the markdown content rendered
      const mainPreview = page.locator('.prose').first();
      await expect(mainPreview.locator('h1')).toContainText('Test Heading');
      await expect(mainPreview.locator('strong')).toContainText('bold');
      await expect(mainPreview.locator('em')).toContainText('italic');
      console.log("✅ Markdown rendering verified in main preview");
    }
    
    console.log("🎉 Markdown rendering in previews verified!");
  });
}); 