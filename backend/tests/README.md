# PowerIt Backend Tests

This directory contains tests for the PowerIt backend functionality. The tests are organized by functionality and use Python's pytest framework.

## Test Organization

The tests are organized into the following directories:

- **unit/**: Unit tests for individual functions and classes
- **integration/**: Integration tests that test multiple components together
- **pptx/**: Tests for PowerPoint generation functionality
- **logo_fetcher/**: Tests for logo fetching functionality
- **fixtures/**: Contains test fixtures and mock data
- **test_data/**: Contains test data files used by the tests

## Running Tests

Use the run_tests.sh script to run the tests:

```bash
# Run all tests in replay mode (default)
./run_tests.sh

# Run specific tests
./run_tests.sh tests/logo_fetcher/test_logo_fetcher.py
./run_tests.sh tests/pptx
```

## Test Approach

The tests use a combination of:

1. **Unit tests**: Testing individual functions and classes in isolation
2. **Mock testing**: Using unittest.mock to replace external dependencies
3. **Integration tests**: Testing multiple components together
4. **Fixtures**: Using pre-defined test data and pytest fixtures

## VCR (Recording and Replaying API Calls)

For external API calls, we use pre-recorded responses to make tests:

1. **Fast**: Tests run faster without making actual API calls
2. **Reliable**: Tests don't depend on API availability 
3. **Free**: No API usage charges when running tests
4. **No credentials needed**: You don't need API keys to run tests

### Recording Mode

To record new API responses:

```bash
GEMINI_VCR_MODE=record OPENAI_VCR_MODE=record ./run_tests.sh
```

In recording mode, you need valid API keys set as environment variables.

### Replay Mode

Replay mode is the default mode, using stored responses instead of real API calls:

```bash
./run_tests.sh
```

## VCR Environment Variables

Each test type uses a specific environment variable to control record/replay mode:

| Test Type | Environment Variable | Default Value |
|-----------|----------------------|---------------|
| Gemini API | `GEMINI_VCR_MODE` | `replay` |
| OpenAI API | `OPENAI_VCR_MODE` | `replay` |
| Presentations | `PRESENTATION_VCR_MODE` | `replay` |
| TOC Font | `TOC_FONT_VCR_MODE` | `replay` |
| Template PPTX | `TEMPLATE_PPTX_VCR_MODE` | `replay` |
| Image API | `IMAGE_API_VCR_MODE` | `replay` |

Setting any of these to `record` will enable recording for that test type.

## Recording Specific Test Types

### Recording Gemini API Fixtures

```bash
export GEMINI_VCR_MODE=record
./run_tests.sh tests/test_slides.py
```

### Recording OpenAI API Fixtures

```bash
export OPENAI_VCR_MODE=record
./run_tests.sh tests/test_images.py
```

## Troubleshooting

### "Fixture not found" errors

Run the test in record mode with the appropriate environment variable.

### Missing test image

Ensure there's a test image at `tests/test_data/test_image.png` or in the root directory at `test_image.png`.

### API server connection errors

If you're recording API fixtures, make sure the API server is running.

## Adding New Tests

When adding new tests:

1. Place them in the appropriate directory based on functionality
2. Use the existing VCR fixtures for API calls
3. Ensure they work in both record and replay modes
4. Add any necessary test data to the test_data directory

For more information, see the [pytest documentation](https://docs.pytest.org/).

## Test Modes

The tests can run in two modes:

1. **Replay Mode** (Default): Uses pre-recorded API responses stored as fixtures
   - Fast, cost-free, and isolated from API availability
   - Tests will skip if required fixtures aren't available
   - This is the default when running `./run_tests.sh`

2. **Record Mode**: Makes real API calls and saves responses as fixtures
   - Requires valid API keys and internet connectivity
   - Will incur costs for Gemini and OpenAI API usage
   - Necessary when adding new tests or changing existing ones

## Running Tests

### Replay Mode (Default)

To run all tests using pre-recorded fixtures:

```bash
./run_tests.sh
```

### Offline Mode

By default the test runner sets `POWERIT_OFFLINE=1` so all external
calls to Gemini and OpenAI are mocked. If you want to run tests with
real network access, unset this variable and enable the appropriate
`*_VCR_MODE=record` flags.

To run a specific test:

```bash
./run_tests.sh tests/test_api.py
```

### Record Mode (Real API Calls)

To run tests with real API calls, use environment variables to control recording:

```bash
# Run a single test with real API calls
GEMINI_VCR_MODE=record ./run_tests.sh tests/test_slides.py

# Run all tests with real API calls
GEMINI_VCR_MODE=record OPENAI_VCR_MODE=record PRESENTATION_VCR_MODE=record ./run_tests.sh
```

Or use the convenience script for a specific test:

```bash
./record_tests.sh tests/test_slides.py
```

### Running All Tests with All Real API Calls

If you need to verify that everything works with actual APIs:

```bash
# Run all tests with all real API calls (will incur costs)
GEMINI_VCR_MODE=record OPENAI_VCR_MODE=record PRESENTATION_VCR_MODE=record \
TOC_FONT_VCR_MODE=record TEMPLATE_PPTX_VCR_MODE=record IMAGE_API_VCR_MODE=record \
./run_tests.sh
```

**Important:** Before using record mode, ensure you have:
- Valid API keys in your `.env` file or environment variables
- Sufficient API quota/budget
- For API integration tests: a running API server

## MCP Integration Tests

Some tests are marked with `@pytest.mark.skip` because they require a running MCP server. These tests are meant for manual verification and are not expected to run in CI.

## Test Data

The `test_data` directory contains resources like images and logos used by the tests. If a test is skipped due to missing resources, check this directory first.

## Clearing Fixtures

If you need to update fixtures, simply delete the relevant files in the `fixtures` directory and re-record them:

```bash
rm tests/fixtures/gemini_*.json
GEMINI_VCR_MODE=record ./run_tests.sh tests/test_slides.py
```

## Troubleshooting

### "Fixture not found" errors

Run the test in record mode with the appropriate environment variable.

### Missing test image

Ensure there's a test image at `tests/test_data/test_image.png` or in the root directory at `test_image.png`.

### API server connection errors

If you're recording API fixtures, make sure the API server is running. 