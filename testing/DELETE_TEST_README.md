# Delete Presentation Test

This test verifies the deletion functionality for presentations using pre-seeded test data.

## Test Overview

The delete-presentation.spec.ts test file contains two tests:
1. **Single deletion**: Deletes Fresh Test Presentation 1 (ID: 1)
2. **Multiple deletion**: Deletes Fresh Test Presentation 3 and 4 (IDs: 3, 4)

## Key Changes from Original

- ✅ Uses pre-seeded test presentations instead of creating new ones
- ✅ Uses only data-testid locators for element selection
- ✅ No hardcoded URLs (uses relative paths)
- ✅ Includes database reset before each test for isolation

## Running the Tests

### Option 1: Using the Test Script (Recommended)
```bash
cd testing
./run-delete-test.sh
```

### Option 2: Manual Setup

1. **Start test backend** (port 8001):
```bash
cd backend
POWERIT_ENV=test ./venv/bin/python run_api.py
```

2. **Start test frontend** (port 3001):
```bash
cd frontend
NEXT_PUBLIC_API_URL=http://localhost:8001 npm run dev -- -p 3001
```

3. **Run the test**:
```bash
cd testing
PLAYWRIGHT_BASE_URL=http://localhost:3001 npx playwright test e2e/delete-presentation.spec.ts
```

### Option 3: Using Make (if configured for test environment)
```bash
make test-e2e-specific test=delete-presentation
```

## Test Data

The tests use the following pre-seeded presentations:
- **Fresh Test Presentation 1** (ID: 1) - Used for single deletion test
- **Fresh Test Presentation 3** (ID: 3) - Used for multiple deletion test
- **Fresh Test Presentation 4** (ID: 4) - Used for multiple deletion test

## Database Reset

The test includes a `beforeEach` hook that resets the test database to ensure:
- All test presentations are available
- Tests are isolated from each other
- Consistent test results

## Troubleshooting

If tests fail with "presentation not found":
1. Ensure the test backend is running (not the production backend)
2. Check that the test database has been properly seeded
3. Verify the frontend is connecting to the test backend (port 8001)

If database reset fails:
1. Check that the `/test/reset-database` endpoint is available
2. Ensure the test backend has write permissions to the test database