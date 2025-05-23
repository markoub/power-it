# API Documentation Tests

This folder contains Playwright tests that verify the backend API documentation.

The tests fetch `/docs` and `/api/openapi.json` from the running backend and ensure that every documented route responds.

Before running the tests, start the backend server locally:

```bash
cd backend
../backend/venv/bin/python run_api.py
```

Then execute the tests using the Playwright binary from the `testing` directory:

```bash
NODE_PATH=testing/node_modules npx playwright test tests/api
```

