# E2E Tests Documentation

This document describes the approach used for E2E tests in the PowerIt application.

## Test Strategy

The E2E tests focus on testing the main user flows in the application with a robust approach that avoids unnecessary timeouts and ensures stability. 

### Test Principles

1. **Avoid fixed timeouts**: Tests are designed to use targeted expectations and assertions, rather than arbitrary waiting periods
2. **Graceful degradation**: Tests try to continue even if specific elements aren't found
3. **Focus on core functionality**: Tests ensure that primary user flows work as expected
4. **Resilience to UI changes**: Tests use reliable indicators like URLs and high-level page components

## Key Test Cases

1. **Presentation Creation**: Tests creating presentations using the AI method
2. **Presentation Workflow**: Tests navigating through the different steps of presentation editing
3. **Presentations List**: Tests viewing and interacting with existing presentations

## Known Limitations

1. **Manual Research Method**: Currently not tested due to some inconsistencies in the component structure
2. **Step Transitions**: The full workflow is not tested end-to-end but in more focused segments

## Best Practices for Writing Tests

1. **Use element selectors** with data-testid attributes whenever possible
2. **Check element visibility** before interacting with them
3. **Use URL checks** for verifying navigation instead of waiting for specific elements
4. **Avoid hard dependencies** on specific UI text or structure that might change
5. **Implement proper error handling** with descriptive messages

## Running Tests

```bash
# Run all E2E tests
make e2e

# Run E2E tests with browser visible
make e2e-headed

# Run specific test
make e2e-test test=presentations-list
```

## Debugging Tests

When tests fail, check:
1. Whether the expected elements exist with the correct data-testid
2. If the timeouts are sufficient for slower environments
3. If the navigation flow has changed in the application
4. If the form validation behavior has changed 