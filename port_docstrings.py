import os
import re

DIFF_PATH = ".agent/reports/jules_diffs/2026-01-21/15718507772184055229/changes.diff"
PROJECT_ROOT = "/Users/mar/Projects/pylabpraxis"

FILE_MAPPING = {
  "praxis/backend/models/orm/asset.py": "praxis/backend/models/domain/asset.py",
  "praxis/backend/models/orm/deck.py": "praxis/backend/models/domain/deck.py",
  "praxis/backend/models/orm/machine.py": "praxis/backend/models/domain/machine.py",
  "praxis/backend/models/orm/outputs.py": "praxis/backend/models/domain/outputs.py",
  "praxis/backend/models/orm/plr_sync.py": "praxis/backend/models/domain/plr_sync.py",
  "praxis/backend/models/orm/protocol.py": "praxis/backend/models/domain/protocol.py",
  "praxis/backend/models/orm/resource.py": "praxis/backend/models/domain/resource.py",
  "praxis/backend/models/orm/schedule.py": "praxis/backend/models/domain/schedule.py",
  "praxis/backend/models/orm/user.py": "praxis/backend/models/domain/user.py",
  "praxis/backend/models/orm/workcell.py": "praxis/backend/models/domain/workcell.py",
}

CLASS_MAPPING = {
  "AssetOrm": "Asset",
  "DeckOrm": "Deck",
  "DeckDefinitionOrm": "DeckDefinition",
  "MachineOrm": "Machine",
  "MachineDefinitionOrm": "MachineDefinition",
  "ResourceOrm": "Resource",
  "ResourceDefinitionOrm": "ResourceDefinition",
  "ProtocolRunOrm": "ProtocolRun",
  "ProtocolDefinitionOrm": "ProtocolDefinition",
  "WorkcellOrm": "Workcell",
  "UserOrm": "User",
  "ScheduleOrm": "Schedule",
}


def load_diff():
  with open(DIFF_PATH, "r") as f:
    return f.read()


def parse_diff(diff_content):
  files = {}
  current_file = None
  current_hunks = []

  lines = diff_content.splitlines()
  i = 0
  while i < len(lines):
    line = lines[i]
    if line.startswith("diff --git"):
      if current_file:
        files[current_file] = current_hunks

      # Extract file path
      match = re.search(r"a/(.+) b/", line)
      if match:
        current_file = match.group(1)
        current_hunks = []
      i += 1
    elif line.startswith("@@"):
      hunk_content = [line]
      i += 1
      while (
        i < len(lines) and not lines[i].startswith("@@") and not lines[i].startswith("diff --git")
      ):
        hunk_content.append(lines[i])
        i += 1
      current_hunks.append(hunk_content)
    else:
      i += 1

  if current_file:
    files[current_file] = current_hunks
  return files


def extract_docstring_fix(hunk):
  # Search for docstring addition in hunk
  doc_lines = []
  in_doc = False

  # We look for lines starting with + and containing """ or starting with + and being inside """
  # But wait, Jules often modifies existing docstrings or adding new ones.
  # We want to catch the whole docstring block.

  # Simple heuristic: find the class/def line in the context (often the @@ line or first lines)
  # Then find the + lines that look like a docstring.

  target_class = None
  for line in hunk:
    if line.startswith(" class ") or "class " in line and line.strip().endswith(":"):
      match = re.search(r"class\s+(\w+)", line)
      if match:
        target_class = match.group(1)
    elif line.startswith(" def ") or "def " in line and line.strip().endswith(":"):
      match = re.search(r"def\s+(\w+)", line)
      if match:
        target_class = match.group(1)  # Using target_class for def name too

  # Extract the full docstring from the + lines
  addition_lines = [line[1:] for line in hunk if line.startswith("+")]

  # Look for """ block in addition_lines
  docstring = ""
  start_idx = -1
  for idx, line in enumerate(addition_lines):
    if '"""' in line:
      if start_idx == -1:
        start_idx = idx
        # If it's a single line docstring """..."""
        if line.count('"""') >= 2:
          return target_class, line.strip()
      else:
        # End of block
        docstring = "\n".join(addition_lines[start_idx : idx + 1])
        return target_class, docstring.strip()

  return target_class, None


def apply_to_file(rel_path, class_name, new_docstring):
  if not new_docstring or not class_name:
    return False

  # Map class name if needed
  target_class = CLASS_MAPPING.get(class_name, class_name)

  # Special case: if class_name ends with Orm, and we didn't find a mapping, try stripping Orm
  if target_class == class_name and class_name.endswith("Orm"):
    target_class = class_name[:-3]

  abs_path = os.path.join(PROJECT_ROOT, rel_path)
  if not os.path.exists(abs_path):
    # Try mapped path
    mapped_path = None
    for old, new in FILE_MAPPING.items():
      if rel_path == old:
        mapped_path = new
        break
    if mapped_path:
      abs_path = os.path.join(PROJECT_ROOT, mapped_path)
    else:
      return False

  if not os.path.exists(abs_path):
    return False

  with open(abs_path, "r") as f:
    content = f.read()

  # Find the class/def line
  # Regex to find class/def and its current docstring
  # We want to match: class TargetClass(...): \n [optional whitespace] """ current docstring """

  pattern = rf"(class\s+{target_class}\b[^:]*:|def\s+{target_class}\b[^:]*:)"
  match = re.search(pattern, content)
  if not match:
    return False

  start_pos = match.end()

  # Look for existing docstring after the match
  # Skip any newlines/whitespace
  sub_content = content[start_pos:]
  doc_match = re.search(r'^\s*("""[\s\S]*?""")', sub_content)

  # Indentation: use the indentation of the existing docstring if it exists, else 2 spaces
  indent = "  "
  if doc_match:
    # Get indentation from the matched docstring
    full_match = doc_match.group(0)
    leading_ws = re.match(r"^\s*", full_match).group(0)
    if "\n" in leading_ws:
      indent = leading_ws.split("\n")[-1]
    else:
      indent = leading_ws

    # Replace existing docstring
    new_content = (
      content[:start_pos]
      + sub_content[: doc_match.start()]
      + "\n"
      + indent
      + new_docstring
      + sub_content[doc_match.end() :]
    )
  else:
    # Insert after class/def line
    # Check if there is already a newline
    new_content = content[:start_pos] + "\n" + indent + new_docstring + content[start_pos:]

  with open(abs_path, "w") as f:
    f.write(new_content)
  return True


def main():
  diff_content = load_diff()
  parsed_files = parse_diff(diff_content)

  modified_count = 0
  for rel_path, hunks in parsed_files.items():
    print(f"Checking {rel_path}")
    for hunk in hunks:
      target, docstring = extract_docstring_fix(hunk)
      if target and docstring:
        print(f"  Found docstring for {target}")
        if apply_to_file(rel_path, target, docstring):
          print(f"    Applied docstring to {target}")
          modified_count += 1
        else:
          print(f"    Failed to apply docstring to {target}")

  print(f"Total modified: {modified_count}")


if __name__ == "__main__":
  main()
