const puppeteer = require('puppeteer');

(async () => {
  const browser = await puppeteer.launch({ headless: false });
  const page = await browser.newPage();
  
  // Enable request/response logging
  page.on('response', async (response) => {
    const url = response.url();
    if (url.includes('/wizard') && response.request().method() === 'POST') {
      console.log('\n=== WIZARD API RESPONSE ===');
      console.log('URL:', url);
      console.log('Status:', response.status());
      try {
        const responseBody = await response.json();
        console.log('Response Body:', JSON.stringify(responseBody, null, 2));
      } catch (e) {
        console.log('Could not parse response as JSON');
      }
      console.log('========================\n');
    }
  });

  try {
    // Navigate to production server
    await page.goto('http://localhost:3000');
    
    // Go to an existing presentation edit page
    await page.goto('http://localhost:3000/edit/1');
    
    // Wait for page to load
    await page.waitForSelector('[data-testid="step-nav-slides"]', { timeout: 10000 });
    
    // Click on slides step
    await page.click('[data-testid="step-nav-slides"]');
    
    // Wait for slides to load
    await page.waitForSelector('[data-testid="slide-thumbnail-0"]', { timeout: 10000 });
    
    // Click on first slide to select it
    await page.click('[data-testid="slide-thumbnail-0"]');
    
    // Wait for wizard to be ready
    await page.waitForSelector('[data-testid="wizard-input"]', { timeout: 10000 });
    
    // Type a message in wizard
    await page.type('[data-testid="wizard-input"]', 'Please improve this slide with better formatting and more engaging content');
    
    // Click send button
    await page.click('[data-testid="wizard-send-button"]');
    
    // Wait for response and suggestion box
    await page.waitForSelector('[data-testid="wizard-message-assistant"]', { timeout: 30000 });
    
    // Check if suggestion box appears
    const suggestionBox = await page.$('[data-testid="wizard-suggestion"]');
    if (suggestionBox) {
      console.log('✅ Suggestion box appeared!');
    } else {
      console.log('❌ No suggestion box found');
    }
    
    // Wait a bit to see the response
    await page.waitForTimeout(5000);
    
  } catch (error) {
    console.error('Error:', error);
  } finally {
    await browser.close();
  }
})();