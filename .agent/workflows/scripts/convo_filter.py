#!/usr/bin/env python3
import os
import sys
import json
import argparse
from datetime import datetime, timedelta
from pathlib import Path

def get_workspace_info():
    cwd = Path.cwd()
    return cwd.name, str(cwd)

def find_conversations(brain_root, workspace_name, query=None, since_days=2, limit=50):
    brain_path = Path(brain_root).expanduser()
    if not brain_path.exists():
        print(f"Error: Brain path {brain_path} not found.")
        return []

    matches = []
    threshold_date = datetime.now() - timedelta(days=since_days)

    # List all brain directories sorted by mtime (most recent first)
    dirs = sorted(
        [d for d in brain_path.iterdir() if d.is_dir() and len(d.name) == 36],
        key=lambda x: x.stat().st_mtime,
        reverse=True
    )

    for d in dirs[:limit]:
        mtime = datetime.fromtimestamp(d.stat().st_mtime)
        
        # Artifact check for workspace relevance
        is_relevant = False
        title = "Unknown Conversation"
        
        # Check any .md files for relevance and title
        md_files = list(d.glob("*.md"))
        if md_files:
            # If any .md exists, it's potentially relevant
            if workspace_name.lower() == "all":
                is_relevant = True
            
            for md_path in md_files:
                content = md_path.read_text(errors='ignore')
                if workspace_name.lower() in content.lower():
                    is_relevant = True
                
                # Extract first H1 as title if not already found
                if title == "Unknown Conversation":
                    for line in content.splitlines():
                        if line.startswith("# "):
                            title = line[2:].strip()
                            break
                if is_relevant and title != "Unknown Conversation":
                    break

        # Filter by Query if provided
        if query and query.lower() not in title.lower() and query.lower() not in d.name.lower():
            continue

        # Default recency filter (unless explicitly searching)
        if not query and mtime < threshold_date and len(matches) >= 2:
            continue

        if is_relevant or query or workspace_name.lower() == "all":
            matches.append({
                "uuid": d.name,
                "title": title,
                "updated": mtime.strftime("%Y-%m-%d %H:%M:%S"),
                "path": str(d)
            })

    return matches

def main():
    parser = argparse.ArgumentParser(description="Filter Antigravity conversations by workspace and keywords.")
    parser.add_argument("--query", "-q", help="Fuzzy search query for title or UUID")
    parser.add_argument("--since", "-s", type=int, default=2, help="Days to look back (default 2)")
    parser.add_argument("--limit", "-l", type=int, default=50, help="Max directories to scan")
    parser.add_argument("--workspace", "-w", help="Override inferred workspace name")
    parser.add_argument("--all", action="store_true", help="List all conversations regardless of workspace")
    parser.add_argument("--json", action="store_true", help="Output JSON format")
    parser.add_argument("--latest", action="store_true", help="Output only the most recent UUID")

    args = parser.parse_args()

    ws_name, ws_path = get_workspace_info()
    target_ws = "all" if args.all else (args.workspace if args.workspace else ws_name)

    brain_root = "~/.gemini/antigravity/brain"
    results = find_conversations(brain_root, target_ws, args.query, args.since, args.limit)

    if args.latest:
        if results:
            print(results[0]["uuid"])
        return

    if args.json:
        print(json.dumps(results, indent=2))
    else:
        if not results:
            print(f"No matching sessions found for workspace '{target_ws}'.")
            return
        
        print(f"{'UUID':<38} | {'Updated':<19} | {'Title'}")
        print("-" * 80)
        for r in results:
            print(f"{r['uuid']:<38} | {r['updated']:<19} | {r['title']}")

if __name__ == "__main__":
    main()
