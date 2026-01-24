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
  "REFACTOR-01|Convert relative imports → @core aliases|P2|refactor"
  "REFACTOR-02|Convert relative imports → @features aliases|P2|refactor"
  "REFACTOR-03|Convert relative imports → @shared aliases|P2|refactor"
  "SPLIT-01|Decompose run-protocol.component.ts (1477 lines)|P2|refactor"
  "SPLIT-02|Decompose playground.component.ts (1324 lines)|P2|refactor"
  "SPLIT-03|Decompose data-visualization.component.ts (932 lines)|P2|refactor"
  "SPLIT-04|Decompose scheduler.py (732 lines)|P2|refactor"
  "SPLIT-05|Decompose plr_inspection.py (716 lines)|P2|refactor"
  "SPLIT-06|Decompose resource_type_definition.py (701 lines)|P2|refactor"
  "E2E-AUDIT-01|Audit E2E test coverage gaps|P1|testing"
  "E2E-NEW-01|Create OPFS migration E2E tests|P1|testing"
  "E2E-NEW-02|Create monitor detail E2E tests|P2|testing"
  "E2E-NEW-03|Create workcell dashboard E2E tests|P2|testing"
  "E2E-RUN-01|Run & fix asset management E2E tests|P1|testing"
  "E2E-RUN-02|Run & fix protocol execution E2E tests|P1|testing"
  "E2E-RUN-03|Run & fix browser persistence E2E tests|P1|testing"
  "E2E-VIZ-01|Visual audit - Asset pages|P2|visual"
  "E2E-VIZ-02|Visual audit - Run protocol pages|P2|visual"
  "E2E-VIZ-03|Visual audit - Data & Playground|P2|visual"
  "E2E-VIZ-04|Visual audit - Settings & Workcell|P2|visual"
  "JLITE-01|Audit simulate-ghpages.sh directory structure|P1|jupyterlite"
  "JLITE-02|Audit & fix theme CSS path doubling|P1|jupyterlite"
  "JLITE-03|Fix Pyodide kernel auto-initialization|P1|jupyterlite"
  "OPFS-01|Audit protocol running via Pyodide under OPFS|P2|opfs"
  "OPFS-02|Review asset instantiation under OPFS|P2|opfs"
  "OPFS-03|Review hardware discovery under OPFS|P2|opfs"
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
