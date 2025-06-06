# E2E Test Migration Guide

This guide shows which preseeded presentations each E2E test should use instead of creating new ones.

## Preseeded Test Data Categories

### 1. Fresh Presentations (IDs 1-4)
- **Purpose**: Testing creation flow, deletion, initial states
- **Tests to use these**:
  - `delete-presentation.spec.ts` - IDs 1, 3, 4
  - `pagination.spec.ts` - View all fresh presentations

### 2. Research Complete (IDs 5-8)
- **Purpose**: Testing slides generation from existing research
- **Tests to use these**:
  - `slides-test-with-preseeded-data.spec.ts` - IDs 5, 6
  - `slides-display.spec.ts` - ID 7
  - `research-content-display.spec.ts` - IDs 5, 6

### 3. Slides Complete (IDs 9-10)
- **Purpose**: Testing illustration generation, slide viewing
- **Tests to use these**:
  - `illustration-stream.spec.ts` - ID 9
  - `markdown-slides.spec.ts` - ID 10
  - `step-navigation-debug.spec.ts` - ID 9

### 4. Illustrations Complete (IDs 11-12)
- **Purpose**: Testing PPTX generation, compiled view
- **Tests to use these**:
  - `pptx-preview.spec.ts` - ID 11
  - `pptx-quick-debug.spec.ts` - ID 12

### 5. Fully Complete (IDs 13-14)
- **Purpose**: Testing complete presentations, editing
- **Tests to use these**:
  - `presentation-steps.spec.ts` - ID 13
  - `markdown-rendering.spec.ts` - ID 14

### 6. Manual Research (ID 15)
- **Purpose**: Testing manual research workflow
- **Tests to use these**:
  - `research-content-display.spec.ts` - ID 15

### 7. Wizard Testing (IDs 16-20)
- **Purpose**: Testing wizard context and improvements
- **Tests to use these**:
  - `wizard-improvements-simple.spec.ts` - ID 18 (Wizard Slides Ready)
  - `wizard-improvements.spec.ts` - ID 19 (Wizard Complete)
  - `wizard-general-context.spec.ts` - ID 16 (Wizard Fresh)
  - `wizard-research-context.spec.ts` - ID 17 (Wizard Research Ready)
  - `wizard-slides-context.spec.ts` - ID 18 (Wizard Slides Ready)
  - `wizard.spec.ts` - ID 20 (Wizard Context Test)

### 8. Clarification Testing (IDs 21-23)
- **Purpose**: Testing research clarification flow
- **Tests to use these**:
  - `research-clarification.spec.ts` - IDs 21, 22, 23

### 9. Step Status Testing (IDs 24-27)
- **Purpose**: Testing different step statuses
- **Tests to use these**:
  - `step-pending-test.spec.ts` - ID 24
  - `step-status-debug.spec.ts` - ID 25, 26, 27

### 10. Customization Testing (IDs 28-30)
- **Purpose**: Testing slide customization, PPTX debug
- **Tests to use these**:
  - `slides-customization.spec.ts` - ID 28
  - `pptx-quick-debug.spec.ts` - ID 29
  - Quick testing needs - ID 30

### 11. Bug Fix Verification (IDs 31-35)
- **Purpose**: Testing specific bug fixes and edge cases
- **Tests to use these**:
  - `test-fixes.spec.ts` - IDs 31, 32, 33
  - `test-research-apply-fix.spec.ts` - ID 34
  - Navigation fixes - ID 35

## Tests That SHOULD Create Presentations

These tests specifically test the creation flow and should continue using `createPresentation()`:

1. **create-presentation.spec.ts** - Tests the actual creation process
2. **wizard-slide-management.spec.ts** - Tests slide management after creation
3. **wizard-research-apply-debug.spec.ts** - Tests research application flow

## Migration Steps for Each Test

### Example Migration

**Before (Creating new presentation):**
```typescript
const name = `Test Presentation ${Date.now()}`;
const topic = 'Test Topic';
await createPresentation(page, name, topic);
```

**After (Using preseeded data):**
```typescript
const presentation = await navigateToTestPresentation(page, 'research_complete', 0);
// presentation.id = 5, presentation.name = "Research Complete Test 1"
```

### Quick Reference

| Test Category | Preseeded Category | Example ID |
|--------------|-------------------|------------|
| Need fresh presentation | 'fresh' | 1-4 |
| Need research done | 'research_complete' | 5-8 |
| Need slides done | 'slides_complete' | 9-10 |
| Need illustrations done | 'illustrations_complete' | 11-12 |
| Need everything done | 'complete' | 13-14 |
| Need manual research | 'manual_research' | 15 |
| Testing wizard | Use IDs 16-20 directly | 16-20 |
| Testing clarification | Use IDs 21-23 directly | 21-23 |
| Testing step status | Use IDs 24-27 directly | 24-27 |
| Testing customization | Use IDs 28-30 directly | 28-30 |
| Testing bug fixes | Use IDs 31-35 directly | 31-35 |

## Benefits of This Approach

1. **Faster Tests**: No waiting for AI generation
2. **Consistent Data**: Same test data every run
3. **Better Isolation**: Tests don't interfere with each other
4. **Reduced Costs**: No API calls during tests
5. **Easier Debugging**: Known data makes issues easier to trace

## Implementation Priority

1. **High Priority** (Tests that create many presentations):
   - wizard-general-context.spec.ts (creates 4)
   - wizard-slides-context.spec.ts (creates 4) 
   - test-fixes.spec.ts (creates 3)
   - wizard-improvements.spec.ts (creates 3)
   - research-clarification.spec.ts (creates 3)

2. **Medium Priority** (Tests that create 2 presentations):
   - research-context-wizard.spec.ts
   - wizard-research-context.spec.ts

3. **Low Priority** (Tests that create 1 presentation):
   - All other tests listed above

## Next Steps

1. Replace the current `init_test_db.py` with `init_test_db_v2.py`
2. Update each test file to use appropriate preseeded presentations
3. Remove unnecessary `createPresentation()` calls
4. Run all tests to verify they work with preseeded data
5. Update test documentation