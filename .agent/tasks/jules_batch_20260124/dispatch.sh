#!/bin/bash
# Jules Batch Dispatch Script
# Dispatches all tasks to Jules and logs session IDs
#
# Usage:
#   ./dispatch.sh              # Dispatch all tasks
#   ./dispatch.sh --dry-run    # Preview without dispatching
#   ./dispatch.sh --filter "REFACTOR"  # Dispatch matching tasks only

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROMPTS_DIR="$SCRIPT_DIR/prompts"
LOG_FILE="$SCRIPT_DIR/dispatch_log.md"
DRY_RUN=false
FILTER=""

# Parse arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --dry-run)
      DRY_RUN=true
      shift
      ;;
    --filter)
      FILTER="$2"
      shift 2
      ;;
    *)
      echo "Unknown option: $1"
      exit 1
      ;;
  esac
done

# Task definitions with metadata
# Format: "ID|TITLE|PRIORITY|CATEGORY"
declare -a TASKS=(
  "DOC-01|Update CONTRIBUTING.md with uv commands|P2|docs"
  "DOC-02|Fix Docker service names in docs|P2|docs"
  "DOC-03|Create CHANGELOG.md|P2|docs"
  "FIX-01|Implement machine editing TODO|P2|fix"
  "FIX-02|Implement resource editing TODO|P2|fix"
  "FIX-03|Add deck confirmation dialog|P2|fix"
  "FIX-04|Guard method.args undefined in direct-control|P1|fix"
  "TEST-01|Add unit tests for name-parser.ts|P2|testing"
  "TEST-02|Expand unit tests for linked-selector.service|P2|testing"
  "TEST-03|Create workcell dashboard E2E|P2|testing"
  "STYLE-01|Theme vars in protocol-summary|P2|styling"
  "STYLE-02|Theme vars in live-dashboard|P2|styling"
  "STYLE-03|Theme vars in settings|P2|styling"
  "REFACTOR-01|Add user-friendly error toasts to asset-wizard|P2|refactor"
  "REFACTOR-02|Document SharedArrayBuffer limitation|P3|docs"
)

# Initialize dispatch log
initialize_log() {
  cat > "$LOG_FILE" << 'EOF'
# Jules Dispatch Log

**Dispatched**: $(date +"%Y-%m-%d %H:%M:%S")
**Total Tasks**: TASK_COUNT
**Dispatcher**: jules-dispatch-batch

## Session Tracking

| ID | Title | Session ID | Status | Priority | Category |
|:---|:------|:-----------|:-------|:---------|:---------|
EOF
  # Replace placeholder
  local count=${#TASKS[@]}
  sed -i '' "s/TASK_COUNT/$count/" "$LOG_FILE" 2>/dev/null || \
  sed -i "s/TASK_COUNT/$count/" "$LOG_FILE"
}

# Dispatch a single task
dispatch_task() {
  local id="$1"
  local title="$2"
  local priority="$3"
  local category="$4"
  local prompt_file="$PROMPTS_DIR/${id}.md"
  
  if [[ ! -f "$prompt_file" ]]; then
    echo "⚠️  Missing prompt: $prompt_file"
    echo "| $id | $title | **MISSING PROMPT** | SKIPPED | $priority | $category |" >> "$LOG_FILE"
    return 1
  fi
  
  local prompt
  prompt=$(cat "$prompt_file")
  
  if [[ "$DRY_RUN" == "true" ]]; then
    echo "🔵 [DRY-RUN] Would dispatch: $id - $title"
    echo "| $id | $title | (dry-run) | PENDING | $priority | $category |" >> "$LOG_FILE"
    return 0
  fi
  
  echo "🚀 Dispatching: $id - $title"
  
  # Dispatch to Jules and capture session ID
  local output
  output=$(jules remote new --session "Title: $title

$prompt" 2>&1)
  
  # Extract session ID from output
  local session_id
  session_id=$(echo "$output" | grep -oE '[a-f0-9-]{36}' | head -1 || echo "")
  
  if [[ -z "$session_id" ]]; then
    # Try alternative pattern
    session_id=$(echo "$output" | grep -oE 'session[_-]?[a-zA-Z0-9-]+' | head -1 || echo "PARSE_ERROR")
  fi
  
  if [[ -z "$session_id" || "$session_id" == "PARSE_ERROR" ]]; then
    echo "   ⚠️  Could not parse session ID"
    echo "   Output: $output"
    session_id="DISPATCH_FAILED"
  else
    echo "   ✅ Session: $session_id"
  fi
  
  echo "| $id | $title | \`$session_id\` | QUEUED | $priority | $category |" >> "$LOG_FILE"
  
  # Small delay to avoid rate limiting
  sleep 1
}

# Main dispatch loop
main() {
  echo "========================================"
  echo "  Jules Batch Dispatcher"
  echo "========================================"
  echo ""
  
  if [[ "$DRY_RUN" == "true" ]]; then
    echo "🔵 DRY RUN MODE - No actual dispatches"
    echo ""
  fi
  
  if [[ -n "$FILTER" ]]; then
    echo "🔍 Filter: $FILTER"
    echo ""
  fi
  
  initialize_log
  
  local dispatched=0
  local skipped=0
  
  for task in "${TASKS[@]}"; do
    IFS='|' read -r id title priority category <<< "$task"
    
    # Apply filter if specified
    if [[ -n "$FILTER" && ! "$id" =~ $FILTER ]]; then
      continue
    fi
    
    if dispatch_task "$id" "$title" "$priority" "$category"; then
      ((dispatched++))
    else
      ((skipped++))
    fi
  done
  
  echo ""
  echo "========================================"
  echo "  Summary"
  echo "========================================"
  echo "  Dispatched: $dispatched"
  echo "  Skipped:    $skipped"
  echo "  Log file:   $LOG_FILE"
  echo ""
  
  # Add summary to log
  cat >> "$LOG_FILE" << EOF

---

## Summary

- **Dispatched**: $dispatched
- **Skipped**: $skipped
- **Timestamp**: $(date +"%Y-%m-%d %H:%M:%S")

## Review Priority

Review sessions in this order:
1. **P1 Tasks** - Critical blockers and core functionality
2. **P1 Visual** - E2E runs that include visual audit
3. **P2 Tasks** - Refactoring and secondary features

## Next Steps

1. Monitor Jules dashboard for completed sessions
2. Use \`jules remote list\` to check status
3. Review completed sessions with \`jules remote pull <session_id>\`
4. Apply approved changes with \`jules remote pull <session_id> --apply\`
5. Update DEVELOPMENT_MATRIX.md with results
EOF
}

main "$@"
