# Makefile for PowerIt project
# Contains commands for running tests and other common tasks

# Variables
SHELL := /bin/bash
TESTING_DIR := testing
E2E_DIR := $(TESTING_DIR)/e2e

# Color outputs
YELLOW := \033[1;33m
GREEN := \033[1;32m
NC := \033[0m # No Color
INFO := @echo "$(GREEN)$(1)$(NC)"
WARN := @echo "$(YELLOW)$(1)$(NC)"

.PHONY: setup e2e e2e-headed e2e-debug e2e-list e2e-install help

# Default target when just running `make`
help:
	@echo "$(GREEN)Available commands:$(NC)"
	@echo "  $(YELLOW)make run$(NC)            - Run the complete application (backend + frontend)"
	@echo "  $(YELLOW)make test-backend$(NC)   - Run backend tests"
	@echo "  $(YELLOW)make setup$(NC)         - Install backend and E2E dependencies"
	@echo "  $(YELLOW)make e2e$(NC)            - Run all E2E tests"
	@echo "  $(YELLOW)make e2e-headed$(NC)     - Run all E2E tests with browser visible"
	@echo "  $(YELLOW)make e2e-debug$(NC)      - Run E2E tests with debugging enabled (headed + slow motion)"
	@echo "  $(YELLOW)make e2e-test$(NC) test=file-name - Run specific E2E tests (e.g., make e2e-test test=presentations-list)"
	@echo "  $(YELLOW)make e2e-list$(NC)       - List all available E2E tests"
	@echo "  $(YELLOW)make e2e-install$(NC)    - Install Playwright browsers"
	@echo ""
	@echo "$(GREEN)Examples:$(NC)"
	@echo "  $(YELLOW)make test-backend$(NC)"
	@echo "  $(YELLOW)make e2e-test test=presentations-list$(NC)"
	@echo "  $(YELLOW)make e2e-headed$(NC)"

# Run the application
run:
	$(call INFO,Starting the application...)
	chmod +x run.sh && ./run.sh
	$(call INFO,Application has been stopped.)

# Run backend tests
test-backend:
	$(call INFO,Running backend tests...)
	cd $(BACKEND_DIR) && chmod +x run_tests.sh && ./run_tests.sh
	$(call INFO,Backend tests complete. See results above.)

# Run all E2E tests
e2e:
	$(call INFO,Running all E2E tests...)
	cd $(TESTING_DIR) && npx playwright test
	$(call INFO,E2E tests complete. See results above.)

# Run all E2E tests with browser visible
e2e-headed:
	$(call INFO,Running all E2E tests with browser visible...)
	cd $(TESTING_DIR) && npx playwright test --headed
	$(call INFO,E2E tests complete. See results above.)

# Run E2E tests with debugging enabled
e2e-debug:
	$(call INFO,Running E2E tests with debugging enabled...)
	cd $(TESTING_DIR) && npx playwright test --headed --debug --timeout 60000
	$(call INFO,E2E debug tests complete.)

# Run specific E2E tests
e2e-test:
	@if [ -z "$(test)" ]; then \
		echo "$(YELLOW)Error: No test specified. Usage: make e2e-test test=test-name$(NC)"; \
		exit 1; \
	fi
	$(call INFO,Running E2E test: $(test)...)
	cd $(TESTING_DIR) && npx playwright test e2e/$(test).spec.ts
	$(call INFO,E2E test complete. See results above.)

# List all available E2E tests
e2e-list:
	$(call INFO,Available E2E tests:)
	@find $(E2E_DIR) -name "*.spec.ts" | sed 's|$(E2E_DIR)/||g' | sed 's|\.spec\.ts$$||g' | sort
	
# Install Playwright browsers
e2e-install:
	$(call INFO,Installing Playwright browsers...)
	cd $(TESTING_DIR) && npx playwright install
	$(call INFO,Browsers installed.)

setup:
	$(call INFO,Setting up project dependencies...)
	sudo apt-get update && sudo apt-get install -y python3 python3-venv python3-pip libreoffice ghostscript
	cd backend && python3 -m venv venv && . venv/bin/activate && pip install --upgrade pip && pip install -r requirements.txt && deactivate
	chmod +x backend/run_tests.sh backend/record_tests.sh backend/record_all_tests.sh
	if [ -f frontend/package.json ]; then cd frontend && npm install && cd ..; else echo "Skipping frontend install - package.json missing"; fi
	cd testing && npm install && npm run install-browsers && cd ..
	$(call INFO,Setup complete.)
