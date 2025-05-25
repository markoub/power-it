const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  await page.goto('http://localhost:3000/edit/3');
  await page.waitForTimeout(3000);
  
  const currentStep = await page.evaluate(() => window.currentStep);
  const completedSteps = await page.evaluate(() => window.completedSteps);
  const presentationSteps = await page.evaluate(() => window.presentation?.steps?.map(s => ({step: s.step, status: s.status})));
  
  console.log('Current step:', currentStep);
  console.log('Completed steps:', completedSteps);
  console.log('Presentation steps:', presentationSteps);
  
  await browser.close();
})(); 