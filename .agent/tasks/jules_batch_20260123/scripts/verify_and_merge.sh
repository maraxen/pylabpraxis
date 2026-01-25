#!/bin/bash
set -e

# Verify and Merge Script
# Usage: ./verify_and_merge.sh <WORKTREE_NAME> <TEST_SCOPES>

WT_NAME=$1
TEST_SCOPES=$2
REPO_ROOT="$(git rev-parse --show-toplevel)"
WT_DIR="$REPO_ROOT/.worktrees/$WT_NAME"
BRANCH_NAME="feature/$WT_NAME"

echo "=================================================="
echo "Processing Merge for $WT_NAME"
echo "Worktree: $WT_DIR"
echo "Branch: $BRANCH_NAME"
echo "=================================================="

if [ ! -d "$WT_DIR" ]; then
    echo "Error: Worktree $WT_DIR does not exist."
    exit 1
fi

# 1. Setup & Test in Worktree
echo "-> Setting up environment in worktree..."
cd "$WT_DIR/praxis/web-client"

# Ensure dependencies (fast CI install if possible, but regular install is safer for worktrees)
# Check if node_modules exists to save time? No, reliable is better.
npm install

echo "-> Running tests..."
# Construct test command. Assuming 'ng test' or 'npm run test'
# We use 'npm run test -- --select=...' pattern
echo "Executing: npm run test -- $TEST_SCOPES --watch=false --browsers=ChromeHeadless"

# Use HEADLESS browser for CI-like execution
if npm run test -- $TEST_SCOPES --watch=false --browsers=ChromeHeadless; then
    echo "✅ Tests Passed!"
else
    echo "❌ Tests Failed. Aborting merge."
    exit 1
fi

# 2. Merge into Main
echo "-> Merging into main..."
cd "$REPO_ROOT"

# Ensure main is clean and up to date? 
# We assume main is checked out in REPO_ROOT
current_branch=$(git rev-parse --abbrev-ref HEAD)
if [ "$current_branch" != "main" ]; then
    echo "Warning: Root repo is on $current_branch, not main. Checking out main..."
    git checkout main
fi

# Merge
git merge "$BRANCH_NAME" --no-ff -m "Merge branch '$BRANCH_NAME' (Jules Integration)"

# 3. Cleanup
echo "-> Cleaning up..."
# Delete branch
git branch -d "$BRANCH_NAME"
# Remove worktree
git worktree remove "$WT_DIR" --force

echo "✅ Optimization Complete for $WT_NAME"
