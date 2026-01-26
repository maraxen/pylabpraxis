#!/bin/bash
set -e

SCRIPT_DIR=".agent/tasks/jules_batch_20260123/scripts"

# Batch 1: Infrastructure (Direct Apply)
echo "=== Batch 1: Infrastructure ==="
$SCRIPT_DIR/apply_task.sh "JLITE-03" "14542845870678146245"
$SCRIPT_DIR/apply_task.sh "OPFS-03" "14808794888910746056"

# Batch 4: Refactor (Direct Apply - check for conflicts manually if needed, but assuming safe)
echo "=== Batch 4: Refactor ==="
# $SCRIPT_DIR/apply_task.sh "REFACTOR-01" "235373965227071886"  # Commented out to do one by one if preferred
$SCRIPT_DIR/apply_task.sh "REFACTOR-02" "3806881592450903343"
$SCRIPT_DIR/apply_task.sh "REFACTOR-03" "13019827227538808257"

# Batch 5: Split (Worktrees)
echo "=== Batch 5: Split (Worktrees) ==="
$SCRIPT_DIR/setup_worktree.sh "SPLIT-01" "9828431918057321321" "split-run-proto"
$SCRIPT_DIR/setup_worktree.sh "SPLIT-02" "1174395877673969907" "split-playground"
$SCRIPT_DIR/setup_worktree.sh "SPLIT-04" "8806860709165683043" "split-scheduler"
$SCRIPT_DIR/setup_worktree.sh "SPLIT-05" "7027017935549180084" "split-plr"
$SCRIPT_DIR/setup_worktree.sh "SPLIT-06" "2939224647793981217" "split-rsrc"

echo "All batches processed."
