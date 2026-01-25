#!/bin/bash
set -e

# Apply Batch Script
# Usage: ./apply_batch.sh <TASK_ID> <SESSION_ID>

TASK_ID=$1
SESSION_ID=$2
STAGING_FILE=".agent/staging/${TASK_ID}.md"

echo "Processing $TASK_ID ($SESSION_ID)..."

if [ ! -f "$STAGING_FILE" ]; then
    echo "Staging file not found: $STAGING_FILE"
    # Try pulling it if missing
    jules remote pull --session "$SESSION_ID" > "$STAGING_FILE"
fi

# Apply the patch
echo "Applying patch for $TASK_ID..."
jules remote pull --session "$SESSION_ID" --apply

echo "Done $TASK_ID"
