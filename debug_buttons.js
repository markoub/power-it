const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  await page.goto('http://localhost:3000/edit/424');
  
  // Wait for page to load
  await page.waitForTimeout(3000);
  
  // Check for the run-images-button
  const runImagesButton = await page.evaluate(() => {
    const button = document.querySelector('[data-testid="run-images-button"]');
    return button ? {
      exists: true,
      text: button.textContent,
      visible: button.offsetParent !== null,
      disabled: button.disabled
    } : { exists: false };
  });
  
  console.log('run-images-button:', JSON.stringify(runImagesButton, null, 2));
  
  // Check all Generate buttons
  const generateButtons = await page.evaluate(() => {
    return Array.from(document.querySelectorAll('button'))
      .filter(b => b.textContent.includes('Generate'))
      .map(b => ({
        text: b.textContent.trim(),
        testId: b.getAttribute('data-testid'),
        visible: b.offsetParent !== null,
        disabled: b.disabled
      }));
  });
  
  console.log('All Generate buttons:', JSON.stringify(generateButtons, null, 2));
  
  await browser.close();
})(); 