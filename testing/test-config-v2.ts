/**
 * Enhanced Test Configuration V2 for E2E Tests
 * 
 * This file provides comprehensive configuration for ALL E2E tests
 * with preseeded presentations to eliminate the need for creating
 * new presentations during tests.
 */

export interface TestPresentation {
  id: number;
  name: string;
  topic: string;
  author: string;
  category: string;
  description: string;
  completedSteps: string[];
  pendingSteps: string[];
  specialFlags?: {
    aiResearchSelected?: boolean;
    manualResearchSelected?: boolean;
    hasError?: boolean;
    isProcessing?: boolean;
  };
}

/**
 * Comprehensive pre-seeded test presentations for ALL E2E tests
 */
export const TEST_PRESENTATIONS_V2: TestPresentation[] = [
  // ========== Fresh Presentations (1-4) ==========
  {
    id: 1,
    name: "Fresh Test Presentation 1",
    topic: "Artificial Intelligence in Healthcare",
    author: "Test Author",
    category: "fresh",
    description: "For delete tests",
    completedSteps: [],
    pendingSteps: ["research", "slides", "illustration", "compiled", "pptx"]
  },
  {
    id: 2,
    name: "Fresh Test Presentation 2",
    topic: "Sustainable Energy Solutions",
    author: "Test Author",
    category: "fresh",
    description: "For general fresh state tests",
    completedSteps: [],
    pendingSteps: ["research", "slides", "illustration", "compiled", "pptx"]
  },
  {
    id: 3,
    name: "Fresh Test Presentation 3",
    topic: "Modern Web Development",
    author: "Test Author",
    category: "fresh",
    description: "For delete tests (multiple)",
    completedSteps: [],
    pendingSteps: ["research", "slides", "illustration", "compiled", "pptx"]
  },
  {
    id: 4,
    name: "Fresh Test Presentation 4",
    topic: "Data Science Fundamentals",
    author: "Test Author",
    category: "fresh",
    description: "For delete tests (multiple)",
    completedSteps: [],
    pendingSteps: ["research", "slides", "illustration", "compiled", "pptx"]
  },

  // ========== Research Complete (5-8) ==========
  {
    id: 5,
    name: "Research Complete Test 1",
    topic: "Machine Learning Applications",
    author: "Test Author",
    category: "research_complete",
    description: "For slides generation tests",
    completedSteps: ["research"],
    pendingSteps: ["slides", "illustration", "compiled", "pptx"]
  },
  {
    id: 6,
    name: "Research Complete Test 2",
    topic: "Climate Change Impact",
    author: "Test Author",
    category: "research_complete",
    description: "For slides generation tests",
    completedSteps: ["research"],
    pendingSteps: ["slides", "illustration", "compiled", "pptx"]
  },
  {
    id: 7,
    name: "Research Complete Test 3",
    topic: "Blockchain Technology",
    author: "Test Author",
    category: "research_complete",
    description: "For slides display tests",
    completedSteps: ["research"],
    pendingSteps: ["slides", "illustration", "compiled", "pptx"]
  },
  {
    id: 8,
    name: "Research Complete Test 4",
    topic: "Quantum Computing",
    author: "Test Author",
    category: "research_complete",
    description: "For wizard tests",
    completedSteps: ["research"],
    pendingSteps: ["slides", "illustration", "compiled", "pptx"]
  },

  // ========== Slides Complete (9-10) ==========
  {
    id: 9,
    name: "Slides Complete Test 1",
    topic: "Digital Marketing Strategies",
    author: "Test Author",
    category: "slides_complete",
    description: "For illustration tests",
    completedSteps: ["research", "slides"],
    pendingSteps: ["illustration", "compiled", "pptx"]
  },
  {
    id: 10,
    name: "Slides Complete Test 2",
    topic: "Remote Work Best Practices",
    author: "Test Author",
    category: "slides_complete",
    description: "For markdown slide tests",
    completedSteps: ["research", "slides"],
    pendingSteps: ["illustration", "compiled", "pptx"]
  },

  // ========== Illustrations Complete (11-12) ==========
  {
    id: 11,
    name: "Illustrations Complete Test 1",
    topic: "Cybersecurity Fundamentals",
    author: "Test Author",
    category: "illustrations_complete",
    description: "For PPTX preview tests",
    completedSteps: ["research", "slides", "illustration"],
    pendingSteps: ["compiled", "pptx"]
  },
  {
    id: 12,
    name: "Illustrations Complete Test 2",
    topic: "Healthy Living Tips",
    author: "Test Author",
    category: "illustrations_complete",
    description: "For PPTX debug tests",
    completedSteps: ["research", "slides", "illustration"],
    pendingSteps: ["compiled", "pptx"]
  },

  // ========== Fully Complete (13-14) ==========
  {
    id: 13,
    name: "Complete Test Presentation 1",
    topic: "Project Management Best Practices",
    author: "Test Author",
    category: "complete",
    description: "For presentation steps tests",
    completedSteps: ["research", "slides", "illustration", "compiled", "pptx"],
    pendingSteps: []
  },
  {
    id: 14,
    name: "Complete Test Presentation 2",
    topic: "Future of Education",
    author: "Test Author",
    category: "complete",
    description: "For markdown rendering tests",
    completedSteps: ["research", "slides", "illustration", "compiled", "pptx"],
    pendingSteps: []
  },

  // ========== Manual Research (15) ==========
  {
    id: 15,
    name: "Manual Research Test 1",
    topic: "User Provided Content",
    author: "Test Author",
    category: "manual_research",
    description: "For manual research workflow tests",
    completedSteps: ["manual_research"],
    pendingSteps: ["slides", "illustration", "compiled", "pptx"]
  },

  // ========== Wizard Testing (16-20) ==========
  {
    id: 16,
    name: "Wizard Fresh Test",
    topic: "Space Exploration",
    author: "Test Author",
    category: "wizard_fresh",
    description: "For wizard general context tests",
    completedSteps: [],
    pendingSteps: ["research", "slides", "illustration", "compiled", "pptx"]
  },
  {
    id: 17,
    name: "Wizard Research Ready",
    topic: "Renewable Energy",
    author: "Test Author",
    category: "wizard_research",
    description: "For wizard research context tests",
    completedSteps: ["research"],
    pendingSteps: ["slides", "illustration", "compiled", "pptx"]
  },
  {
    id: 18,
    name: "Wizard Slides Ready",
    topic: "Mobile App Development",
    author: "Test Author",
    category: "wizard_slides",
    description: "For wizard slides context tests",
    completedSteps: ["research", "slides"],
    pendingSteps: ["illustration", "compiled", "pptx"]
  },
  {
    id: 19,
    name: "Wizard Complete Test",
    topic: "Digital Transformation",
    author: "Test Author",
    category: "wizard_complete",
    description: "For wizard improvements tests",
    completedSteps: ["research", "slides", "illustration", "compiled", "pptx"],
    pendingSteps: []
  },
  {
    id: 20,
    name: "Wizard Context Test",
    topic: "5G Technology",
    author: "Test Author",
    category: "wizard_context",
    description: "For basic wizard tests",
    completedSteps: ["research"],
    pendingSteps: ["slides", "illustration", "compiled", "pptx"]
  },

  // ========== Clarification Testing (21-23) ==========
  {
    id: 21,
    name: "Clarification Ready Test",
    topic: "Artificial Intelligence Ethics",
    author: "Test Author",
    category: "clarification_ready",
    description: "For research clarification tests",
    completedSteps: [],
    pendingSteps: ["research", "slides", "illustration", "compiled", "pptx"]
  },
  {
    id: 22,
    name: "Clarification AI Selected",
    topic: "Smart Cities",
    author: "Test Author",
    category: "clarification_ai",
    description: "For AI research clarification tests",
    completedSteps: [],
    pendingSteps: ["research", "slides", "illustration", "compiled", "pptx"],
    specialFlags: {
      aiResearchSelected: true
    }
  },
  {
    id: 23,
    name: "Clarification Manual Selected",
    topic: "Custom Research Topic",
    author: "Test Author",
    category: "clarification_manual",
    description: "For manual research clarification tests",
    completedSteps: [],
    pendingSteps: ["manual_research", "slides", "illustration", "compiled", "pptx"],
    specialFlags: {
      manualResearchSelected: true
    }
  },

  // ========== Step Status Testing (24-27) ==========
  {
    id: 24,
    name: "Step Pending Test",
    topic: "Robotics",
    author: "Test Author",
    category: "step_pending",
    description: "For step pending tests",
    completedSteps: [],
    pendingSteps: ["research", "slides", "illustration", "compiled", "pptx"]
  },
  {
    id: 25,
    name: "Step Running Test",
    topic: "Nanotechnology",
    author: "Test Author",
    category: "step_running",
    description: "For step running tests",
    completedSteps: [],
    pendingSteps: ["research", "slides", "illustration", "compiled", "pptx"],
    specialFlags: {
      isProcessing: true
    }
  },
  {
    id: 26,
    name: "Step Error Test",
    topic: "Virtual Reality",
    author: "Test Author",
    category: "step_error",
    description: "For step error tests",
    completedSteps: [],
    pendingSteps: ["research", "slides", "illustration", "compiled", "pptx"],
    specialFlags: {
      hasError: true
    }
  },
  {
    id: 27,
    name: "Step Mixed Status Test",
    topic: "Augmented Reality",
    author: "Test Author",
    category: "step_mixed",
    description: "For mixed step status tests",
    completedSteps: ["research"],
    pendingSteps: ["slides", "illustration", "compiled", "pptx"],
    specialFlags: {
      isProcessing: true,
      hasError: true
    }
  },

  // ========== Customization Testing (28-30) ==========
  {
    id: 28,
    name: "Slides Customization Test",
    topic: "Social Media Strategy",
    author: "Test Author",
    category: "customization_slides",
    description: "For slides customization tests",
    completedSteps: ["research", "slides"],
    pendingSteps: ["illustration", "compiled", "pptx"]
  },
  {
    id: 29,
    name: "PPTX Debug Test",
    topic: "Cloud Computing",
    author: "Test Author",
    category: "pptx_debug",
    description: "For PPTX generation debug tests",
    completedSteps: ["research", "slides", "illustration"],
    pendingSteps: ["compiled", "pptx"]
  },
  {
    id: 30,
    name: "Quick Test Presentation",
    topic: "Quick Testing",
    author: "Test Author",
    category: "quick_test",
    description: "For quick testing needs",
    completedSteps: ["research", "slides"],
    pendingSteps: ["illustration", "compiled", "pptx"]
  },

  // ========== Bug Fix Verification (31-35) ==========
  {
    id: 31,
    name: "Fix Verification Test 1",
    topic: "Edge Case Testing",
    author: "Test Author",
    category: "fix_edge_cases",
    description: "For testing edge cases with special characters",
    completedSteps: ["research"],
    pendingSteps: ["slides", "illustration", "compiled", "pptx"]
  },
  {
    id: 32,
    name: "Fix Verification Test 2",
    topic: "Empty Content Testing",
    author: "Test Author",
    category: "fix_empty_content",
    description: "For testing empty content handling",
    completedSteps: ["research"],
    pendingSteps: ["slides", "illustration", "compiled", "pptx"]
  },
  {
    id: 33,
    name: "Fix Verification Test 3",
    topic: "Markdown Edge Cases",
    author: "Test Author",
    category: "fix_markdown",
    description: "For testing markdown edge cases",
    completedSteps: ["research"],
    pendingSteps: ["slides", "illustration", "compiled", "pptx"]
  },
  {
    id: 34,
    name: "Research Apply Fix Test",
    topic: "Testing Research Updates",
    author: "Test Author",
    category: "fix_research_apply",
    description: "For testing research apply fix",
    completedSteps: ["research"],
    pendingSteps: ["slides", "illustration", "compiled", "pptx"]
  },
  {
    id: 35,
    name: "Navigation Fix Test",
    topic: "Step Navigation Testing",
    author: "Test Author",
    category: "fix_navigation",
    description: "For testing navigation fixes",
    completedSteps: ["research", "slides"],
    pendingSteps: ["illustration", "compiled", "pptx"]
  }
];

/**
 * Test-to-Presentation Mapping
 * Maps each E2E test file to the presentations it should use
 */
export const TEST_PRESENTATION_MAPPING = {
  // Tests using fresh presentations
  "delete-presentation.spec.ts": [1, 3, 4],
  "pagination.spec.ts": "all_fresh", // Uses all fresh presentations

  // Tests using research complete
  "slides-test-with-preseeded-data.spec.ts": [5, 6],
  "slides-display.spec.ts": [7],
  "research-content-display.spec.ts": [5, 6, 15], // Also uses manual research

  // Tests using slides complete
  "illustration-stream.spec.ts": [9],
  "markdown-slides.spec.ts": [10],
  "step-navigation-debug.spec.ts": [9],

  // Tests using illustrations complete
  "pptx-preview.spec.ts": [11],
  "pptx-quick-debug.spec.ts": [12, 29], // Also uses PPTX debug

  // Tests using fully complete
  "presentation-steps.spec.ts": [13],
  "markdown-rendering.spec.ts": [14],

  // Wizard tests
  "wizard-improvements-simple.spec.ts": [18], // Wizard Slides Ready
  "wizard-improvements.spec.ts": [19], // Wizard Complete
  "wizard-general-context.spec.ts": [16], // Wizard Fresh
  "wizard-research-context.spec.ts": [17], // Wizard Research Ready
  "wizard-slides-context.spec.ts": [18], // Wizard Slides Ready
  "wizard.spec.ts": [20], // Wizard Context Test

  // Clarification tests
  "research-clarification.spec.ts": [21, 22, 23],

  // Step status tests
  "step-pending-test.spec.ts": [24],
  "step-status-debug.spec.ts": [25, 26, 27],

  // Customization tests
  "slides-customization.spec.ts": [28],

  // Bug fix tests
  "test-fixes.spec.ts": [31, 32, 33],
  "test-research-apply-fix.spec.ts": [34],
  
  // Navigation tests
  "step-navigation-debug.spec.ts": [35],

  // Tests that should continue creating presentations
  "create-presentation.spec.ts": "creates_new",
  "wizard-slide-management.spec.ts": "creates_new",
  "wizard-research-apply-debug.spec.ts": "creates_new"
};

/**
 * Get test presentation by ID
 */
export function getTestPresentationById(id: number): TestPresentation | undefined {
  return TEST_PRESENTATIONS_V2.find(p => p.id === id);
}

/**
 * Get test presentations by category
 */
export function getTestPresentationsByCategory(category: string): TestPresentation[] {
  return TEST_PRESENTATIONS_V2.filter(p => p.category === category);
}

/**
 * Get presentations for a specific test file
 */
export function getPresentationsForTest(testFile: string): number[] | string {
  return TEST_PRESENTATION_MAPPING[testFile] || [];
}

/**
 * Navigate directly to a test presentation by ID
 */
export function getTestPresentationUrl(id: number, baseUrl: string = 'http://localhost:3001'): string {
  return `${baseUrl}/edit/${id}`;
}

/**
 * Test configuration
 */
export const TEST_CONFIG_V2 = {
  // API endpoints
  TEST_API_BASE_URL: "http://localhost:8001",
  PROD_API_BASE_URL: "http://localhost:8000",
  
  // Frontend URLs  
  TEST_FRONTEND_URL: "http://localhost:3001",
  PROD_FRONTEND_URL: "http://localhost:3000",
  
  // Database info
  TEST_DATABASE_FILE: "presentations_test.db",
  
  // Test settings
  DEFAULT_TIMEOUT: 30000,
  STEP_COMPLETION_TIMEOUT: 60000,
  
  // Offline mode settings
  OFFLINE_MODE: process.env.POWERIT_OFFLINE_E2E !== 'false',
  
  // Total number of preseeded presentations
  TOTAL_PRESENTATIONS: 35
};

/**
 * Quick navigation helper for tests
 */
export async function navigateToTestPresentationById(page: any, id: number) {
  const presentation = getTestPresentationById(id);
  if (!presentation) {
    throw new Error(`Test presentation with ID ${id} not found`);
  }
  
  const url = getTestPresentationUrl(id);
  await page.goto(url);
  
  // Wait for the edit page to load
  await page.waitForSelector('[data-testid="step-nav-research"]', { state: 'visible', timeout: 15000 });
  
  return presentation;
}