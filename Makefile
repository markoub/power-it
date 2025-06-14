# Makefile for PowerIt project
# Contains commands for running tests and other common tasks

# Variables
SHELL := /bin/bash
TESTING_DIR := testing
BACKEND_DIR := backend
FRONTEND_DIR := frontend
E2E_DIR := $(TESTING_DIR)/e2e

# Test environment variables
TEST_BACKEND_PORT := 8001
TEST_FRONTEND_PORT := 3001
PROD_BACKEND_PORT := 8000
PROD_FRONTEND_PORT := 3000

# Color outputs (using printf for better compatibility)
define print_info
	@printf "\033[1;32m%s\033[0m\n" "$(1)"
endef

define print_warn
	@printf "\033[1;33m%s\033[0m\n" "$(1)"
endef

define print_section
	@printf "\033[1;36m\n=== %s ===\033[0m\n" "$(1)"
endef

.PHONY: help setup run clean
.PHONY: test-backend test-backend-online test-backend-offline test-backend-unit test-backend-integration
.PHONY: test-frontend test-e2e test-e2e-headed test-e2e-debug test-e2e-api test-e2e-specific test-e2e-list
.PHONY: test-all test-all-online test-all-offline test-all-failures
.PHONY: install-deps install-browsers dev reset-test-db

# Default target when just running `make`
help:
	$(call print_section,PowerIt Project Commands)
	@printf "\033[1;32mApplication Management:\033[0m\n"
	@printf "  \033[1;33mmake run\033[0m              - Run the complete application (backend + frontend)\n"
	@printf "  \033[1;33mmake dev\033[0m              - Run in development mode with hot reload\n"
	@printf "  \033[1;33mmake setup\033[0m            - Install all dependencies\n"
	@printf "  \033[1;33mmake clean\033[0m            - Clean build artifacts and cache\n"
	@printf "\n"
	@printf "\033[1;32mTesting - Backend:\033[0m\n"
	@printf "  \033[1;33mmake test-backend\033[0m         - Run all backend tests (offline by default)\n"
	@printf "  \033[1;33mmake test-backend-online\033[0m  - Run backend tests with network access\n"
	@printf "  \033[1;33mmake test-backend-offline\033[0m - Run backend tests without network access\n"
	@printf "  \033[1;33mmake test-backend-unit\033[0m    - Run only unit tests\n"
	@printf "  \033[1;33mmake test-backend-integration\033[0m - Run only integration tests\n"
	@printf "\n"
	@printf "\033[1;32mTesting - Frontend:\033[0m\n"
	@printf "  \033[1;33mmake test-frontend\033[0m        - Run frontend tests (E2E tests)\n"
	@printf "\n"
	@printf "\033[1;32mTesting - E2E:\033[0m (Uses test servers on ports 3001/8001)\n"
	@printf "  \033[1;33mmake test-e2e\033[0m            - Run all E2E tests with test database\n"
	@printf "  \033[1;33mmake test-e2e-headed\033[0m     - Run E2E tests with browser visible\n"
	@printf "  \033[1;33mmake test-e2e-debug\033[0m      - Run E2E tests with debugging enabled\n"
	@printf "  \033[1;33mmake test-e2e-api\033[0m        - Run API documentation tests\n"
	@printf "  \033[1;33mmake test-e2e-specific\033[0m test=file-name - Run specific E2E test\n"
	@printf "  \033[1;33mmake test-e2e-list\033[0m       - List all available E2E tests\n"
	@printf "  \033[1;33mmake reset-test-db\033[0m        - Reset the test database to initial seeded state\n"
	@printf "\n"
	@printf "\033[1;32mTesting - All:\033[0m\n"
	@printf "  \033[1;33mmake test-all\033[0m            - Run all tests (backend + frontend + e2e)\n"
	@printf "  \033[1;33mmake test-all-online\033[0m     - Run all tests with network access\n"
	@printf "  \033[1;33mmake test-all-offline\033[0m    - Run all tests without network access\n"
	@printf "  \033[1;33mmake test-all-failures\033[0m   - Run all tests and show only failures summary\n"
	@printf "\n"
	@printf "\033[1;32mDevelopment Tools:\033[0m\n"
	@printf "  \033[1;33mmake install-deps\033[0m        - Install project dependencies\n"
	@printf "  \033[1;33mmake install-browsers\033[0m    - Install Playwright browsers\n"
	@printf "  \033[1;33mmake install-browser-deps\033[0m - Install system dependencies for Playwright (Linux only)\n"
	@printf "\n"
	@printf "\033[1;32mExamples:\033[0m\n"
	@printf "  \033[1;33mmake test-backend-offline\033[0m\n"
	@printf "  \033[1;33mmake test-e2e-api\033[0m\n"
	@printf "  \033[1;33mmake test-e2e-specific test=presentations-list\033[0m\n"
	@printf "  \033[1;33mmake test-all-online\033[0m\n"

# ==========================================
# Application Management
# ==========================================

# Run the application
run:
	$(call print_info,Starting the application...)
	@chmod +x run.sh && ./run.sh
	$(call print_info,Application has been stopped.)

# Development mode
dev:
	$(call print_info,Starting development mode...)
	@echo "Starting backend and frontend in development mode..."
	# Add development-specific commands here

# Setup all dependencies
setup: install-deps install-browsers
	$(call print_info,Complete setup finished!)

# Clean build artifacts and cache
clean:
	$(call print_info,Cleaning build artifacts and cache...)
	@rm -rf $(FRONTEND_DIR)/.next
	@rm -rf $(FRONTEND_DIR)/node_modules/.cache
	@rm -rf $(BACKEND_DIR)/.pytest_cache
	@rm -rf $(TESTING_DIR)/.pytest_cache
	@rm -rf $(TESTING_DIR)/test-results
	@rm -rf $(TESTING_DIR)/playwright-report
	$(call print_info,Clean complete.)

# ==========================================
# Backend Testing
# ==========================================

# Run all backend tests (offline by default for speed)
test-backend: test-backend-offline

# Run backend tests with network access (for integration tests that need external APIs)
test-backend-online:
	$(call print_info,Running backend tests with network access...)
	@cd $(BACKEND_DIR) && chmod +x run_tests.sh && PYTEST_ARGS="--tb=short -v" ./run_tests.sh
	$(call print_info,Backend online tests complete.)

# Run backend tests without network access (faster, isolated)
test-backend-offline:
	$(call print_info,Running backend tests without network access...)
	@cd $(BACKEND_DIR) && chmod +x run_tests.sh && PYTEST_ARGS="--tb=short -v -m 'not network'" ./run_tests.sh
	$(call print_info,Backend offline tests complete.)

# Run only unit tests
test-backend-unit:
	$(call print_info,Running backend unit tests...)
	@cd $(BACKEND_DIR) && chmod +x run_tests.sh && PYTEST_ARGS="--tb=short -v -m unit" ./run_tests.sh
	$(call print_info,Backend unit tests complete.)

# Run only integration tests
test-backend-integration:
	$(call print_info,Running backend integration tests...)
	@cd $(BACKEND_DIR) && chmod +x run_tests.sh && PYTEST_ARGS="--tb=short -v -m integration" ./run_tests.sh
	$(call print_info,Backend integration tests complete.)

# ==========================================
# Frontend Testing
# ==========================================

# Run frontend tests (which are the E2E tests)
test-frontend:
	$(call print_info,Running frontend tests (E2E)...)
	@cd $(TESTING_DIR) && npx playwright test
	$(call print_info,Frontend tests complete.)

# ==========================================
# E2E Testing (Using Test Servers on 3001/8001)
# ==========================================

# Run all E2E tests (now defaults to using test servers)
test-e2e:
	$(call print_info,Running all E2E tests on test servers $(TEST_FRONTEND_PORT)/$(TEST_BACKEND_PORT)...)
	@cd $(TESTING_DIR) && chmod +x test.sh && ./test.sh
	$(call print_info,E2E tests complete.)

# Run all E2E tests with browser visible
test-e2e-headed:
	$(call print_info,Running all E2E tests with browser visible...)
	@cd $(TESTING_DIR) && chmod +x test.sh && ./test.sh --headed
	$(call print_info,E2E headed tests complete.)

# Run E2E tests with debugging enabled
test-e2e-debug:
	$(call print_info,Running E2E tests with debugging enabled...)
	@cd $(TESTING_DIR) && chmod +x test.sh && ./test.sh --headed --debug --timeout 60000
	$(call print_info,E2E debug tests complete.)

# Run API documentation tests
test-e2e-api:
	$(call print_info,Running API documentation tests...)
	cd $(TESTING_DIR) && npx playwright test api --config api/playwright.config.ts
	$(call print_info,API tests complete. See results above.)

# Run specific E2E tests
test-e2e-specific:
	@if [ -z "$(test)" ]; then \
		$(call print_warn,Error: No test specified. Usage: make test-e2e-specific test=test-name); \
		exit 1; \
	fi
	$(call print_info,Running E2E test: $(test)...)
	@cd $(TESTING_DIR) && chmod +x test.sh && ./test.sh e2e/$(test).spec.ts
	$(call print_info,E2E test complete.)

# List all available E2E tests
test-e2e-list:
	$(call print_info,Available E2E tests:)
	@find $(E2E_DIR) -name "*.spec.ts" | sed 's|$(E2E_DIR)/||g' | sed 's|\.spec\.ts$$||g' | sort

# Run E2E tests in batches to avoid timeouts
test-e2e-batch1:
	$(call print_info,Running E2E Batch 1: Core functionality tests...)
	@cd $(TESTING_DIR) && chmod +x test.sh && ./test.sh e2e/api-docs.spec.ts e2e/create-presentation.spec.ts e2e/delete-presentation.spec.ts e2e/presentations-list.spec.ts e2e/pagination.spec.ts
	$(call print_info,Batch 1 complete.)

test-e2e-batch2:
	$(call print_info,Running E2E Batch 2: Step and display tests...)
	@cd $(TESTING_DIR) && chmod +x test.sh && ./test.sh e2e/presentation-steps.spec.ts e2e/slides-display.spec.ts e2e/pptx-preview.spec.ts e2e/slides-customization.spec.ts e2e/illustration-stream.spec.ts
	$(call print_info,Batch 2 complete.)

test-e2e-batch3:
	$(call print_info,Running E2E Batch 3: Wizard tests...)
	@cd $(TESTING_DIR) && chmod +x test.sh && ./test.sh e2e/wizard.spec.ts e2e/wizard-general-context.spec.ts e2e/wizard-research-context.spec.ts e2e/wizard-slides-context.spec.ts e2e/wizard-improvements*.spec.ts
	$(call print_info,Batch 3 complete.)

test-e2e-batch4:
	$(call print_info,Running E2E Batch 4: Remaining tests...)
	@cd $(TESTING_DIR) && chmod +x test.sh && ./test.sh e2e/research-clarification.spec.ts e2e/research-content-display.spec.ts e2e/markdown-rendering.spec.ts e2e/markdown-slides.spec.ts
	$(call print_info,Batch 4 complete.)

# Run all E2E tests in batches
test-e2e-all-batches: test-e2e-batch1 test-e2e-batch2 test-e2e-batch3 test-e2e-batch4
	$(call print_info,All E2E test batches complete!)


# Reset the test database to initial seeded state
reset-test-db:
	$(call print_info,Resetting test database to initial seeded state...)
	@cd $(BACKEND_DIR) && POWERIT_ENV=test ./venv/bin/python reset_test_db.py
	$(call print_info,Test database reset complete.)

# Restart test servers (backend and frontend)
test-servers-restart:
	$(call print_info,Restarting test servers...)
	@$(MAKE) test-servers-stop
	@sleep 2
	@$(MAKE) test-servers-start
	$(call print_info,Test servers restarted.)

# Stop test servers
test-servers-stop:
	$(call print_info,Stopping test servers...)
	@pkill -f "run_api.py --test" || true
	@pkill -f "PORT=$(TEST_FRONTEND_PORT)" || true
	@sleep 1
	$(call print_info,Test servers stopped.)

# Start test servers
test-servers-start:
	$(call print_info,Starting test servers...)
	@cd $(BACKEND_DIR) && POWERIT_ENV=test POWERIT_OFFLINE=1 ./venv/bin/python run_api.py --test > /tmp/test_backend.log 2>&1 &
	@cd $(FRONTEND_DIR) && NEXT_PUBLIC_API_URL="http://localhost:$(TEST_BACKEND_PORT)" PORT=$(TEST_FRONTEND_PORT) npm run dev > /tmp/test_frontend.log 2>&1 &
	@sleep 5
	@if lsof -i:$(TEST_BACKEND_PORT) | grep LISTEN >/dev/null 2>&1; then \
		echo "✅ Backend started on port $(TEST_BACKEND_PORT)"; \
	else \
		echo "⚠️  Backend failed to start - check /tmp/test_backend.log"; \
	fi
	@if lsof -i:$(TEST_FRONTEND_PORT) | grep LISTEN >/dev/null 2>&1; then \
		echo "✅ Frontend started on port $(TEST_FRONTEND_PORT)"; \
	else \
		echo "⚠️  Frontend failed to start - check /tmp/test_frontend.log"; \
	fi
	$(call print_info,Test servers started.)

# ==========================================
# Combined Testing
# ==========================================

# Run all tests (backend offline + frontend)
test-all: test-backend-offline test-frontend
	$(call print_info,All tests complete!)

# Run all tests with network access
test-all-online: test-backend-online test-frontend
	$(call print_info,All online tests complete!)

# Run all tests without network access
test-all-offline: test-backend-offline test-frontend test-e2e
	$(call print_info,All offline tests complete!)

# Run all tests and show only failures summary
test-all-failures:
	$(call print_info,Running all tests and collecting failures...)
	@printf "=== RUNNING ALL TESTS - FAILURES ONLY ===\n" > test-failures.log
	@printf "Date: %s\n" "$$(date)" >> test-failures.log
	@printf "\n" >> test-failures.log
	
	$(call print_section,Backend Tests)
	@printf "🔧 Backend Tests:\n" >> test-failures.log
	@printf "Running backend tests...\n"
	@cd $(BACKEND_DIR) && chmod +x run_tests.sh && PYTEST_ARGS="--tb=short -v -m 'not network'" ./run_tests.sh 2>&1 | tee backend-test-output.log | grep -E "(FAILED|ERROR|AssertionError)" >> ../test-failures.log || true
	@if grep -q "failed" $(BACKEND_DIR)/backend-test-output.log 2>/dev/null; then \
		printf "\n⚠️  Backend tests had failures\n" >> test-failures.log; \
	else \
		printf "\n✅ Backend tests all passed\n" >> test-failures.log; \
	fi
	@rm -f $(BACKEND_DIR)/backend-test-output.log
	@printf "\n" >> test-failures.log
	
	$(call print_section,Starting Test Servers)
	@printf "🚀 Starting test servers...\n" >> test-failures.log
	@$(MAKE) test-servers-restart > /dev/null 2>&1
	@sleep 3
	@printf "✅ Test servers started\n" >> test-failures.log
	@printf "\n" >> test-failures.log
	
	$(call print_section,Resetting Test Database)
	@$(MAKE) reset-test-db > /dev/null 2>&1
	@printf "🗄️  Test database reset\n" >> test-failures.log
	@printf "\n" >> test-failures.log
	
	$(call print_section,E2E Tests)
	@printf "🌐 E2E Tests:\n" >> test-failures.log
	@printf "Running all E2E tests...\n"
	
	@# Run all E2E tests at once using test servers
	@cd $(TESTING_DIR) && chmod +x test.sh && ./test.sh 2>&1 | tee e2e-test-output.log | grep -E "(✘|FAILED|failed|Error:|TimeoutError)" >> ../test-failures.log || true
	
	@# Check if E2E tests passed or failed
	@if grep -q "failed" $(TESTING_DIR)/e2e-test-output.log 2>/dev/null; then \
		printf "\n⚠️  E2E tests had failures\n" >> test-failures.log; \
	else \
		printf "\n✅ E2E tests all passed\n" >> test-failures.log; \
	fi
	@rm -f $(TESTING_DIR)/e2e-test-output.log
	
	@printf "\n" >> test-failures.log
	@printf "=== FINAL SUMMARY ===\n" >> test-failures.log
	@if [ -s test-failures.log ] && grep -q -E "(FAILED|ERROR|✘|failed|AssertionError|TimeoutError)" test-failures.log; then \
		$(call print_warn,Tests completed with failures. See summary below:); \
		printf "\n"; \
		cat test-failures.log; \
		printf "\n"; \
		$(call print_warn,To run specific failing tests:); \
		printf "  Backend: make test-backend\n"; \
		printf "  E2E: make test-e2e\n"; \
		printf "  E2E specific: make test-e2e-specific test=test-name\n"; \
	else \
		$(call print_info,All tests passed! No failures detected.); \
		printf "All tests passed! No failures detected.\n" >> test-failures.log; \
		cat test-failures.log; \
	fi

# ==========================================
# Development Tools
# ==========================================

# Install project dependencies
install-deps:
	$(call print_info,Installing project dependencies...)
	@if command -v apt-get >/dev/null 2>&1; then \
		sudo apt-get update && sudo apt-get install -y python3 python3-venv python3-pip libreoffice ghostscript; \
	elif command -v brew >/dev/null 2>&1; then \
		brew install python3 libreoffice ghostscript; \
	else \
		$(call print_warn,Package manager not detected. Please install python3, libreoffice, and ghostscript manually.); \
	fi
	@cd $(BACKEND_DIR) && python3 -m venv venv && . venv/bin/activate && pip install --upgrade pip && pip install -r requirements.txt && deactivate
	@chmod +x $(BACKEND_DIR)/run_tests.sh $(BACKEND_DIR)/record_tests.sh $(BACKEND_DIR)/record_all_tests.sh 2>/dev/null || true
	@if [ -f $(FRONTEND_DIR)/package.json ]; then \
		cd $(FRONTEND_DIR) && npm install; \
	else \
		$(call print_warn,Skipping frontend install - package.json missing); \
	fi
	@if [ -f $(TESTING_DIR)/package.json ]; then \
		cd $(TESTING_DIR) && npm install; \
	else \
		$(call print_warn,Skipping testing install - package.json missing); \
	fi
	$(call print_info,Dependencies installation complete.)

# Install Playwright browsers
install-browsers:
	$(call print_info,Installing Playwright browsers...)
	@if [ -f $(TESTING_DIR)/package.json ]; then \
		cd $(TESTING_DIR); \
		if command -v apt-get >/dev/null 2>&1; then \
			$(call print_info,Installing system dependencies for Playwright browsers...); \
			if ! npx playwright install-deps 2>/dev/null; then \
				$(call print_warn,System dependencies installation failed. Trying with sudo...); \
				if command -v sudo >/dev/null 2>&1; then \
					sudo npx playwright install-deps || { \
						$(call print_warn,Failed to install system dependencies. Some E2E tests may not work.); \
					}; \
				else \
					$(call print_warn,sudo not available. Some E2E tests may not work without system dependencies.); \
				fi; \
			fi; \
		fi; \
		$(call print_info,Installing Playwright browser binaries...); \
		npx playwright install; \
	else \
		$(call print_warn,Cannot install browsers - testing/package.json missing); \
	fi
	$(call print_info,Browsers installation complete.)

# Install system dependencies for Playwright browsers (Linux only)
install-browser-deps:
	$(call print_info,Installing system dependencies for Playwright browsers...)
	@if command -v apt-get >/dev/null 2>&1; then \
		if [ -f $(TESTING_DIR)/package.json ]; then \
			cd $(TESTING_DIR); \
			if ! npx playwright install-deps 2>/dev/null; then \
				$(call print_warn,System dependencies installation failed. Trying with sudo...); \
				if command -v sudo >/dev/null 2>&1; then \
					sudo npx playwright install-deps || { \
						echo ""; \
						$(call print_warn,Failed to install system dependencies.); \
						$(call print_warn,You may need to install them manually:); \
						echo "  sudo apt-get update"; \
						echo "  sudo apt-get install -y libgtk-3-0 libgtk-4-1 libasound2 libxss1 libgconf-2-4 libxtst6 libxrandr2 libnss3 libgbm1"; \
						exit 1; \
					}; \
				else \
					$(call print_warn,sudo not available. Please run with root privileges or install dependencies manually.); \
					exit 1; \
				fi; \
			fi; \
		else \
			$(call print_warn,Cannot install browser dependencies - testing/package.json missing); \
			exit 1; \
		fi; \
	else \
		$(call print_warn,System dependency installation only supported on apt-based Linux distributions); \
		$(call print_warn,For other systems, please install Playwright dependencies according to your package manager); \
	fi
	$(call print_info,System dependencies installation complete.)

# ==========================================
# Legacy aliases (for backward compatibility)
# ==========================================

e2e: test-e2e
e2e-headed: test-e2e-headed  
e2e-debug: test-e2e-debug
e2e-api: test-e2e-api
e2e-test: test-e2e-specific
e2e-list: test-e2e-list
e2e-install: install-browsers
browser-deps: install-browser-deps
