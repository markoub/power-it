#!/bin/bash

# Git Commit Helper Script
# This script helps you review changes and create meaningful git commits

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== Git Commit Helper ===${NC}"
echo ""

# Function to show current status
show_status() {
    echo -e "${YELLOW}Current Git Status:${NC}"
    git status --short
    echo ""
}

# Function to show detailed changes
show_changes() {
    echo -e "${YELLOW}Changed Files Summary:${NC}"
    git diff --stat
    echo ""
    
    echo -e "${YELLOW}Would you like to see detailed changes? (y/n)${NC}"
    read -r response
    if [[ "$response" == "y" ]]; then
        git diff
    fi
}

# Function to stage files
stage_files() {
    echo -e "${YELLOW}Files to stage:${NC}"
    echo "1) Stage all changes (git add -A)"
    echo "2) Stage specific files"
    echo "3) Stage all modified files only (git add -u)"
    echo "4) Interactive staging (git add -p)"
    echo "5) Skip staging"
    
    read -r choice
    case $choice in
        1)
            git add -A
            echo -e "${GREEN}All changes staged${NC}"
            ;;
        2)
            echo "Enter files to stage (space-separated):"
            read -r files
            git add $files
            echo -e "${GREEN}Specified files staged${NC}"
            ;;
        3)
            git add -u
            echo -e "${GREEN}All modified files staged${NC}"
            ;;
        4)
            git add -p
            ;;
        5)
            echo "Skipping staging"
            ;;
        *)
            echo -e "${RED}Invalid choice${NC}"
            ;;
    esac
    echo ""
}

# Function to create commit
create_commit() {
    echo -e "${YELLOW}Staged changes:${NC}"
    git diff --cached --stat
    echo ""
    
    echo -e "${YELLOW}Enter commit type:${NC}"
    echo "1) feat: A new feature"
    echo "2) fix: A bug fix"
    echo "3) docs: Documentation changes"
    echo "4) style: Code style changes"
    echo "5) refactor: Code refactoring"
    echo "6) test: Adding or updating tests"
    echo "7) chore: Maintenance tasks"
    echo "8) custom: Enter custom type"
    
    read -r type_choice
    
    case $type_choice in
        1) commit_type="feat" ;;
        2) commit_type="fix" ;;
        3) commit_type="docs" ;;
        4) commit_type="style" ;;
        5) commit_type="refactor" ;;
        6) commit_type="test" ;;
        7) commit_type="chore" ;;
        8) 
            echo "Enter custom type:"
            read -r commit_type
            ;;
        *) 
            echo -e "${RED}Invalid choice, using 'chore'${NC}"
            commit_type="chore"
            ;;
    esac
    
    echo -e "${YELLOW}Enter commit scope (optional, press Enter to skip):${NC}"
    read -r scope
    
    echo -e "${YELLOW}Enter commit message:${NC}"
    read -r message
    
    # Build commit message
    if [[ -n "$scope" ]]; then
        full_message="${commit_type}(${scope}): ${message}"
    else
        full_message="${commit_type}: ${message}"
    fi
    
    echo ""
    echo -e "${YELLOW}Commit message will be:${NC}"
    echo "$full_message"
    echo ""
    echo -e "${YELLOW}Add extended description? (y/n)${NC}"
    read -r add_description
    
    if [[ "$add_description" == "y" ]]; then
        echo "Enter description (press Ctrl+D when done):"
        description=$(cat)
        
        # Create commit with description
        git commit -m "$full_message" -m "$description"
    else
        # Create commit without description
        git commit -m "$full_message"
    fi
    
    echo -e "${GREEN}Commit created successfully!${NC}"
}

# Main flow
main() {
    # Check if we're in a git repository
    if ! git rev-parse --git-dir > /dev/null 2>&1; then
        echo -e "${RED}Error: Not in a git repository${NC}"
        exit 1
    fi
    
    # Show current status
    show_status
    
    # Check if there are any changes
    if [[ -z $(git status --porcelain) ]]; then
        echo -e "${GREEN}No changes to commit${NC}"
        exit 0
    fi
    
    # Show changes
    show_changes
    
    # Stage files
    stage_files
    
    # Check if anything is staged
    if [[ -z $(git diff --cached --name-only) ]]; then
        echo -e "${YELLOW}No files staged for commit${NC}"
        exit 0
    fi
    
    # Create commit
    create_commit
    
    # Show final status
    echo ""
    echo -e "${YELLOW}Final status:${NC}"
    git status --short
    
    echo ""
    echo -e "${YELLOW}Recent commits:${NC}"
    git log --oneline -5
}

# Run main function
main