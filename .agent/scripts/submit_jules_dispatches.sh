#!/bin/bash
# Submit pending Jules dispatches from the agent database
# Usage: ./submit_jules_dispatches.sh

DB_PATH="/Users/mar/Projects/pylabpraxis/.agent/agent.db"
REPO="maraxen/pylabpraxis"
BRANCH="angular_refactor"

# Get all pending jules dispatches
sqlite3 -separator '|' "$DB_PATH" \
  "SELECT id, prompt_full FROM dispatches WHERE target = 'jules' AND status = 'pending' ORDER BY created_at ASC" | \
while IFS='|' read -r dispatch_id prompt; do
  echo "=========================================="
  echo "Submitting dispatch: $dispatch_id"
  echo "=========================================="
  
  # Create temp file for the prompt
  TEMP_FILE=$(mktemp)
  echo "$prompt" > "$TEMP_FILE"
  
  # Submit to Jules
  # Note: jules remote new expects prompt on stdin or as argument
  jules remote new --session "$(cat "$TEMP_FILE")" 2>&1
  
  JULES_EXIT=$?
  
  # Clean up
  rm -f "$TEMP_FILE"
  
  if [ $JULES_EXIT -eq 0 ]; then
    echo "✓ Dispatch $dispatch_id submitted successfully"
    # Update status in database
    sqlite3 "$DB_PATH" "UPDATE dispatches SET status = 'running', claimed_at = datetime('now') WHERE id = '$dispatch_id'"
  else
    echo "✗ Dispatch $dispatch_id failed to submit"
  fi
  
  # Small delay to avoid rate limiting
  sleep 2
done

echo ""
echo "Done! Check jules remote list for status."
