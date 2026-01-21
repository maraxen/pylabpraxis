#!/usr/bin/env python3
"""Submit pending Jules dispatches from the agent database."""
import sqlite3
import subprocess
import tempfile
import time
import os

DB_PATH = "/Users/mar/Projects/pylabpraxis/.agent/agent.db"

def get_pending_dispatches():
    """Get all pending Jules dispatches."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, prompt_full 
        FROM dispatches 
        WHERE target = 'jules' AND status = 'pending' 
        ORDER BY created_at ASC
    """)
    dispatches = cursor.fetchall()
    conn.close()
    return dispatches

def update_dispatch_status(dispatch_id: str, status: str, jules_session_id: str = None):
    """Update dispatch status in database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    if jules_session_id:
        cursor.execute("""
            UPDATE dispatches 
            SET status = ?, claimed_at = datetime('now'), claimed_by = ?
            WHERE id = ?
        """, (status, f"jules:{jules_session_id}", dispatch_id))
    else:
        cursor.execute("""
            UPDATE dispatches 
            SET status = ?, claimed_at = datetime('now')
            WHERE id = ?
        """, (status, dispatch_id))
    conn.commit()
    conn.close()

def submit_to_jules(prompt: str) -> tuple[bool, str]:
    """Submit a prompt to Jules via CLI."""
    try:
        result = subprocess.run(
            ["jules", "remote", "new", "--session", prompt],
            capture_output=True,
            text=True,
            timeout=60,
            cwd="/Users/mar/Projects/pylabpraxis"
        )
        
        output = result.stdout + result.stderr
        
        # Extract session ID from output
        session_id = None
        for line in output.split('\n'):
            if line.startswith('ID:'):
                session_id = line.split(':')[1].strip()
                break
        
        if result.returncode == 0 and 'Session is created' in output:
            return True, session_id or "unknown"
        else:
            return False, output
    except subprocess.TimeoutExpired:
        return False, "timeout"
    except Exception as e:
        return False, str(e)

def main():
    dispatches = get_pending_dispatches()
    print(f"Found {len(dispatches)} pending Jules dispatches")
    print("=" * 60)
    
    success_count = 0
    fail_count = 0
    
    for dispatch_id, prompt in dispatches:
        print(f"\n[{dispatch_id}] Submitting...")
        
        success, result = submit_to_jules(prompt)
        
        if success:
            print(f"✓ Success! Jules session: {result}")
            update_dispatch_status(dispatch_id, "running", result)
            success_count += 1
        else:
            print(f"✗ Failed: {result[:200]}...")
            update_dispatch_status(dispatch_id, "failed")
            fail_count += 1
        
        # Rate limiting
        time.sleep(3)
    
    print("\n" + "=" * 60)
    print(f"Done! Success: {success_count}, Failed: {fail_count}")
    print("Check: jules remote list --session")

if __name__ == "__main__":
    main()
