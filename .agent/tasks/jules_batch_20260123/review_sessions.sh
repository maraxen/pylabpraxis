#!/bin/bash
# Jules Session Review Script
# Pulls diffs from all completed sessions, filters files, generates report

set -e

REVIEW_DIR="$(dirname "$0")/session_reviews"
REPORT_FILE="$(dirname "$0")/REVIEW_REPORT.md"

# Create review directory
mkdir -p "$REVIEW_DIR"

# Completed session IDs from jules remote list (Jan 23 batch only)
declare -A SESSIONS=(
    # REFACTOR
    ["REFACTOR-02"]="3806881592450903343"
    ["REFACTOR-03"]="13019827227538808257"
    
    # SPLIT
    ["SPLIT-02"]="1174395877673969907"
    ["SPLIT-03"]="13313504630511132226"
    ["SPLIT-04"]="8806860709165683043"
    ["SPLIT-05"]="7027017935549180084"
    ["SPLIT-06"]="2939224647793981217"
    
    # E2E
    ["E2E-AUDIT-01"]="3561513229318693513"
    ["E2E-NEW-01"]="16991222562636305897"
    ["E2E-NEW-02"]="16282140182043530519"
    ["E2E-NEW-03"]="8998018472489986175"
    ["E2E-VIZ-02"]="12590817473184387784"
    ["E2E-VIZ-03"]="16182069641460709376"
    
    # JLITE
    ["JLITE-03"]="14542845870678146245"
    
    # OPFS
    ["OPFS-01"]="9221878143682473760"
    ["OPFS-03"]="14808794888910746056"
)

# Initialize report
cat > "$REPORT_FILE" << 'EOF'
# Jules Session Review Report

**Generated**: $(date)
**Total Sessions**: ${#SESSIONS[@]}

## Review Summary

| Task ID | Files Changed | Status | Action |
|:--------|:--------------|:-------|:-------|
EOF

echo "Pulling ${#SESSIONS[@]} completed sessions..."

for TASK_ID in "${!SESSIONS[@]}"; do
    SESSION_ID="${SESSIONS[$TASK_ID]}"
    SESSION_DIR="$REVIEW_DIR/$TASK_ID"
    
    echo "=== Processing $TASK_ID (Session: $SESSION_ID) ==="
    mkdir -p "$SESSION_DIR"
    
    # Pull session (no apply, just review)
    if jules remote pull --session "$SESSION_ID" > "$SESSION_DIR/pull_output.txt" 2>&1; then
        echo "  ✓ Pulled successfully"
        
        # Get diff
        git diff origin/main...HEAD -- . ':(exclude)*.png' ':(exclude)package.json' ':(exclude)package-lock.json' > "$SESSION_DIR/filtered_diff.patch" 2>/dev/null || true
        
        # List files changed (excluding images and package files)
        git diff --name-only origin/main...HEAD -- . ':(exclude)*.png' ':(exclude)package.json' ':(exclude)package-lock.json' > "$SESSION_DIR/files_changed.txt" 2>/dev/null || true
        
        FILE_COUNT=$(wc -l < "$SESSION_DIR/files_changed.txt" | tr -d ' ')
        echo "  Files changed: $FILE_COUNT"
        
        # Add to report
        echo "| $TASK_ID | $FILE_COUNT | ✅ Pulled | Pending Review |" >> "$REPORT_FILE"
    else
        echo "  ✗ Pull failed"
        echo "| $TASK_ID | - | ❌ Failed | Check manually |" >> "$REPORT_FILE"
    fi
    
    # Reset for next session
    git checkout main --quiet 2>/dev/null || true
done

echo ""
echo "Review complete. Report saved to: $REPORT_FILE"
echo "Session data saved to: $REVIEW_DIR/"
