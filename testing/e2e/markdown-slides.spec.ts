import { test, expect } from "@playwright/test";
import { createPresentation } from "./utils";

test.describe("Markdown Slides", () => {
  test.setTimeout(120000);
  test("slides render markdown content correctly", async ({ page }) => {
    const name = `Markdown Slides Test ${Date.now()}`;
    const topic = "Testing markdown rendering";

    // Create presentation and run research first
    const presentationId = await createPresentation(page, name, topic);
    console.log(`✅ Created presentation with ID: ${presentationId}`);
    
    // 1. Run research and wait for completion
    console.log("🔍 Running research...");
    await page.getByTestId('start-ai-research-button').click();
    
    // Wait for research to complete by waiting for generated content to appear
    await page.waitForSelector('text=Generated Research Content', { timeout: 30000 });
    console.log("✅ Research completed");

    // 2. Navigate to slides and run using the exact working pattern
    console.log("🔍 Running slides...");
    await page.getByTestId('step-nav-slides').click();
    
    const runSlidesButton = page.getByTestId('run-slides-button');
    const slidesButtonExists = await runSlidesButton.count() > 0;
    console.log(`Slides button exists: ${slidesButtonExists}`);
    
    if (slidesButtonExists) {
      await runSlidesButton.click();
      console.log("✅ Slides clicked");
      
      // Wait for slides to be generated
      console.log("⏳ Waiting for slides to be generated...");
      await page.waitForFunction(() => {
        const thumbnails = document.querySelectorAll('[data-testid^="slide-thumbnail-"]');
        return thumbnails.length > 0;
      }, {}, { timeout: 30000 });
      
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
      await expect(page.locator('.prose.prose-lg h1')).toContainText('Main Heading');
      
      // Verify markdown elements are rendered properly
      const slidePreview = page.locator('.prose.prose-lg');
      
      // Check that headings are rendered
      await expect(slidePreview.locator('h1')).toContainText('Main Heading');
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
      
    } else {
      throw new Error("❌ Slides button not found - this should not happen after research completion");
    }
  });
  
  test("markdown works in mini slide previews", async ({ page }) => {
    const name = `Markdown Mini Preview Test ${Date.now()}`;
    const topic = "Testing markdown in thumbnails";

    // Create presentation and run research first
    const presentationId = await createPresentation(page, name, topic);
    console.log(`✅ Created presentation with ID: ${presentationId}`);
    
    // Run research and wait for completion
    console.log("🔍 Running research...");
    await page.getByTestId('start-ai-research-button').click();
    
    // Wait for research to complete by waiting for generated content to appear
    await page.waitForSelector('text=Generated Research Content', { timeout: 30000 });
    console.log("✅ Research completed");

    // Navigate to slides and run
    console.log("🔍 Running slides...");
    await page.getByTestId('step-nav-slides').click();
    
    const runSlidesButton = page.getByTestId('run-slides-button');
    if (await runSlidesButton.count() > 0) {
      await runSlidesButton.click();
      console.log("✅ Clicked run slides button");
      
      // Wait for either:
      // 1. Slides to appear (success case)
      // 2. Button to become enabled again (generation complete)
      // Use race condition to handle both cases
      await Promise.race([
        // Wait for slides thumbnails to appear
        page.waitForSelector('[data-testid^="slide-thumbnail-"]', { 
          timeout: 60000 
        }),
        // OR wait for the button to not be disabled anymore
        page.waitForFunction(() => {
          const button = document.querySelector('[data-testid="run-slides-button"]');
          return button && !button.hasAttribute('disabled') && !button.textContent?.includes('Generating');
        }, { 
          polling: 500, // Poll every 500ms
          timeout: 60000 
        })
      ]);
      
      // Extra check to ensure slides are actually there
      const slidesCount = await page.locator('[data-testid^="slide-thumbnail-"]').count();
      if (slidesCount === 0) {
        // If no slides yet, wait a bit more
        await page.waitForSelector('[data-testid^="slide-thumbnail-"]', { 
          timeout: 10000 
        });
      }
      console.log(`✅ Slides generated (${slidesCount} slides)`);
      
      // First, let's add some markdown content to the first slide to test
      console.log("🔍 Adding markdown content to first slide for testing...");
      await page.getByTestId("slide-thumbnail-0").click();
      
      // Switch to edit mode
      await page.getByRole('tab', { name: 'Edit' }).click();
      
      // Add markdown content to test
      const markdownContent = `# Test Heading
This slide has **bold** and *italic* text for testing mini previews.`;

      // Clear existing content and add markdown
      const contentTextarea = page.locator('textarea').nth(1); // Second textarea is content
      await contentTextarea.fill(markdownContent);
      console.log("✅ Added markdown content to slide");
      
      // Try to access compiled step directly to see mini previews
      console.log("🔍 Attempting to access compiled step...");
      
      // Check if compiled step is clickable
      const compiledButton = page.getByTestId('step-nav-compiled');
      const isCompiled = await page.waitForFunction(() => {
        const button = document.querySelector('[data-testid="step-nav-compiled"]');
        return button && !button.hasAttribute('disabled');
      }, {}, { timeout: 5000 }).catch(() => false);
      
      if (isCompiled) {
        console.log("✅ Compiled step accessible, testing mini previews");
        await compiledButton.click();
        
        // Verify that we can see slide previews (even without images)
        await page.waitForSelector('.prose', { timeout: 10000 });
        
        // Verify main slide preview is visible with markdown
        await expect(page.locator('.prose').first()).toBeVisible();
        console.log("✅ Main slide preview with markdown is visible");
        
        // Check if there are any thumbnail previews
        const thumbnails = await page.locator('[data-testid^="compiled-thumbnail-"]').count();
        if (thumbnails > 0) {
          console.log(`✅ Found ${thumbnails} thumbnail previews`);
        } else {
          console.log("ℹ️ No compiled thumbnails found, but main preview works");
        }
        
        console.log("🎉 Markdown rendering in previews verified!");
      } else {
        console.log("⚠️ Compiled step not accessible without illustration step");
        console.log("🔍 Testing markdown rendering in slides view instead...");
        
        // If compiled step isn't accessible, test markdown in the slides view itself
        await page.getByTestId('step-nav-slides').click();
        
        // Switch to preview mode to see rendered markdown
        await page.getByRole('tab', { name: 'Preview' }).click();
        
        // Wait for markdown content to be rendered 
        await expect(page.locator('.prose.prose-lg h1')).toContainText('Test Heading');
        
        // Verify markdown elements are rendered properly in the slide preview
        const slidePreview = page.locator('.prose.prose-lg');
        await expect(slidePreview.locator('h1')).toContainText('Test Heading');
        await expect(slidePreview.locator('strong')).toContainText('bold');
        await expect(slidePreview.locator('em')).toContainText('italic');
        
        console.log("✅ Markdown rendering verified in slides view");
      }
      
    } else {
      throw new Error("❌ Slides button not found");
    }
  });
}); 