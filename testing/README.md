# PowerIt Testing

This directory contains the e2e tests for the PowerIt application using Playwright.

## Prerequisites

Before running e2e tests, ensure that both servers are running:

1. **Frontend Server**: `http://localhost:3000`
2. **Backend Server**: `http://localhost:8000`

## Running E2E Tests

### Quick Start (Recommended)

Use the run script for the best experience:

```bash
# Run with offline mode (default - faster and more reliable)
./run-e2e.sh

# Run with online mode (actual API calls - slower)
POWERIT_OFFLINE_E2E=false ./run-e2e.sh

# Run specific tests
./run-e2e.sh research-content-display.spec.ts

# Run with headed browser (for debugging)
./run-e2e.sh --headed
```

### Manual Execution

You can also run tests directly with npx:

```bash
# Default offline mode
npx playwright test

# Force online mode
POWERIT_OFFLINE_E2E=false npx playwright test

# Run specific test file
npx playwright test research-content-display.spec.ts
```

## Offline vs Online Mode

### Offline Mode (Default)
- **Fast**: Tests run quickly using mock API responses
- **Reliable**: No dependency on external APIs or internet connection
- **Free**: No API usage charges
- **No Credentials**: No need for API keys

### Online Mode 
- **Realistic**: Uses actual API calls
- **Slow**: Takes longer due to real API response times
- **Requires**: Valid API keys (GEMINI_API_KEY, OPENAI_API_KEY)
- **Costs**: May incur API usage charges

## Configuration

The test setup automatically configures the backend for offline/online mode through the `/health/config` endpoint.

Environment variables:
- `POWERIT_OFFLINE_E2E`: Set to `false` to enable online mode (default is offline)

## Test Structure

- `research-content-display.spec.ts`: Tests for AI and manual research content display
- `create-presentation.spec.ts`: Tests for presentation creation flow
- `presentations-list.spec.ts`: Tests for presentation listing and management
- `wizard.spec.ts`: Tests for the presentation wizard
- `wizard-research-context.spec.ts`: Tests for research context display in wizard
- `wizard-improvements.spec.ts`: Tests for wizard improvement suggestions
- `test-research-apply-fix.spec.ts`: Tests for wizard research apply functionality
- And more...

## Debugging Failed Tests

1. **View Test Report**: `npx playwright show-report`
2. **Screenshots**: Failed tests automatically capture screenshots
3. **Videos**: Test videos are recorded on failure
4. **Console Logs**: Check browser console output in test results

## Troubleshooting

### Backend Not Available
If you see "Backend not available" during test setup:
1. Make sure the backend server is running on `http://localhost:8000`
2. Check backend logs for any startup errors

### Tests Taking Too Long
If tests are running slowly:
1. Ensure you're using offline mode (default)
2. Check if `POWERIT_OFFLINE_E2E=false` is set somewhere

### API Key Errors (Online Mode Only)
If running in online mode without API keys:
1. Set `GEMINI_API_KEY` environment variable
2. Set `OPENAI_API_KEY` environment variable
3. Or switch back to offline mode for testing

## Recent Test Additions

### Wizard Research Apply Test (May 31, 2025)
Added `test-research-apply-fix.spec.ts` to verify that wizard research modifications are properly applied:

```bash
# Run this specific test
npx playwright test test-research-apply-fix.spec.ts

# Or with offline mode disabled to test with real APIs
POWERIT_OFFLINE=0 npx playwright test test-research-apply-fix.spec.ts
```

This test verifies:
1. User can navigate to research step
2. User can request research modifications via wizard
3. Wizard generates appropriate suggestions
4. Clicking "Apply" actually updates the research content
5. The suggestion is properly dismissed after applying 