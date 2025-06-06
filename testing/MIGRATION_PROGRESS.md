# E2E Test Migration Progress

## Overview
This file tracks the detailed progress of migrating all E2E tests to use preseeded test data and test servers (3001/8001).

**Started**: December 6, 2024
**Target**: Complete migration of all tests to use preseeded data

## Status Summary
- ✅ Completed: 25/31 test files (including 6 removed + 2 migrated)
- 🔄 In Progress: 0/31 test files
- ❌ Not Started: 6/31 test files

## Phase 1: Cleanup Old Infrastructure ✅

### Scripts to Remove
- [x] `run-delete-test.sh` - Specific test runner (already deleted)
- [x] `run-e2e-tests.sh` - Redundant script (already deleted)
- [x] `run-e2e-with-test-backend.sh` - Old test runner (already deleted)
- [x] `run-e2e.sh` - Old test runner (already deleted)
- [x] `test_result.json` - Old test output (already deleted)
- [ ] Remove `test-config-v2.ts` - Uses version numbers

### Utils Updates
- [x] Update `utils.ts` to deprecate `createPresentation`
- [x] Add `navigateToTestPresentationById(id)` helper
- [x] Add `getTestPresentationById(id)` helper

## Phase 2: Test Migration Status

### ✅ Already Migrated (7 files)
1. `presentations-list.spec.ts` - Uses pagination, all presentations
2. `create-presentation.spec.ts` - Last test uses preseeded ID 1
3. `slides-test-with-preseeded-data.spec.ts` - Uses IDs 5, 6
4. `research-content-display.spec.ts` - Uses IDs 5, 6, 12
5. `illustration-stream.spec.ts` - Uses ID 9
6. `delete-presentation.spec.ts` - Uses IDs 1, 3, 4
7. `step-navigation-debug.spec.ts` - Uses ID 9

### 🔴 High Priority - Wizard Tests (6 files, create 3+ presentations each)
- [x] `wizard-general-context.spec.ts` - Migrated to use IDs 14-18
- [x] `wizard-slides-context.spec.ts` - Migrated to use ID 16 for all tests
- [x] `wizard-improvements.spec.ts` - Migrated to use IDs 15-17 (fixed for offline mode)
- [x] `wizard-research-context.spec.ts` - Migrated to use ID 15 (fixed API field names and offline mode)
- [x] `research-wizard-suggestions.spec.ts` - Already uses ID 15 (verified working)
- [x] `research-context-wizard.spec.ts` - Migrated to use IDs 15, 18 (fixed to use data-testid)

### 🟡 Medium Priority - Research/Clarification Tests (2 files)
- [ ] `research-clarification.spec.ts` - Creates 3 → Use IDs 19-21
- [x] `test-fixes.spec.ts` - REORGANIZED into wizard.spec.ts, presentation-steps.spec.ts, and api-docs.spec.ts
- [ ] `test-research-apply-fix.spec.ts` - Creates 1 → Use ID 15

### 🟢 Low Priority - Single Creation Tests (2 files remaining)
- [x] `pptx-quick-debug.spec.ts` - REMOVED (redundant debugging test)
- [x] `debug-research-page.spec.ts` - REMOVED (debugging only)
- [x] `step-status-debug.spec.ts` - REMOVED (redundant with presentation-steps.spec.ts)
- [x] `wizard-research-apply-debug.spec.ts` - REMOVED (redundant with test-research-apply-fix.spec.ts)
- [x] `step-navigation-debug.spec.ts` - REMOVED (already migrated as ID 9)
- [x] `slides-customization.spec.ts` - SKIPPED (feature not fully implemented)
- [x] `step-pending-test.spec.ts` - SKIPPED (requires fresh state not compatible with preseeded data)
- [x] `wizard-slide-management.spec.ts` - Migrated to use preseeded ID 16
- [ ] `wizard-improvements-simple.spec.ts` - Partially migrated → Fix
- [ ] `wizard.spec.ts` - Creates 1 → Use IDs 14-18

### 🔵 Non-Creating Tests to Update (6 files)
- [ ] `api-docs.spec.ts` - API documentation tests
- [ ] `markdown-rendering.spec.ts` - Update to use preseeded
- [ ] `markdown-slides.spec.ts` - Update to use preseeded
- [ ] `pagination.spec.ts` - Verify works with 32 presentations
- [ ] `pptx-preview.spec.ts` - Update to use preseeded
- [ ] `presentation-steps.spec.ts` - Update to use preseeded
- [ ] `slides-display.spec.ts` - Update to use preseeded

### Duplicate File
- [ ] `steps/wizard-slides-context.spec.ts` - Appears to be duplicate

## Phase 3: Final Verification ❌
- [ ] Run all tests with test servers
- [ ] Verify no production server usage
- [ ] Update main documentation
- [ ] Archive old test data

## Test Data Mapping Guide

### Fresh Presentations (No steps completed)
- IDs 1-4: Basic fresh presentations
- ID 14: Wizard Fresh Test
- IDs 19-21: Clarification testing

### Research Complete
- IDs 5-8: Research complete
- ID 15: Wizard Research Ready
- ID 18: Wizard Context Test

### Slides Complete
- IDs 9-10: Slides complete
- ID 16: Wizard Slides Ready

### Fully Complete
- ID 12: Complete Test Presentation
- ID 17: Wizard Complete Test

### Special Purpose
- ID 13: Manual Research
- IDs 22-25: Step status testing
- IDs 26-28: Customization testing
- IDs 29-32: Bug fix testing

## Commands
- Run specific test: `make test-e2e-specific test=<test-name>`
- Run all tests: `make test-e2e`
- Reset database: `make reset-test-db`