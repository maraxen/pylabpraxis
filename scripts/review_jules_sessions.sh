#!/bin/bash
# Jules Session Review Script
# Purpose: Review completed Jules sessions and categorize by change type
# 
# Categories:
#   - REPORTS_ONLY: Only .agent/reports/* files changed → safe to auto-apply
#   - CODE_CHANGES: Other files changed → needs manual review
#   - NO_CHANGES: No diff → inspect session output for message
#
# Usage:
#   ./scripts/review_jules_sessions.sh           # Review all completed
#   ./scripts/review_jules_sessions.sh --apply   # Auto-apply reports-only sessions

set -euo pipefail

AUTO_APPLY=false
if [[ "${1:-}" == "--apply" ]]; then
    AUTO_APPLY=true
fi

echo ""
echo "🔍 Jules Session Review"
echo "========================"
echo ""

# Get completed sessions for praxis repo
SESSIONS=$(jules remote list --session 2>&1 | cat | grep "maraxen/praxis" | grep -E "Completed|Done" | awk '{print $1}')

if [[ -z "$SESSIONS" ]]; then
    echo "No completed sessions found for maraxen/praxis"
    exit 0
fi

SESSION_COUNT=$(echo "$SESSIONS" | wc -l | tr -d ' ')
echo "Found $SESSION_COUNT completed session(s)"
echo ""

# Arrays to track categories
declare -a REPORTS_ONLY=()
declare -a CODE_CHANGES=()
declare -a NO_CHANGES=()

for session_id in $SESSIONS; do
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "📋 Session: $session_id"
    
    # Pull the session (without applying) to get the diff
    PULL_OUTPUT=$(jules remote pull --session "$session_id" 2>&1 || true)
    
    # Check if there's a diff section
    if echo "$PULL_OUTPUT" | grep -q "^diff --git"; then
        # Extract changed files from diff
        CHANGED_FILES=$(echo "$PULL_OUTPUT" | grep "^diff --git" | sed 's/diff --git a\/\(.*\) b\/.*/\1/' | sort -u)
        
        # Check if all changes are in .agent/reports/
        NON_REPORT_FILES=$(echo "$CHANGED_FILES" | grep -v "^\.agent/reports/" || true)
        
        if [[ -z "$NON_REPORT_FILES" ]]; then
            echo "   📁 Category: REPORTS_ONLY"
            echo "   Files:"
            echo "$CHANGED_FILES" | sed 's/^/      /'
            REPORTS_ONLY+=("$session_id")
            
            if $AUTO_APPLY; then
                echo "   🔧 Auto-applying..."
                jules remote pull --session "$session_id" --apply 2>&1 | tail -3
                echo "   ✅ Applied"
            fi
        else
            echo "   ⚠️  Category: CODE_CHANGES (needs review)"
            echo "   Report files:"
            echo "$CHANGED_FILES" | grep "^\.agent/reports/" | sed 's/^/      /' || echo "      (none)"
            echo "   Other files:"
            echo "$NON_REPORT_FILES" | sed 's/^/      /'
            CODE_CHANGES+=("$session_id")
        fi
    else
        # No diff - check for message
        echo "   📭 Category: NO_CHANGES"
        NO_CHANGES+=("$session_id")
        
        # Try to extract any message from the output
        if echo "$PULL_OUTPUT" | grep -qi "no changes\|nothing to apply\|empty"; then
            echo "   Message: No changes were made by Jules"
        elif echo "$PULL_OUTPUT" | grep -qi "error\|failed"; then
            echo "   ⚠️  Message: Session may have encountered an error"
            echo "$PULL_OUTPUT" | grep -i "error\|failed" | head -3 | sed 's/^/      /'
        else
            # Show first few lines of output for context
            echo "   Output preview:"
            echo "$PULL_OUTPUT" | head -5 | sed 's/^/      /'
        fi
    fi
    echo ""
done

# Summary
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📊 SUMMARY"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "✅ Reports Only (${#REPORTS_ONLY[@]} sessions):"
for sid in "${REPORTS_ONLY[@]:-}"; do
    [[ -n "$sid" ]] && echo "   - $sid"
done
[[ ${#REPORTS_ONLY[@]} -eq 0 ]] && echo "   (none)"

echo ""
echo "⚠️  Code Changes (${#CODE_CHANGES[@]} sessions - needs review):"
for sid in "${CODE_CHANGES[@]:-}"; do
    [[ -n "$sid" ]] && echo "   - $sid"
done
[[ ${#CODE_CHANGES[@]} -eq 0 ]] && echo "   (none)"

echo ""
echo "📭 No Changes (${#NO_CHANGES[@]} sessions):"
for sid in "${NO_CHANGES[@]:-}"; do
    [[ -n "$sid" ]] && echo "   - $sid"
done
[[ ${#NO_CHANGES[@]} -eq 0 ]] && echo "   (none)"

echo ""
if ! $AUTO_APPLY && [[ ${#REPORTS_ONLY[@]} -gt 0 ]]; then
    echo "To auto-apply reports-only sessions, run:"
    echo "   ./scripts/review_jules_sessions.sh --apply"
fi
