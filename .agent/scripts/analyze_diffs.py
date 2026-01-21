#!/usr/bin/env python3
import os
import json
from collections import defaultdict

session_ids = [
    "18100194563593856842", "7833557422181935314", "7169150082809541249", "8053431069385739941",
    "17528057938872959418", "693011006660131583", "5758405153110470721", "2946937954468200048",
    "15023855711672891138", "9868075249617187364", "1955602947950537137", "15033366457735355048",
    "16249831400007417250", "12822272099245934316", "12408408457884280509", "5772657439955006749",
    "16235462376134233538", "2357822123779432063", "7588975548984364060", "4091292972154822687",
    "18333554910223635761", "17486039806276221924", "7966319430585451351", "9570037443858871469",
    "9326114167496894643", "954639313672326160", "15718507772184055229", "11789340521090048069",
    "2675599457561484882", "14904239789534326926", "11930790793989115694", "10964805792793165164"
]

base_dir = ".agent/reports/jules_diffs/2026-01-21"
file_map = defaultdict(list)
sessions_data = []

# Ensure base_dir is absolute if running from elsewhere, assuming CWD is project root
cwd = os.getcwd()
base_path = os.path.join(cwd, base_dir)

for sid in session_ids:
    s_dir = os.path.join(base_path, sid)
    
    # Metadata
    meta_path = os.path.join(s_dir, "metadata.json")
    try:
        with open(meta_path, 'r') as f:
            meta = json.load(f)
            task_name = meta.get("task_name", "Unknown Task").split("**")[0].replace("## Task: ", "").strip()
    except FileNotFoundError:
        task_name = "Unknown Task"
        
    # Files
    files_path = os.path.join(s_dir, "files_changed.txt")
    files = []
    if os.path.exists(files_path):
        with open(files_path, 'r') as f:
            files = [line.strip() for line in f if line.strip()]
            
    for file in files:
        file_map[file].append(sid)

    # Diff Analysis
    diff_path = os.path.join(s_dir, "changes.diff")
    diff_content = ""
    has_conflict_markers = False
    is_scaffold = False
    if os.path.exists(diff_path):
        with open(diff_path, 'r') as f:
            diff_content = f.read()
            if "<<<<" in diff_content and "====" in diff_content:
                has_conflict_markers = True
            if "TODO: Implement" in diff_content or "pass  # TODO" in diff_content:
                is_scaffold = True

    sessions_data.append({
        "id": sid,
        "task": task_name,
        "files": files,
        "conflict_markers": has_conflict_markers,
        "is_scaffold": is_scaffold,
        "diff_len": len(diff_content)
    })

# Output Report
print("# Analysis Report\n")

print("## File Conflicts (Multiple Sessions Touching Same File)")
for file, sids in file_map.items():
    if len(sids) > 1:
        print(f"- **{file}**")
        for sid in sids:
            task = next((s['task'] for s in sessions_data if s['id'] == sid), "Unknown")
            print(f"  - {sid}: {task}")

print("\n## Session Details")
for s in sessions_data:
    print(f"### {s['task']} ({s['id']})")
    print(f"- Files: {len(s['files'])}")
    print(f"- Conflict Markers: {s['conflict_markers']}")
    print(f"- Is Scaffold: {s['is_scaffold']}")
    print(f"- Files List: {', '.join(s['files'][:5])}{'...' if len(s['files']) > 5 else ''}")
    print("")
