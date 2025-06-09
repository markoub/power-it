/**
 * Test Configuration for E2E Tests
 * 
 * This file provides configuration and utilities for E2E tests that use
 * the prepared test database with pre-seeded presentations.
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
}

/**
 * Pre-seeded test presentations available in the test database
 */
export const TEST_PRESENTATIONS: TestPresentation[] = [
  // Fresh presentations (just created, no steps completed)
  {
    id: 1,
    name: "Fresh Test Presentation 1",
    topic: "Artificial Intelligence in Healthcare",
    author: "Test Author",
    category: "fresh",
    description: "For delete tests - single deletion",
    completedSteps: [],
    pendingSteps: ["research", "slides", "illustration", "compiled", "pptx"]
  },
  {
    id: 2,
    name: "Fresh Test Presentation 2", 
    topic: "Sustainable Energy Solutions",
    author: "Test Author",
    category: "fresh",
    description: "For create/delete tests",
    completedSteps: [],
    pendingSteps: ["research", "slides", "illustration", "compiled", "pptx"]
  },
  {
    id: 3,
    name: "Fresh Test Presentation 3",
    topic: "Modern Web Development",
    author: "Test Author",
    category: "fresh",
    description: "For navigation tests",
    completedSteps: [],
    pendingSteps: ["research", "slides", "illustration", "compiled", "pptx"]
  },
  {
    id: 4,
    name: "Fresh Test Presentation 4",
    topic: "Data Science Fundamentals",
    author: "Test Author",
    category: "fresh",
    description: "For workflow tests",
    completedSteps: [],
    pendingSteps: ["research", "slides", "illustration", "compiled", "pptx"]
  },
  
  // Research completed presentations
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
    description: "For step navigation tests",
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
  
  // Slides completed presentation
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
  
  // Illustrations completed presentation  
  {
    id: 10,
    name: "Illustrations Complete Test 1",
    topic: "Cybersecurity Fundamentals",
    author: "Test Author",
    category: "illustrations_complete",
    description: "For compiled/PPTX tests",
    completedSteps: ["research", "slides", "illustration"], 
    pendingSteps: ["compiled", "pptx"]
  },
  
  // Complete presentation
  {
    id: 11,
    name: "Illustrations Complete Test 1",
    topic: "Cybersecurity Fundamentals",
    author: "Test Author",
    category: "illustrations_complete",
    description: "For compiled/PPTX tests",
    completedSteps: ["research", "slides", "illustration"],
    pendingSteps: ["compiled", "pptx"]
  },
  
  // Fully complete presentation
  {
    id: 12,
    name: "Complete Test Presentation 1",
    topic: "Project Management Best Practices",
    author: "Test Author",
    category: "complete",
    description: "For wizard/editing tests",
    completedSteps: ["research", "slides", "illustration", "compiled", "pptx"],
    pendingSteps: []
  },
  
  // Manual research presentation
  {
    id: 13,
    name: "Manual Research Test 1", 
    topic: "User Provided Content",
    author: "Test Author",
    category: "manual_research",
    description: "For manual research workflow tests",
    completedSteps: ["manual_research"],
    pendingSteps: ["slides", "illustration", "compiled", "pptx"]
  },
  
  // Wizard testing presentations
  {
    id: 14,
    name: "Wizard Fresh Test",
    topic: "Space Exploration",
    author: "Test Author",
    category: "wizard_testing",
    description: "For wizard general context tests",
    completedSteps: [],
    pendingSteps: ["research", "slides", "illustration", "compiled", "pptx"]
  },
  {
    id: 15,
    name: "Wizard Research Ready",
    topic: "Renewable Energy",
    author: "Test Author",
    category: "wizard_testing",
    description: "For wizard research context tests",
    completedSteps: ["research"],
    pendingSteps: ["slides", "illustration", "compiled", "pptx"]
  },
  {
    id: 16,
    name: "Wizard Slides Ready",
    topic: "Mobile App Development",
    author: "Test Author",
    category: "wizard_testing",
    description: "For wizard slides context tests",
    completedSteps: ["research", "slides"],
    pendingSteps: ["illustration", "compiled", "pptx"]
  },
  {
    id: 17,
    name: "Wizard Complete Test",
    topic: "Digital Transformation",
    author: "Test Author",
    category: "wizard_testing",
    description: "For wizard improvements tests",
    completedSteps: ["research", "slides", "illustration", "compiled", "pptx"],
    pendingSteps: []
  },
  {
    id: 18,
    name: "Wizard Context Test",
    topic: "5G Technology",
    author: "Test Author",
    category: "wizard_testing",
    description: "For basic wizard tests",
    completedSteps: ["research"],
    pendingSteps: ["slides", "illustration", "compiled", "pptx"]
  },
  
  // Clarification testing presentations
  {
    id: 19,
    name: "Clarification Test ADK",
    topic: "Google ADK",
    author: "Test Author",
    category: "clarification_testing",
    description: "For testing clarification when topic has ambiguous acronym (ADK)",
    completedSteps: [],
    pendingSteps: ["research", "slides", "illustration", "compiled", "pptx"]
  },
  {
    id: 20,
    name: "Clarification Test Clear Topic",
    topic: "Machine Learning in Healthcare",
    author: "Test Author",
    category: "clarification_testing",
    description: "For testing when topic is clear and no clarification needed",
    completedSteps: [],
    pendingSteps: ["research", "slides", "illustration", "compiled", "pptx"]
  },
  {
    id: 21,
    name: "Clarification Test SDK",
    topic: "Google SDK",
    author: "Test Author",
    category: "clarification_testing",
    description: "For testing clarification when topic has ambiguous acronym (SDK)",
    completedSteps: [],
    pendingSteps: ["research", "slides", "illustration", "compiled", "pptx"]
  },
  
  // Step status testing presentations
  {
    id: 22,
    name: "Step Pending Test",
    topic: "Robotics",
    author: "Test Author",
    category: "step_status_testing",
    description: "For step pending tests - all steps pending",
    completedSteps: [],
    pendingSteps: ["research", "slides", "illustration", "compiled", "pptx"]
  },
  {
    id: 23,
    name: "Step Running Test",
    topic: "Nanotechnology",
    author: "Test Author",
    category: "step_status_testing",
    description: "For step running tests - research in progress",
    completedSteps: [],
    pendingSteps: ["research", "slides", "illustration", "compiled", "pptx"]
  },
  {
    id: 24,
    name: "Step Error Test",
    topic: "Virtual Reality",
    author: "Test Author",
    category: "step_status_testing",
    description: "For step error tests - research failed",
    completedSteps: [],
    pendingSteps: ["research", "slides", "illustration", "compiled", "pptx"]
  },
  {
    id: 25,
    name: "Step Mixed Status Test",
    topic: "Augmented Reality",
    author: "Test Author",
    category: "step_status_testing",
    description: "For mixed step status tests",
    completedSteps: ["research"],
    pendingSteps: ["slides", "illustration", "compiled", "pptx"]
  },
  
  // Customization testing presentations
  {
    id: 26,
    name: "Slide Customization Test",
    topic: "Business Strategy",
    author: "Test Author",
    category: "customization_testing",
    description: "For testing slide customization features",
    completedSteps: ["research", "slides"],
    pendingSteps: ["illustration", "compiled", "pptx"]
  },
  {
    id: 27,
    name: "PPTX Generation Test",
    topic: "Education Technology",
    author: "Test Author",
    category: "customization_testing",
    description: "For testing PPTX export features",
    completedSteps: ["research", "slides", "illustration", "compiled"],
    pendingSteps: ["pptx"]
  },
  {
    id: 28,
    name: "Template Styles Test",
    topic: "Design Systems",
    author: "Test Author",
    category: "customization_testing",
    description: "For testing different template styles",
    completedSteps: ["research", "slides"],
    pendingSteps: ["illustration", "compiled", "pptx"]
  },
  
  // Bug fix testing presentations
  {
    id: 29,
    name: "Empty Images Bug Test",
    topic: "Healthcare Innovation",
    author: "Test Author",
    category: "bug_fix_testing",
    description: "For testing empty images handling",
    completedSteps: ["research", "slides", "illustration"],
    pendingSteps: ["compiled", "pptx"]
  },
  {
    id: 30,
    name: "Special Characters Test",
    topic: "Fintech & Banking",
    author: "Test Author",
    category: "bug_fix_testing",
    description: "For testing special characters in content",
    completedSteps: ["research", "slides"],
    pendingSteps: ["illustration", "compiled", "pptx"]
  },
  {
    id: 31,
    name: "Long Content Test",
    topic: "Environmental Sustainability",
    author: "Test Author",
    category: "bug_fix_testing",
    description: "For testing long content handling",
    completedSteps: ["research"],
    pendingSteps: ["slides", "illustration", "compiled", "pptx"]
  },
  {
    id: 32,
    name: "Unicode Content Test",
    topic: "Global Languages",
    author: "Test Author",
    category: "bug_fix_testing",
    description: "For testing Unicode and multilingual content",
    completedSteps: ["research", "slides"],
    pendingSteps: ["illustration", "compiled", "pptx"]
  }
];

/**
 * Test configuration
 */
export const TEST_CONFIG = {
  // API endpoints
  TEST_API_BASE_URL: "http://localhost:8001",
  PROD_API_BASE_URL: "http://localhost:8000",
  
  // Frontend URLs  
  TEST_FRONTEND_URL: "http://localhost:3001",
  
  // Database info
  TEST_DATABASE_FILE: "presentations_test.db",
  
  // Test settings
  DEFAULT_TIMEOUT: 30000,
  STEP_COMPLETION_TIMEOUT: 60000,
  
  // Offline mode settings
  OFFLINE_MODE: process.env.POWERIT_OFFLINE_E2E !== 'false'
};

/**
 * Get API URL based on test configuration
 */
export function getApiUrl(): string {
  return TEST_CONFIG.TEST_API_BASE_URL;
}

/**
 * Get a test presentation by category
 */
export function getTestPresentation(category: string, index: number = 0): TestPresentation | undefined {
  const presentations = TEST_PRESENTATIONS.filter(p => p.category === category);
  return presentations[index];
}

/**
 * Get test presentations by category
 */
export function getTestPresentations(category: string): TestPresentation[] {
  return TEST_PRESENTATIONS.filter(p => p.category === category);
}

/**
 * Navigate to edit page for a test presentation
 */
export function getEditUrl(presentationId: number): string {
  return `${TEST_CONFIG.TEST_FRONTEND_URL}/edit/${presentationId}`;
}

/**
 * Get timeout value based on offline mode
 */
export function getTimeout(defaultTimeout: number = TEST_CONFIG.DEFAULT_TIMEOUT): number {
  return TEST_CONFIG.OFFLINE_MODE ? Math.min(defaultTimeout, 10000) : defaultTimeout;
}

/**
 * Check if we should use the test API or production API
 */
export function shouldUseTestBackend(): boolean {
  return process.env.E2E_USE_TEST_BACKEND === 'true';
}

/**
 * Available step types in the application
 */
export const STEP_TYPES = ['research', 'manual_research', 'slides', 'illustration', 'compiled', 'pptx'] as const;

export type StepType = typeof STEP_TYPES[number];

/**
 * Test data categories for different test scenarios
 */
export const TEST_CATEGORIES = {
  FRESH: 'fresh',                           // Just created, no steps completed
  RESEARCH_COMPLETE: 'research_complete',   // Research step completed
  SLIDES_COMPLETE: 'slides_complete',       // Research + slides completed  
  ILLUSTRATIONS_COMPLETE: 'illustrations_complete', // Research + slides + illustrations completed
  COMPLETE: 'complete',                     // All steps completed
  MANUAL_RESEARCH: 'manual_research',       // Manual research completed
  WIZARD_TESTING: 'wizard_testing',         // For wizard functionality tests
  CLARIFICATION_TESTING: 'clarification_testing', // For research clarification tests
  STEP_STATUS_TESTING: 'step_status_testing', // For testing different step statuses
  CUSTOMIZATION_TESTING: 'customization_testing', // For slide customization and PPTX tests
  BUG_FIX_TESTING: 'bug_fix_testing'        // For regression tests and edge cases
} as const;