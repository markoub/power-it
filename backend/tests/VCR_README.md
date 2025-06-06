# VCR Test Recording Guide

This guide explains how to record and use VCR (Video Cassette Recorder) fixtures for API tests in the PowerIt backend.

## Overview

VCR allows us to record real API responses and replay them during tests, ensuring:
- Fast test execution (no real API calls)
- Consistent test results
- No API rate limit issues
- No API costs during regular test runs

## Recording New Fixtures

### 1. Prerequisites

Before recording, ensure you have:
- Valid API keys in your `.env` file:
  ```bash
  GEMINI_API_KEY=your_actual_key
  OPENAI_API_KEY=your_actual_key
  ```
- Active internet connection
- Sufficient API credits/quota

### 2. Recording Commands

To record VCR fixtures for specific test files:

```bash
# Record modify API calls
./record_tests.sh tests/unit/test_modify_vcr.py

# Record wizard API calls
./record_tests.sh tests/unit/test_wizard_vcr.py

# Record Gemini image API calls
./record_tests.sh tests/unit/test_gemini_images_vcr.py

# Record all image provider API calls
./record_tests.sh tests/unit/test_image_providers_vcr.py

# Record multiple test files at once
./record_tests.sh tests/unit/test_modify_vcr.py tests/unit/test_wizard_vcr.py
```

### 3. What Gets Recorded

The VCR tests record:
- **Gemini API calls**: Research, slides, modify, and wizard interactions
- **OpenAI API calls**: Image generation
- **Gemini Image API calls**: Image generation (if available)

Fixtures are saved in `tests/fixtures/` with descriptive names.

## Test Coverage

### API Call Types with VCR Tests

1. **Modify Operations** (`test_modify_vcr.py`)
   - `modify_presentation`: Full presentation modifications
   - `modify_single_slide`: Single slide modifications
   - Adding new slides

2. **Wizard Interactions** (`test_wizard_vcr.py`)
   - General wizard: General presentation advice
   - Research wizard: Research content modifications
   - Slides wizard: Slide structure modifications
   - Wizard suggestions

3. **Image Generation** (`test_image_providers_vcr.py`)
   - OpenAI image generation
   - Batch image generation for slides
   - Error handling scenarios

4. **Gemini Images** (`test_gemini_images_vcr.py`)
   - Single image generation
   - Multiple images for slides
   - Fallback handling

## Using Recorded Fixtures

### Running Tests with Fixtures

By default, tests run in replay mode using recorded fixtures:

```bash
# Run all tests with fixtures
./run_tests.sh

# Run specific tests with fixtures
./venv/bin/pytest tests/unit/test_modify_vcr.py -v

# Run offline tests only
make test-backend-offline
```

### Test Markers

Tests are marked with `@pytest.mark.vcr_record` to indicate they record VCR fixtures:

```python
@pytest.mark.asyncio
@pytest.mark.vcr_record
async def test_modify_presentation_vcr(self):
    # Test that records API calls
    pass
```

## Maintenance

### When to Re-record Fixtures

Re-record fixtures when:
- API response format changes
- New API features are added
- Test inputs significantly change
- Fixtures become outdated (> 6 months old)

### Updating Fixtures

1. Delete old fixture files:
   ```bash
   rm tests/fixtures/modify_*.json
   ```

2. Re-record:
   ```bash
   ./record_tests.sh tests/unit/test_modify_vcr.py
   ```

3. Commit new fixtures to version control

## Troubleshooting

### Common Issues

1. **"Fixture not found" errors**
   - Run the recording script to create fixtures
   - Check fixture file names match test expectations

2. **API key errors during recording**
   - Ensure `.env` file has valid keys
   - Check environment variables are loaded

3. **Different responses than expected**
   - API may have changed - re-record fixtures
   - Check if prompt/input has changed

### Debug Mode

To see detailed VCR activity:
```bash
export VCR_DEBUG=1
./run_tests.sh tests/unit/test_modify_vcr.py -v
```

## Best Practices

1. **Keep fixtures small**: Use minimal test data to reduce fixture size
2. **Use descriptive names**: Fixture names should indicate their purpose
3. **Document changes**: When updating fixtures, note why in commit messages
4. **Regular updates**: Review and update fixtures periodically
5. **Sensitive data**: Never commit fixtures with real sensitive data

## Adding New VCR Tests

To add VCR tests for new API calls:

1. Create a new test file: `test_[feature]_vcr.py`
2. Mark tests with `@pytest.mark.vcr_record`
3. Use appropriate fixtures and assertions
4. Run recording script to create fixtures
5. Verify tests pass in replay mode
6. Commit both test and fixture files