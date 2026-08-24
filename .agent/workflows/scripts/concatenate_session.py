#!/usr/bin/env python3
import os
import sys
import argparse
from pathlib import Path

def extract_session(uuid, output_file=None):
    brain_root = Path("~/.gemini/antigravity/brain").expanduser()
    brain_dir = brain_root / uuid
    
    if not brain_dir.exists():
        print(f"Error: Brain directory {brain_dir} not found.")
        sys.exit(1)

    sections = {
        "turns": [],
        "main": [],
        "all": []
    }

    # Section 1: Conversation Turns (Thinking Steps)
    steps_dir = brain_dir / ".system_generated" / "steps"
    if steps_dir.exists():
        # Step directories are numeric, sort them numerically
        step_paths = sorted(
            [d for d in steps_dir.iterdir() if d.is_dir()],
            key=lambda x: int(x.name) if x.name.isdigit() else 999999
        )
        
        for step in step_paths:
            content_file = step / "content.md"
            output_file_txt = step / "output.txt"
            
            step_header = f"### Step {step.name}"
            step_content = ""
            
            if content_file.exists():
                step_content += content_file.read_text(errors='ignore') + "\n"
            
            if output_file_txt.exists():
                output_val = output_file_txt.read_text(errors='ignore')
                if output_val.strip():
                    step_content += "\n#### Tool Output\n```\n" + output_val + "\n```\n"
            
            if step_content:
                sections["turns"].append(f"{step_header}\n{step_content}")

    # Section 2: Main Artifacts
    main_files = ["implementation_plan.md", "task.md", "walkthrough.md"]
    for f_name in main_files:
        f_path = brain_dir / f_name
        if f_path.exists():
            content = f_path.read_text(errors='ignore')
            sections["main"].append(f"### {f_name}\n\n{content}")

    # Section 3: All Artifacts (Metadata, Versions, etc.)
    # Iterate through ALL files in the directory
    all_files = sorted([f for f in brain_dir.iterdir() if f.is_file()])
    for f in all_files:
        content = f.read_text(errors='ignore')
        sections["all"].append(f"### {f.name}\n\n```markdown\n{content}\n```")

    # Construct Final Output
    output_lines = [f"# Session History Archive: {uuid}\n"]
    
    output_lines.append("## [1] Conversation Turns\n")
    if sections["turns"]:
        output_lines.extend(sections["turns"])
    else:
        output_lines.append("_No internal step logs found._\n")

    output_lines.append("\n---\n## [2] Main Artifacts\n")
    if sections["main"]:
        output_lines.extend(sections["main"])
    else:
        output_lines.append("_No primary artifacts found._\n")

    output_lines.append("\n---\n## [3] All Artifacts (Metadata & History)\n")
    if sections["all"]:
        output_lines.extend(sections["all"])
    else:
        output_lines.append("_No files found in brain directory._\n")

    # Determine Output Path
    if not output_file:
        archives_dir = Path("eph/session-archives")
        archives_dir.mkdir(parents=True, exist_ok=True)
        # Using project name to make it easier to identify
        project_name = Path.cwd().name
        output_file = archives_dir / f"{project_name}-{uuid}.md"
    else:
        output_file = Path(output_file)

    output_file.write_text("\n".join(output_lines))
    print(f"Successfully archived session to: {output_file}")

def main():
    parser = argparse.ArgumentParser(description="Extract a complete session archive from an Antigravity UUID.")
    parser.add_argument("uuid", help="The 36-character conversation UUID")
    parser.add_argument("--output", "-o", help="Explicit output file path")

    args = parser.parse_args()
    
    extract_session(args.uuid, args.output)

if __name__ == "__main__":
    main()
