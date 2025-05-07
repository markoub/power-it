# E2E Testing Changelog

## 2025-05-07: Step Dependencies and Loading States Improvements

### New Features
- Added `step-dependencies.spec.ts` test to verify step dependencies and disabled/enabled states
- Added testing for tooltips that appear on disabled steps
- Added testing for consistent loading states across steps
- Added test for manual research step as an alternative to AI research

### Improvements
- Updated `utils.ts` with improved helper functions:
  - New `StepType` type to support all step types consistently
  - Improved `getStepStatus` function to work with the updated UI
  - Added `isStepEnabled` function to check disabled/enabled state of steps
  - Added `getStepDisabledTooltip` function to verify tooltip content
  - Added `verifyStepDependencies` function to check logical dependencies
  - Enhanced error handling in `createPresentation` function
  
- Updated `presentation-steps.spec.ts` to:
  - Use new helper functions
  - Work with the updated UI structure (sidebar navigation instead of cards)
  - Test the step sequence with correct dependencies

- Updated `presentation-slides.spec.ts` to work with the new UI and test slide generation

### Documentation
- Added comprehensive `README-e2e.md` with:
  - Setup instructions
  - Running tests commands
  - Common issues and solutions
  - Best practices
  - Guide for adding new tests

### Technical Changes
- Added longer timeouts for long-running processes
- Added checks to skip tests if servers aren't running
- Improved error handling and logging
- Made tests more robust against UI changes
- Added proper cleanup of test resources 