# E2E Test Migration Status

This file tracks the progress of migrating E2E tests to use preseeded database.

## Migration Progress

### ✅ Completed Tests
These tests have been migrated to use preseeded data:

- [x] `presentations-list.spec.ts` - Uses all presentations, handles pagination
- [x] `create-presentation.spec.ts` - Last test uses preseeded presentation ID 1
- [x] `slides-test-with-preseeded-data.spec.ts` - Uses research complete presentations (IDs 5, 6)
- [x] `research-content-display.spec.ts` - Uses research complete (5, 6) and manual research (12)
- [x] `illustration-stream.spec.ts` - Uses slides complete presentation (ID 9)
- [x] `delete-presentation.spec.ts` - Uses fresh presentations (IDs 1, 3, 4)
- [x] `step-navigation-debug.spec.ts` - Uses slides complete presentation (ID 9)

### 🔄 Partially Completed
These tests have been partially migrated but still have issues:

- [ ] `wizard-improvements-simple.spec.ts` - Uses preseeded data but has wizard interaction issues

### ❌ Not Yet Migrated
These tests still create presentations from scratch:

#### High Priority (Create 3+ presentations)
- [ ] `wizard-general-context.spec.ts` - Creates 4 presentations
- [ ] `wizard-slides-context.spec.ts` - Creates 4 presentations
- [ ] `test-fixes.spec.ts` - Creates 3 presentations
- [ ] `wizard-improvements.spec.ts` - Creates 3 presentations
- [ ] `research-clarification.spec.ts` - Creates 3 presentations
- [ ] `research-wizard-suggestions.spec.ts` - Creates 3 presentations

#### Medium Priority (Create 2 presentations)
- [ ] `research-context-wizard.spec.ts` - Creates 2 presentations
- [ ] `wizard-research-context.spec.ts` - Creates 2 presentations

#### Low Priority (Create 1 presentation)
- [ ] `pptx-quick-debug.spec.ts` - Creates 1 presentation
- [ ] `slides-customization.spec.ts` - Creates 1 presentation
- [ ] `step-pending-test.spec.ts` - Creates 1 presentation
- [ ] `step-status-debug.spec.ts` - Creates 1 presentation
- [ ] `test-research-apply-fix.spec.ts` - Creates 1 presentation
- [ ] `wizard-research-apply-debug.spec.ts` - Creates 1 presentation
- [ ] `wizard-slide-management.spec.ts` - Creates 1 presentation
- [ ] `wizard.spec.ts` - Creates 1 presentation

#### Tests that don't create presentations
- [ ] `api-docs.spec.ts` - Tests API documentation
- [ ] `debug-research-page.spec.ts` - Debug test
- [ ] `markdown-rendering.spec.ts` - Currently uses createPresentation, should use preseeded
- [ ] `markdown-slides.spec.ts` - Currently uses createPresentation, should use preseeded
- [ ] `pagination.spec.ts` - Tests pagination (might need adjustment for 12+ presentations)
- [ ] `pptx-preview.spec.ts` - Currently uses createPresentation, should use preseeded
- [ ] `presentation-steps.spec.ts` - Currently uses createPresentation, should use preseeded
- [ ] `slides-display.spec.ts` - Currently uses createPresentation, should use preseeded

## Database Seeding Status

### ✅ Implemented Categories
- [x] Fresh Presentations (IDs 1-4) - `test_data/fresh_presentations.py`
- [x] Research Complete (IDs 5-8) - `test_data/research_complete.py`
- [x] Slides Complete (IDs 9-10) - `test_data/slides_complete.py`
- [x] Illustrations Complete (ID 11) - `test_data/illustrations_complete.py`
- [x] Fully Complete (ID 12) - `test_data/fully_complete.py`
- [x] Manual Research (ID 13) - `test_data/manual_research.py`
- [x] Wizard Testing (IDs 14-18) - `test_data/wizard_testing.py`
- [x] Clarification Testing (IDs 19-21) - `test_data/clarification_testing.py`
- [x] Step Status Testing (IDs 22-25) - `test_data/step_status_testing.py`
- [x] Customization Testing (IDs 26-28) - `test_data/customization_testing.py`
- [x] Bug Fix Testing (IDs 29-32) - `test_data/bug_fix_testing.py`

### 🔄 Database Structure Updates
- [x] Created modular test_data directory structure
- [x] Updated init_test_db.py to use modular imports
- [x] Implemented all test data categories (32 presentations total)
- [ ] Need to test database initialization with new structure

## Next Steps

1. Test database initialization with new modular structure
2. Update test configuration to remove version numbers (v1, v2, etc.)
3. Migrate high-priority tests first (those creating 3+ presentations)
4. Run migrated tests to verify they work correctly
5. Update this status file as tests are migrated

## Notes

- Total presentations in database: 32 (covering all test scenarios)
- Tests should use `navigateToTestPresentation` or direct navigation to `/edit/{id}`
- Only tests that specifically test creation flow should use `createPresentation`
- Database is reset before test runs using `reset_test_db.py`
- All test data is organized in modular files under `backend/test_data/`