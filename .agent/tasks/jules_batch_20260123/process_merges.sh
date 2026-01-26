#!/bin/bash
set -e

SCRIPT_DIR=".agent/tasks/jules_batch_20260123/scripts"

echo "=== Processing Merges ==="

# Merge SPLIT-01
# Note: Test scope 'src/app/features/run-protocol' covers the split components
$SCRIPT_DIR/verify_and_merge.sh "split-run-proto" "--include=src/app/features/run-protocol"

# Merge REFACTOR-01
# Note: Test scope 'src/app/core' covers the core service changes
$SCRIPT_DIR/verify_and_merge.sh "refactor-core" "--include=src/app/core"

echo "All merges processed."
