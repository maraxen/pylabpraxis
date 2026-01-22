#!/bin/bash
# Jules Session Retrieval & Diff Saver
# Purpose: Retrieve diffs from all completed Jules sessions, save locally, and identify reports
#
# Usage:
#   ./scripts/fetch_jules_diffs.sh

set -euo pipefail

TODAY=$(date +%Y-%m-%d)
DIFF_DIR=".agent/reports/jules_diffs/$TODAY"
mkdir -p "$DIFF_DIR"

echo ""
echo "📥 Fetching Jules Session Diffs to $DIFF_DIR"
echo "=================================================="

# Get completed sessions
SESSIONS=$(jules remote list --session 2>&1 | cat | grep "maraxen/praxis" | grep -E "Completed|Done" | awk '{print $1}')

if [[ -z "$SESSIONS" ]]; then
    echo "No completed sessions found."
    exit 0
fi

SESSION_COUNT=$(echo "$SESSIONS" | wc -l | tr -d ' ')
echo "Found $SESSION_COUNT sessions to check."
echo ""

for session_id in $SESSIONS; do
    echo "Processing $session_id..."
    
    # Create session dir
    SESSION_DIR="$DIFF_DIR/$session_id"
    mkdir -p "$SESSION_DIR"
    
    # Check if we already have the diff
    if [[ -f "$SESSION_DIR/changes.diff" ]]; then
        echo "   Skipping (already fetched)"
        continue
    fi
    
    # Pull diff
    DIFF_CONTENT=$(jules remote pull --session "$session_id" 2>&1 || true)
    
    # Save raw output just in case
    echo "$DIFF_CONTENT" > "$SESSION_DIR/raw_output.txt"
    
    # Check if it contains a diff
    if echo "$DIFF_CONTENT" | grep -q "^diff --git"; then
        echo "$DIFF_CONTENT" > "$SESSION_DIR/changes.diff"
        echo "   ✅ Saved diff ($SESSION_DIR/changes.diff)"
    else
        echo "   ⚠️  No diff found (Content saved to raw_output.txt)"
    fi
done

echo ""
echo "🔍 Scanning for Reports in Diffs..."
echo "=================================================="

# Find all diffs that contain new report files
# Look for '+++ b/.agent/reports/' pattern
grep -l "+++ b/.agent/reports/" "$DIFF_DIR"/*/changes.diff | while read diff_file; do
    session_id=$(basename $(dirname "$diff_file"))
    echo "📄 Found Report(s) in Session $session_id"
    
    # Extract filename(s)
    grep "+++ b/.agent/reports/" "$diff_file" | sed 's/+++ b\///' | sed 's/^/   └─ /'
    
    # Check if ONLY reports changed (safe to apply)
    # Count files changed in diff
    TOTAL_FILES=$(grep "^diff --git" "$diff_file" | wc -l)
    REPORT_FILES=$(grep "^diff --git" "$diff_file" | grep ".agent/reports/" | wc -l)
    
    if [[ "$TOTAL_FILES" -eq "$REPORT_FILES" ]]; then
        echo "   ✅ SAFE TO APPLY (Only reports changed)"
        echo "   run: jules remote pull --session $session_id --apply"
    else
        echo "   ⚠️  MIXED CHANGES (Review required)"
        grep "^diff --git" "$diff_file" | grep -v ".agent/reports/" | sed 's/diff --git a\/\(.*\) b\/.*/   ⚠️  Changed: \1/'
    fi
    echo ""
done

echo "Done."
