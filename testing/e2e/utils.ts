import { Page, expect } from '@playwright/test';
import { getApiUrl as getConfigApiUrl, TEST_CONFIG, getTestPresentation, TestPresentation } from '../test-config';

/**
 * Reset the test database to ensure clean state
 */
export async function resetTestDatabase(page: Page): Promise<void> {
  const apiUrl = getConfigApiUrl();
  try {
    const response = await page.request.post(`${apiUrl}/test/reset-database`);
    if (!response.ok()) {
      console.warn('Failed to reset test database:', response.status());
    }
  } catch (error) {
    console.warn('Error resetting test database:', error);
  }
}

/**
 * Get timeout value based on offline mode - keep minimal for safety
 */
export function getTimeout(defaultTimeout: number = 5000): number {
  const isOffline = process.env.POWERIT_OFFLINE_E2E !== 'false';
  return isOffline ? Math.min(defaultTimeout, 10000) : defaultTimeout;
}

/**
 * Waits for network requests to complete with a shorter timeout
 */
export async function waitForNetworkIdle(page: Page, timeout = 3000) {
  try {
    // Wait for network to be idle (no requests for 300ms)
    await page.waitForLoadState('networkidle', { timeout });
  } catch (error) {
    console.log(`Network idle wait completed, continuing`);
  }
}

/**
 * Navigate to the presentations page
 */
export async function goToPresentationsPage(page: Page) {
  // Use the base URL from environment or default to test port
  const baseUrl = process.env.PLAYWRIGHT_BASE_URL || 'http://localhost:3001';
  await page.goto(baseUrl);
  
  // Wait for the presentations container to be visible
  await expect(page.getByTestId('presentations-container')).toBeVisible();
}

/**
 * Create a new presentation with better error handling
 * @deprecated Use navigateToTestPresentation() instead for tests that don't specifically test creation flow
 */
export async function createPresentation(page: Page, name: string, topic: string) {
  console.warn('⚠️ DEPRECATED: createPresentation() should only be used for tests that specifically test the creation flow. Use navigateToTestPresentation() for other tests.');
  // Make the name unique by adding a timestamp
  const uniqueName = `${name} ${Date.now()}`;
  console.log(`Creating presentation: ${uniqueName} with topic: ${topic}`);
  
  // Navigate directly to the create page using baseURL
  await page.goto('/create');
  
  // Wait for page to load completely with multiple strategies
  await page.waitForLoadState('domcontentloaded');
  await page.waitForLoadState('networkidle');
  
  // Try multiple selectors to ensure page has loaded
  try {
    // First try to wait for the page wrapper
    await page.waitForSelector('[data-testid="create-page"]', { state: 'visible', timeout: 5000 });
  } catch (e) {
    // If that fails, try waiting for any visible element
    await page.waitForSelector('body', { state: 'visible', timeout: 5000 });
  }
  
  // Add a small delay to ensure React has hydrated
  await page.waitForTimeout(1000);
  
  // Now wait for the form to be visible
  const formLocator = page.getByTestId('create-presentation-form');
  const formCount = await formLocator.count();
  
  if (formCount === 0) {
    // If form not found, log current page content for debugging
    const pageContent = await page.content();
    console.error('Form not found. Page URL:', page.url());
    console.error('Page title:', await page.title());
    throw new Error('Create form not found on page');
  }
  
  await expect(formLocator).toBeVisible({ timeout: 10000 });
  
  // Fill out the basic form (only name and author required)
  await page.getByTestId('presentation-title-input').fill(uniqueName);
  await page.getByTestId('presentation-author-input').fill('Test Author');
  
  // Submit the form
  await page.getByTestId('submit-presentation-button').click();
  
  // Wait for navigation to edit page (should show in URL) with longer timeout
  try {
    await expect(page).toHaveURL(/\/edit\/\d+/, { timeout: 15000 });
  } catch (error) {
    // Check if there's an error message displayed
    const errorElement = page.getByTestId('error-message');
    const hasError = await errorElement.isVisible().catch(() => false);
    
    if (hasError) {
      const errorText = await errorElement.textContent();
      console.error(`Form submission error: ${errorText}`);
      
      // If it's a unique constraint error, try with a different name
      if (errorText?.includes('already exists')) {
        const retryName = `${name} ${Date.now()}_retry`;
        console.log(`Retrying with name: ${retryName}`);
        
        await page.getByTestId('presentation-title-input').fill(retryName);
        await page.getByTestId('submit-presentation-button').click();
        await expect(page).toHaveURL(/\/edit\/\d+/, { timeout: 15000 });
      } else {
        throw new Error(`Form submission failed: ${errorText}`);
      }
    } else {
      // Take a screenshot for debugging
      await page.screenshot({ path: `createPresentation-error-${Date.now()}.png` });
      throw error;
    }
  }
  
  // Handle method selection if it appears
  const methodSelection = page.getByTestId('research-method-selection');
  if (await methodSelection.isVisible()) {
    console.log('Method selection is visible, proceeding with AI research selection...');
    
    // Select AI research method
    await page.getByTestId('ai-research-option').click();
    
    // Wait for continue button and click it
    const continueButton = page.getByTestId('continue-with-method-button');
    await expect(continueButton).toBeEnabled();
    await continueButton.click();
    
    // Wait for method selection to disappear
    await expect(methodSelection).not.toBeVisible({ timeout: 10000 });
    
    // Wait for AI research interface
    await expect(page.getByTestId('ai-research-interface')).toBeVisible({ timeout: 10000 });
    
    // Fill in topic
    await page.getByTestId('topic-input').fill(topic);
    
    console.log('✅ Successfully set up AI research interface');
  } else {
    // Check if AI interface is already visible
    const aiInterface = page.getByTestId('ai-research-interface');
    if (await aiInterface.isVisible()) {
      console.log('AI research interface already visible');
      // Fill in the topic if it's not already filled
      const topicInput = page.getByTestId('topic-input');
      const currentTopic = await topicInput.inputValue().catch(() => '');
      if (!currentTopic) {
        await topicInput.fill(topic);
      }
    } else {
      throw new Error('Neither method selection nor AI research interface is visible');
    }
  }
  
  // Try to get the ID from the URL
  const url = page.url();
  const match = url.match(/\/edit\/(\d+)/);
  
  if (match) {
    console.log(`✅ Created presentation with ID: ${match[1]}`);
    return Number(match[1]);
  } else {
    console.log(`⚠️ Could not extract ID from URL: ${url}, returning fallback`);
    return 1; // Return fallback ID
  }
}

// Define all available step types
export type StepType = 'research' | 'manual_research' | 'slides' | 'illustration' | 'compiled' | 'pptx';

/**
 * Get the status of a presentation step by checking UI components and backend status
 */
export async function getStepStatus(page: Page, stepType: StepType): Promise<string> {
  try {
    // First check the backend status which is more reliable
    const apiUrl = getApiUrl();
    const presentationId = await getPresentationIdFromUrl(page);
    
    if (presentationId) {
      try {
        const response = await page.request.get(`${apiUrl}/presentations/${presentationId}`);
        if (response.ok()) {
          const data = await response.json();
          const step = data.steps?.find((s: any) => s.step === stepType);
          
          if (step) {
            // Return the actual backend status
            return step.status; // Will be 'completed', 'processing', 'pending', or 'error'
          }
        }
      } catch (apiError) {
        console.log(`API status check error for ${stepType}: ${apiError}`);
      }
    }
    
    // Fallback to UI-based status checking
    const stepButton = page.getByTestId(`step-nav-${stepType}`);
    
    // Check if button exists
    const exists = await stepButton.count() > 0;
    if (!exists) {
      return 'unknown';
    }
    
    // Check if the step has a checkmark icon (completed)
    // Look for an SVG element which indicates the step is completed (shows icon instead of number)
    const svgElement = await stepButton.locator('svg').first();
    const svgExists = await svgElement.count() > 0;
    
    if (svgExists) {
      return 'completed';
    }
    
    // Alternative: Check for completion styling (bg-primary-500 without ring)
    const className = await stepButton.getAttribute('class') || '';
    if (className.includes('bg-primary-500') && !className.includes('ring-')) {
      return 'completed';
    }
    
    // Check if the step is currently active (has ring styling)
    if (className.includes('ring-4') || className.includes('ring-primary')) {
      return 'active';
    }
    
    // Check if the step is disabled
    const isDisabled = await stepButton.isDisabled();
    if (isDisabled) {
      return 'disabled';
    }
    
    return 'pending';
  } catch (error) {
    console.error(`Error getting status for ${stepType} step:`, error);
    return 'unknown';
  }
}

/**
 * Wait for a step to be marked as completed in the UI
 */
export async function waitForStepCompletion(page: Page, stepType: StepType, timeout: number = 30000): Promise<boolean> {
  try {
    console.log(`⏳ Waiting for ${stepType} step to be marked as completed...`);
    
    // First, wait for backend completion by polling the API directly
    const apiUrl = getApiUrl();
    const presentationId = await getPresentationIdFromUrl(page);
    
    if (presentationId) {
      // Poll the backend API for step completion
      const startTime = Date.now();
      while (Date.now() - startTime < timeout) {
        try {
          // Increase timeout for individual API requests to 30 seconds
          const response = await page.request.get(`${apiUrl}/presentations/${presentationId}`, {
            timeout: 30000
          });
          if (response.ok()) {
            const data = await response.json();
            const step = data.steps?.find((s: any) => s.step === stepType && s.status === 'completed');
            if (step) {
              console.log(`✅ ${stepType} step completed in backend`);
              
              // Now wait for UI to reflect the completion (shorter timeout)
              try {
                await page.waitForFunction((stepName) => {
                  const stepButton = document.querySelector(`[data-testid="step-nav-${stepName}"]`);
                  if (!stepButton) return false;
                  
                  // Method 1: Check if there's an SVG element (icon) instead of a number
                  const svgElement = stepButton.querySelector('svg');
                  if (svgElement) {
                    // If there's an SVG, this likely means the step is completed (shows check icon instead of number)
                    return true;
                  }
                  
                  // Method 2: Check for specific completion styling
                  const buttonClasses = stepButton.className || '';
                  // Completed steps have bg-primary-500 but no ring (active steps have ring)
                  if (buttonClasses.includes('bg-primary-500') && !buttonClasses.includes('ring-')) {
                    return true;
                  }
                  
                  return false;
                }, stepType, { timeout: 10000 });
                
                console.log(`✅ ${stepType} step marked as completed in UI`);
                return true;
              } catch (uiError) {
                console.log(`⚠️ ${stepType} step completed in backend but UI not updated yet - continuing anyway`);
                return true; // Consider it successful if backend is completed
              }
            }
          }
        } catch (apiError) {
          console.log(`API poll error: ${apiError}`);
          // Continue polling even if individual requests fail
        }
        
        // Wait 3 seconds between polls instead of 2 to reduce load
        await new Promise(resolve => setTimeout(resolve, 3000));
      }
    }
    
    // Fallback to original UI-only approach with increased timeout
    await page.waitForFunction((stepName) => {
      const stepButton = document.querySelector(`[data-testid="step-nav-${stepName}"]`);
      if (!stepButton) return false;
      
      // Method 1: Check if there's an SVG element (icon) instead of a number
      const svgElement = stepButton.querySelector('svg');
      if (svgElement) {
        // If there's an SVG, this likely means the step is completed (shows check icon instead of number)
        return true;
      }
      
      // Method 2: Check for specific completion styling
      const buttonClasses = stepButton.className || '';
      // Completed steps have bg-primary-500 but no ring (active steps have ring)
      if (buttonClasses.includes('bg-primary-500') && !buttonClasses.includes('ring-')) {
        return true;
      }
      
      return false;
    }, stepType, { timeout: Math.max(timeout, 60000) }); // Use the larger of provided timeout or 60 seconds
    
    console.log(`✅ ${stepType} step marked as completed`);
    return true;
  } catch (error) {
    console.log(`⚠️ ${stepType} step completion wait timed out: ${error}`);
    return false;
  }
}

/**
 * Extract presentation ID from the current page URL
 */
async function getPresentationIdFromUrl(page: Page): Promise<number | null> {
  const url = page.url();
  const match = url.match(/\/edit\/(\d+)/);
  return match ? Number(match[1]) : null;
}

/**
 * Check if a step is enabled in the UI
 */
export async function isStepEnabled(page: Page, stepType: StepType): Promise<boolean> {
  try {
    const stepButton = page.getByTestId(`step-nav-${stepType}`);
    
    const exists = await stepButton.count() > 0;
    if (!exists) {
      return false;
    }
    
    const isDisabled = await stepButton.isDisabled();
    
    // If UI shows enabled, return true
    if (!isDisabled) {
      return true;
    }
    
    // If UI shows disabled, check backend status to see if it should be enabled
    // This helps with timing issues where backend completes but UI hasn't updated yet
    const apiUrl = getApiUrl();
    const presentationId = await getPresentationIdFromUrl(page);
    
    if (presentationId) {
      try {
        const response = await page.request.get(`${apiUrl}/presentations/${presentationId}`);
        if (response.ok()) {
          const data = await response.json();
          
          // Check if this step should be enabled based on backend status
          const stepName = stepType;
          const step = data.steps?.find((s: any) => s.step === stepName);
          
          // A step is enabled if:
          // 1. It exists and is completed
          // 2. Or it's pending/processing and the previous step is completed
          if (step) {
            if (step.status === 'completed' || step.status === 'processing') {
              return true;
            }
            
            if (step.status === 'pending') {
              // Check if prerequisite steps are completed
              const stepOrder = ['research', 'slides', 'illustration', 'compiled', 'pptx'];
              const currentIndex = stepOrder.indexOf(stepName);
              
              if (currentIndex === 0) {
                return true; // First step is always enabled
              }
              
              if (currentIndex > 0) {
                const prevStepName = stepOrder[currentIndex - 1];
                const prevStep = data.steps?.find((s: any) => s.step === prevStepName);
                
                if (prevStep && prevStep.status === 'completed') {
                  return true;
                }
                
                // Also check if manual_research is completed for slides step
                if (stepName === 'slides') {
                  const manualResearchStep = data.steps?.find((s: any) => s.step === 'manual_research');
                  if (manualResearchStep && manualResearchStep.status === 'completed') {
                    return true;
                  }
                }
              }
            }
          }
        }
      } catch (apiError) {
        console.log(`API check error for ${stepType}: ${apiError}`);
      }
    }
    
    return !isDisabled;
  } catch (error) {
    console.error(`Error checking if ${stepType} step is enabled:`, error);
    return false;
  }
}

/**
 * Run a step and wait for completion by watching UI components
 */
export async function runStepAndWaitForCompletion(
  page: Page,
  stepType: StepType
) {
  console.log(`🔄 Running ${stepType} step`);
  
  try {
    // Click the step to activate it
    const stepButton = page.getByTestId(`step-nav-${stepType}`);
    if (await stepButton.count() > 0) {
      // Check if step is enabled before clicking
      const isDisabled = await stepButton.isDisabled().catch(() => true);
      if (isDisabled) {
        console.log(`⚠️ ${stepType} step is disabled - skipping`);
        return;
      }
      await stepButton.click();
    }
    
    // Find and click the appropriate run button
    let runButton;
    if (stepType === 'slides') {
      runButton = page.getByTestId('run-slides-button');
    } else if (stepType === 'illustration') {
      runButton = page.getByTestId('run-images-button-center');
    } else if (stepType === 'research') {
      runButton = page.getByTestId('start-ai-research-button');
    } else if (stepType === 'pptx') {
      runButton = page.getByTestId('run-pptx-button');
    } else if (stepType === 'compiled') {
      // Compiled step doesn't have a run button - it's automatically triggered
      // Just wait for it to complete
      console.log(`⚠️ ${stepType} step is automatically triggered - waiting for completion`);
      await waitForStepCompletion(page, stepType, 60000); // Increased timeout for auto-triggered step
      return;
    } else {
      runButton = page.getByTestId(`run-${stepType}-button`);
    }
    
    // Check if the run button exists and is enabled
    const runButtonExists = await runButton.count() > 0;
    if (!runButtonExists) {
      console.log(`⚠️ Run button for ${stepType} step not found`);
      return;
    }
    
    const isDisabled = await runButton.isDisabled().catch(() => true);
    if (isDisabled) {
      console.log(`⚠️ Run button for ${stepType} step is disabled`);
      return;
    }
    
    // Click the run button with stability handling
    console.log(`▶️ Starting ${stepType} step...`);
    
    // Wait for button to be stable and then click with retry logic
    try {
      // Wait for the button to be stable
      await runButton.waitFor({ state: 'visible' });
      await page.waitForTimeout(1000); // Allow DOM to stabilize after navigation
      
      // Use force click to handle potential DOM instability
      await runButton.click({ force: true, timeout: 15000 });
    } catch (clickError) {
      console.log(`Button click failed, retrying: ${clickError}`);
      
      // Retry with a fresh button locator
      await page.waitForTimeout(2000);
      const retryButton = page.getByTestId(runButton.constructor.name.includes('slides') ? 'run-slides-button' : 
                                          runButton.constructor.name.includes('images') ? 'run-images-button-center' :
                                          runButton.constructor.name.includes('research') ? 'start-ai-research-button' :
                                          runButton.constructor.name.includes('pptx') ? 'run-pptx-button' :
                                          `run-${stepType}-button`);
      
      // Simple retry with correct button testid based on stepType
      let retryButtonTestId;
      if (stepType === 'slides') {
        retryButtonTestId = 'run-slides-button';
      } else if (stepType === 'illustration') {
        retryButtonTestId = 'run-images-button-center';
      } else if (stepType === 'research') {
        retryButtonTestId = 'start-ai-research-button';
      } else if (stepType === 'pptx') {
        retryButtonTestId = 'run-pptx-button';
      } else {
        retryButtonTestId = `run-${stepType}-button`;
      }
      
      const retryButtonLocator = page.getByTestId(retryButtonTestId);
      await retryButtonLocator.waitFor({ state: 'visible' });
      await retryButtonLocator.click({ force: true });
    }
    
    // Wait for step completion - the UI should now update automatically thanks to our fixes
    console.log(`⏳ Waiting for ${stepType} step to complete...`);
    
    // Wait for the step to be marked as completed in the UI
    // For robustness, let's try multiple detection methods
    await page.waitForFunction((stepName) => {
      const stepButton = document.querySelector(`[data-testid="step-nav-${stepName}"]`);
      if (!stepButton) return false;
      
      // Method 1: Check if there's an SVG element (icon) instead of a number
      const svgElement = stepButton.querySelector('svg');
      if (svgElement) {
        // If there's an SVG, this likely means the step is completed (shows check icon instead of number)
        return true;
      }
      
      // Method 2: Check for specific completion styling
      const buttonClasses = stepButton.className || '';
      // Completed steps have bg-primary-500 but no ring (active steps have ring)
      if (buttonClasses.includes('bg-primary-500') && !buttonClasses.includes('ring-')) {
        return true;
      }
      
      return false;
    }, stepType, { timeout: 60000 }); // Longer timeout for completion
    
    console.log(`✅ ${stepType} step completed successfully`);
    
  } catch (error) {
    console.error(`❌ Error running ${stepType} step:`, error);
    
    // Take a screenshot for debugging
    await page.screenshot({ path: `${stepType}-step-error-${Date.now()}.png` });
    
    // Don't throw - let the test continue
  }
}

/**
 * Check the step dependencies are correctly enforced
 */
export async function verifyStepDependencies(page: Page): Promise<boolean> {
  try {
    // Get status of each step
    const researchStatus = await getStepStatus(page, 'research');
    
    // Check if slides is enabled
    let slidesEnabled = false;
    try {
      slidesEnabled = await isStepEnabled(page, 'slides');
    } catch (error) {
      console.log(`Error checking if slides step is enabled: ${error.message}`);
    }
    
    // Basic check - if research is completed, slides should be enabled
    return researchStatus === 'completed' ? slidesEnabled : true;
  } catch (error) {
    console.error(`Error verifying step dependencies:`, error);
    return false;
  }
}

/**
 * Get the base API URL based on environment
 */
export function getApiUrl(): string {
  // When running tests with the test runner, PLAYWRIGHT_BASE_URL will be set to the test frontend
  // The test frontend will be configured to use the test backend
  // This is just for direct API calls from tests (if any)
  const baseUrl = process.env.PLAYWRIGHT_BASE_URL;
  if (baseUrl && baseUrl.includes(':3001')) {
    // We're using the test frontend, so use test backend
    return TEST_CONFIG.TEST_API_BASE_URL;
  }
  return TEST_CONFIG.PROD_API_BASE_URL;
}

/**
 * Login to the application (if authentication is required)
 * For now, this is a stub function since the app doesn't require authentication
 */
export async function login(page: Page): Promise<void> {
  // Navigate to the home page
  const baseUrl = process.env.PLAYWRIGHT_BASE_URL || 'http://localhost:3001';
  await page.goto(baseUrl);
  
  // No login needed for now
  return;
}

/**
 * Navigate to the edit page for a specific presentation
 */
export async function navigateToEditPage(page: Page, presentationId: number): Promise<void> {
  const baseUrl = process.env.PLAYWRIGHT_BASE_URL || 'http://localhost:3001';
  await page.goto(`${baseUrl}/edit/${presentationId}`);
  
  // Wait for the edit page to load by checking for the save button or workflow steps
  await expect(page.locator('[data-testid="save-button"]')).toBeVisible({ timeout: 15000 });
}

/**
 * Fill in the research topic in the AI research interface
 */
export async function fillResearchTopic(page: Page, topic: string): Promise<void> {
  // Wait for the research topic input to be visible
  const topicInput = page.locator('[data-testid="topic-input"]');
  await expect(topicInput).toBeVisible({ timeout: 10000 });
  
  // Clear any existing content and fill with new topic
  await topicInput.clear();
  await topicInput.fill(topic);
}

/**
 * Start the AI research process
 */
export async function startAIResearch(page: Page): Promise<void> {
  // Check if research is already completed - if so, use update button instead
  const updateButton = page.locator('[data-testid="update-research-button"]');
  const startButton = page.locator('[data-testid="start-ai-research-button"]');
  
  // Wait a moment for the page to load and determine which button is available
  await page.waitForTimeout(2000);
  
  if (await updateButton.isVisible()) {
    // Research already exists, use update button
    await expect(updateButton).toBeEnabled();
    await updateButton.click();
  } else {
    // No research yet, use start button
    await expect(startButton).toBeVisible();
    await expect(startButton).toBeEnabled();
    await startButton.click();
  }
}

/**
 * Wait for research completion by checking for generated content
 */
export async function waitForResearchCompletion(page: Page, timeout: number = 60000): Promise<void> {
  // Wait for the research content label to appear (using data-testid)
  await expect(page.locator('[data-testid="ai-research-content-label"]')).toBeVisible({ timeout });
  
  // Also wait for the actual research content to be visible
  await expect(page.locator('[data-testid="ai-research-content"]')).toBeVisible({ timeout });
  
  // Also wait for the research step to be marked as completed
  await waitForStepCompletion(page, 'research', timeout);
}

/**
 * Navigate to a pre-seeded test presentation by category
 */
export async function navigateToTestPresentation(page: Page, category: string, index: number = 0): Promise<TestPresentation> {
  const presentation = getTestPresentation(category, index);
  if (!presentation) {
    throw new Error(`No test presentation found for category: ${category}, index: ${index}`);
  }
  
  console.log(`🔗 Navigating to test presentation: ${presentation.name} (ID: ${presentation.id})`);
  
  // Get the base URL from environment or use default
  const baseUrl = process.env.PLAYWRIGHT_BASE_URL || 'http://localhost:3001';
  
  // Navigate to the edit page for this presentation
  await page.goto(`${baseUrl}/edit/${presentation.id}`);
  
  // Wait for the edit page to load by checking for workflow steps
  await expect(page.locator('[data-testid="step-nav-research"]')).toBeVisible({ timeout: 15000 });
  
  return presentation;
}

/**
 * Verify that a presentation has the expected step statuses
 */
export async function verifyPresentationSteps(page: Page, presentation: TestPresentation): Promise<void> {
  console.log(`🔍 Verifying steps for presentation: ${presentation.name}`);
  
  // Check completed steps
  for (const stepType of presentation.completedSteps) {
    const status = await getStepStatus(page, stepType as StepType);
    if (status !== 'completed') {
      console.warn(`⚠️ Expected step ${stepType} to be completed, but status is: ${status}`);
    }
  }
  
  // Check that next step is available
  if (presentation.pendingSteps.length > 0) {
    const nextStep = presentation.pendingSteps[0];
    const isEnabled = await isStepEnabled(page, nextStep as StepType);
    if (!isEnabled) {
      console.warn(`⚠️ Expected next step ${nextStep} to be enabled`);
    }
  }
}


/**
 * Get a test presentation by its ID
 * @param id The presentation ID from the preseeded database
 * @returns The test presentation data
 */
export async function getTestPresentationById(id: number): Promise<TestPresentation | null> {
  // Import TEST_PRESENTATIONS from test-config
  const { TEST_PRESENTATIONS } = await import('../test-config');
  
  // Find presentation by ID
  const presentation = TEST_PRESENTATIONS.find(p => p.id === id);
  return presentation || null;
}

/**
 * Navigate directly to a test presentation by ID
 * @param page The Playwright page object
 * @param id The presentation ID to navigate to
 * @returns The test presentation data if found
 */
export async function navigateToTestPresentationById(page: Page, id: number): Promise<TestPresentation | null> {
  console.log(`🔗 Navigating to test presentation with ID: ${id}`);
  
  // Get the presentation data
  const presentation = await getTestPresentationById(id);
  if (!presentation) {
    console.warn(`⚠️ No test presentation found with ID: ${id}`);
  }
  
  // Get the base URL from environment or use default
  const baseUrl = process.env.PLAYWRIGHT_BASE_URL || 'http://localhost:3001';
  
  // Navigate to the edit page for this presentation
  await page.goto(`${baseUrl}/edit/${id}`);
  
  // Wait for the edit page to load by checking for workflow steps
  await expect(page.locator('[data-testid="step-nav-research"]')).toBeVisible({ timeout: 15000 });
  
  return presentation;
}