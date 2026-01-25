#!/bin/bash
# Jules Audit Batch Dispatch Script - 2026-01-24
# Dispatches 9 high-level audits to Jules

set -e

PROMPTS_DIR="/Users/mar/Projects/praxis/.agent/tasks/jules_audit_20260124/prompts"
LOG_FILE="/Users/mar/Projects/praxis/.agent/tasks/jules_audit_20260124/dispatch_log.md"

echo "# Dispatch Log - $(date)" > "$LOG_FILE"
echo "" >> "$LOG_FILE"

# Array of audit IDs
AUDITS=(
  "AUDIT-01:Run Protocol & Wizard"
  "AUDIT-02:Asset Management"
  "AUDIT-03:Protocol Library & Execution"
  "AUDIT-04:Playground & Data Viz"
  "AUDIT-05:Workcell Dashboard"
  "AUDIT-06:Browser Persistence"
  "AUDIT-07:JupyterLite Integration"
  "AUDIT-08:GH-Pages Config"
  "AUDIT-09:Direct Control"
)

echo "Starting Jules dispatch for ${#AUDITS[@]} audits..."
echo ""

for audit in "${AUDITS[@]}"; do
  ID="${audit%%:*}"
  TITLE="${audit#*:}"
  PROMPT_FILE="$PROMPTS_DIR/${ID}.md"
  
  if [[ ! -f "$PROMPT_FILE" ]]; then
    echo "ERROR: Prompt file not found: $PROMPT_FILE"
    continue
  fi
  
  echo "Dispatching $ID: $TITLE"
  
  # Read prompt content
  PROMPT=$(cat "$PROMPT_FILE")
  
  # Dispatch to Jules
  # Note: jules remote new --session expects the full prompt as input
  echo "---" >> "$LOG_FILE"
  echo "## $ID: $TITLE" >> "$LOG_FILE"
  echo "- Dispatched: $(date)" >> "$LOG_FILE"
  
  # Run the actual dispatch
  jules remote new --session "$PROMPT" 2>&1 | tee -a "$LOG_FILE"
  
  echo "- Status: dispatched" >> "$LOG_FILE"
  echo "" >> "$LOG_FILE"
  
  # Small delay to avoid rate limiting
  sleep 2
done

echo ""
echo "All audits dispatched. Check $LOG_FILE for session IDs."
