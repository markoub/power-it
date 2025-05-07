# End-to-End (E2E) Tests for PowerIt

This folder contains end-to-end tests for the PowerIt application using Playwright. These tests verify the application's behavior from a user's perspective by automating browser interactions.

## Prerequisites

Before running the tests, ensure you have:

1. Node.js 16+ installed
2. The Playwright browsers installed: `npx playwright install`

## Setup

1. Install dependencies:
```bash
cd testing
npm install
```

2. Start the backend server (in a separate terminal):
```bash
cd backend
# Activate the virtual environment
source venv/bin/activate
# Start the backend server
uvicorn main:app --reload
```

3. Start the frontend server (in a separate terminal):
```bash
cd frontend
npm run dev
```

## Running Tests

### Run all tests:
```bash
npx playwright test
```

### Run a specific test file:
```bash
npx playwright test e2e/step-dependencies.spec.ts
```

### Run with headed browser (to see the browser UI):
```bash
npx playwright test --headed
```

### Run with longer timeout for slow servers:
```bash
npx playwright test --timeout=300000  # 5 minutes
```

### Debug a specific test:
```bash
npx playwright test e2e/step-dependencies.spec.ts --debug
```

### View test report:
```bash
npx playwright show-report
```

## Test Files

- `step-dependencies.spec.ts`: Tests step dependencies and disabled/enabled states
- `presentation-steps.spec.ts`: Tests the presentation step workflow
- `presentation-slides.spec.ts`: Tests slide generation and content
- `image-generation.spec.ts`: Tests image generation functionality
- `presentations-list.spec.ts`: Tests the presentations list page
- `create-presentation.spec.ts`: Tests creating new presentations
- `utils.ts`: Helper functions used across all tests

## Common Issues

1. **Tests timing out**: Ensure both frontend and backend servers are running. Increase the timeout if needed.

2. **Element not found**: If selectors have changed in the UI, update them in the test files.

3. **Authentication failures**: Make sure any required authentication is properly set up.

4. **Server errors**: Check the backend server logs for any errors.

## Best Practices

1. **Selectors**: Use data-testid attributes for selecting elements.

2. **Timeouts**: Use reasonable timeouts for operations that might take time.

3. **Isolation**: Each test should be independent and not rely on other tests.

4. **Cleanup**: Clean up any test data created during tests.

5. **Assertions**: Make clear assertions about what you expect to happen.

## Adding New Tests

1. Create a new file in the e2e folder with the naming convention `feature-name.spec.ts`

2. Use the existing test files as templates

3. Utilize helper functions from utils.ts

4. Add appropriate assertions

5. Run and verify your test works 