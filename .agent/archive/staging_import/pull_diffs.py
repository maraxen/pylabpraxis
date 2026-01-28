import re
import subprocess
import os

TRACKING_FILE = "/Users/mar/Projects/praxis/.agent/tasks/jules_batch_20260123/SESSION_TRACKING.md"
STAGING_DIR = ".agent/staging"


def parse_tracking_file(file_path):
  sessions = []
  with open(file_path, "r") as f:
    lines = f.readlines()

  # Simple table parsing
  for line in lines:
    line = line.strip()
    if not line.startswith("|") or "---" in line or "Task ID" in line:
      continue

    parts = [p.strip() for p in line.split("|")]
    if len(parts) < 6:
      continue

    task_id = parts[1]
    session_id_raw = parts[2]
    status = parts[3]
    recommendation = parts[4]

    session_id = session_id_raw.replace("`", "")

    item = {
      "task_id": task_id,
      "session_id": session_id,
      "status": status,
      "recommendation": recommendation,
    }

    should_pull = False
    is_completed = "Completed" in status
    is_planning = "Awaiting Plan Approval" in status
    is_discard = (
      "Discard" in recommendation or "Obsolete" in recommendation or "Skip" in recommendation
    )

    if (is_completed or is_planning) and not is_discard:
      should_pull = True

    if should_pull:
      sessions.append(item)

  return sessions


def pull_session(session, output_dir):
  task_id = session["task_id"]
  sid = session["session_id"]
  target_file = os.path.join(output_dir, f"{task_id}.md")

  print(f"Pulling {task_id} ({sid})...")

  cmd = ["jules", "remote", "pull", "--session", sid]

  try:
    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    content = result.stdout

    if not content.strip():
      print(f"WARNING: No content for {task_id}")
      return

    with open(target_file, "w") as f:
      header = f"---\ntask_id: {task_id}\nsession_id: {sid}\nstatus: {session['status']}\n---\n\n"
      f.write(header + content)
    print(f"Saved to {target_file}")

  except subprocess.CalledProcessError as e:
    print(f"ERROR pulling {task_id}: {e}")
    print(e.stderr)


def main():
  if not os.path.exists(STAGING_DIR):
    os.makedirs(STAGING_DIR)

  sessions = parse_tracking_file(TRACKING_FILE)
  print(f"Found {len(sessions)} sessions to pull.")

  for sess in sessions:
    pull_session(sess, STAGING_DIR)


if __name__ == "__main__":
  main()
