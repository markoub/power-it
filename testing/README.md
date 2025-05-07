# Presentation Assistant E2E Tests

This directory contains end-to-end tests for the Presentation Assistant application using Playwright.

## Test Structure

- `e2e/` - Contains all end-to-end tests
  - `utils.ts` - Common testing utilities and helper functions
  - `presentations-list.spec.ts` - Tests for the presentations list page
  - `create-presentation.spec.ts` - Tests for creating a new presentation
  - `presentation-steps.spec.ts` - Tests for running presentation steps

## Prerequisites

Before running the tests, ensure:

1. The backend server is running on http://localhost:8000
2. The frontend server is running on http://localhost:3000
3. Playwright browsers are installed

## Running Tests

To run all tests:

```bash
# From the testing directory
npx playwright test
```

To run a specific test file:

```bash
npx playwright test e2e/presentations-list.spec.ts
```

To run tests with UI mode (recommended for debugging):

```bash
npx playwright test --ui
```

## Test with Specific Browser

By default, tests run on Chromium. To run on a specific browser:

```bash
npx playwright test --project=chromium
```

## Viewing Test Reports

After running tests, you can view the HTML report:

```bash
npx playwright show-report
```

## Notes

- Some tests may take several minutes to complete due to the nature of the presentation generation process
- The tests use data-testid attributes for robust element selection
- Failed tests will generate screenshots automatically 