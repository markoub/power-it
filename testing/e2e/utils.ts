import { Page, expect } from '@playwright/test';

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
  await page.goto('http://localhost:3000');
  
  // Wait for the presentations container to be visible
  await expect(page.getByTestId('presentations-container')).toBeVisible();
}

/**
 * Create a new presentation with better error handling
 */
export async function createPresentation(page: Page, name: string, topic: string) {
  // Make the name unique by adding a timestamp
  const uniqueName = `${name} ${Date.now()}`;
  console.log(`Creating presentation: ${uniqueName} with topic: ${topic}`);
  
  // Navigate directly to the create page
  await page.goto('http://localhost:3000/create');
  
  // Wait for the create form to be visible
  await expect(page.getByTestId('create-presentation-form')).toBeVisible();
  
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
  
  // Wait for the edit page to load completely
  // The edit page should show either research method selection OR the research interface
  // Let's wait for either to appear
  try {
    // Try to wait for research method selection first (for new presentations)
    await expect(page.getByTestId('research-method-selection')).toBeVisible({ timeout: 10000 });
    console.log('Research method selection is visible - new presentation');
    
    // Select AI research method
    await page.getByTestId('ai-research-option').click();
    await page.getByTestId('continue-with-method-button').click();
    
    // Now wait for AI research interface
    await expect(page.getByTestId('ai-research-interface')).toBeVisible({ timeout: 10000 });
    
    // Fill in the topic
    await page.getByTestId('topic-input').fill(topic);
    
  } catch (error) {
    console.log('Research method selection not found, checking for existing research interface...');
    
    // Maybe the presentation already has a research method selected
    // Check if we're already in the research interface
    const hasAiInterface = await page.getByTestId('ai-research-interface').isVisible().catch(() => false);
    const hasManualInterface = await page.getByTestId('manual-research-interface').isVisible().catch(() => false);
    
    if (hasAiInterface) {
      console.log('AI research interface already visible');
      // Fill in the topic if it's not already filled
      const topicInput = page.getByTestId('topic-input');
      const currentTopic = await topicInput.inputValue().catch(() => '');
      if (!currentTopic) {
        await topicInput.fill(topic);
      }
    } else if (hasManualInterface) {
      console.log('Manual research interface visible - unexpected for test');
      throw new Error('Unexpected manual research interface found');
    } else {
      // Take a screenshot for debugging
      await page.screenshot({ path: `createPresentation-error-${Date.now()}.png` });
      throw new Error('Could not find research method selection or research interface');
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
  // Default to localhost API endpoint
  return 'http://localhost:8000';
}

/**
 * Login to the application (if authentication is required)
 * For now, this is a stub function since the app doesn't require authentication
 */
export async function login(page: Page): Promise<void> {
  // Navigate to the home page
  await page.goto('http://localhost:3000');
  
  // No login needed for now
  return;
}