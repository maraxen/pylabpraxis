#!/bin/bash
set -e

# Setup Worktree Batch Script
# Usage: ./setup_worktree.sh <TASK_ID> <SESSION_ID> <WORKTREE_NAME>

TASK_ID=$1
SESSION_ID=$2
WT_NAME=$3
STAGING_FILE=".agent/staging/${TASK_ID}.md"
REPO_ROOT="$(git rev-parse --show-toplevel)"
WT_DIR="$REPO_ROOT/.worktrees/$WT_NAME"

echo "Setting up worktree $WT_NAME for $TASK_ID..."

# Check if worktree directory exists
if [ -d "$WT_DIR" ]; then
    echo "Worktree $WT_DIR already exists. Using it."
else
    # Verify .worktrees is ignored in the MAIN repo
    cd "$REPO_ROOT"
    if ! git check-ignore -q .worktrees; then
        echo ".worktrees is not ignored! Adding to .gitignore..."
        echo ".worktrees/" >> .gitignore
    fi
    
    # Create worktree
    # Check if branch exists
    if git rev-parse --verify "feature/$WT_NAME" >/dev/null 2>&1; then
        echo "Branch feature/$WT_NAME exists. Checking it out in worktree."
        git worktree add "$WT_DIR" "feature/$WT_NAME"
    else
        echo "Creating new branch feature/$WT_NAME."
        git worktree add "$WT_DIR" -b "feature/$WT_NAME"
    fi
    
    # Run setup
    cd "$WT_DIR"
    # Only run npm install if package.json exists
    if [ -f "package.json" ]; then
        echo "Running npm install..."
        npm install
    fi
fi

# Navigate to worktree
cd "$WT_DIR"

echo "Applying patch in worktree..."
# We need to make sure we are in the worktree context for jules to apply correctly
# Jules presumably uses CWD.
jules remote pull --session "$SESSION_ID" --apply

echo "Worktree ready at $WT_DIR"
