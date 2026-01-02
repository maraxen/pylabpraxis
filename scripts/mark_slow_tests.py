#!/usr/bin/env python3
"""Script to identify and mark slow tests (>1 second) with @pytest.mark.slow.

This script should be run after executing the full test suite with:
    uv run pytest --durations=0 --json-report --json-report-file=test_durations.json

Or to generate a simple duration report:
    uv run pytest --durations=0 -v > test_durations.txt

Then run this script to identify tests that should be marked as slow.
"""

import re
import subprocess
import sys
from pathlib import Path


def find_slow_tests_from_pytest(threshold_seconds: float = 1.0) -> dict[str, float]:
  """Run pytest and capture slow tests.

  Args:
      threshold_seconds: Minimum duration in seconds to consider a test slow

  Returns:
      Dictionary mapping test file paths to their durations

  """
  # Run pytest with durations=0 to get all test timings
  cmd = ["uv", "run", "pytest", "--durations=0", "-v", "--tb=no", "--no-cov"]

  result = subprocess.run(
    cmd,
    check=False, capture_output=True,
    text=True,
    timeout=600,  # 10 minute timeout
  )

  # Parse output for test durations
  slow_tests = {}
  duration_pattern = r"([\d.]+)s\s+(call|setup|teardown)\s+(.+)"

  for line in result.stdout.split("\n"):
    match = re.search(duration_pattern, line)
    if match:
      duration = float(match.group(1))
      test_path = match.group(3)

      if duration >= threshold_seconds:
        # Extract file path from test path
        if "::" in test_path:
          file_path = test_path.split("::")[0]
          if file_path not in slow_tests or slow_tests[file_path] < duration:
            slow_tests[file_path] = duration

  return slow_tests


def check_if_marked_slow(file_path: Path) -> bool:
  """Check if a test file already has @pytest.mark.slow decorators."""
  if not file_path.exists():
    return False

  content = file_path.read_text()
  return "@pytest.mark.slow" in content or "mark.slow" in content


def add_slow_marker_to_file(file_path: Path, dry_run: bool = True) -> None:
  """Add @pytest.mark.slow to test functions in a file.

  Args:
      file_path: Path to test file
      dry_run: If True, only print what would be done

  """
  if not file_path.exists():
    return

  content = file_path.read_text()

  # Check if already has pytest import

  # Pattern to match test functions (async or sync)

  lines = content.split("\n")
  modified_lines = []
  modified = False

  for i, line in enumerate(lines):
    # Check if this is a test function definition
    if re.match(r"^\s*(async\s+)?def\s+test_", line):
      # Check if the previous line already has @pytest.mark.slow
      if i > 0 and "@pytest.mark.slow" in lines[i - 1]:
        modified_lines.append(line)
        continue

      # Add the marker before the function
      indent = len(line) - len(line.lstrip())
      marker = " " * indent + "@pytest.mark.slow"
      modified_lines.append(marker)
      modified = True

    modified_lines.append(line)

  if not modified:
    return

  if dry_run:
    pass
  else:
    new_content = "\n".join(modified_lines)
    file_path.write_text(new_content)


def main():
  """Main entry point."""
  import argparse

  parser = argparse.ArgumentParser(description="Identify and mark slow tests")
  parser.add_argument(
    "--threshold",
    type=float,
    default=1.0,
    help="Minimum duration in seconds to consider a test slow (default: 1.0)",
  )
  parser.add_argument(
    "--apply",
    action="store_true",
    help="Actually modify files (default is dry-run)",
  )
  parser.add_argument(
    "--manual",
    action="store_true",
    help="Skip pytest run and manually specify test files to mark",
  )
  parser.add_argument(
    "files",
    nargs="*",
    help="Test files to mark as slow (for --manual mode)",
  )

  args = parser.parse_args()

  root = Path(__file__).parent.parent
  tests_dir = root / "tests"

  if args.manual:
    # Manual mode: user specifies which files to mark
    if not args.files:
      sys.exit(1)

    for file_path_str in args.files:
      file_path = Path(file_path_str)
      if not file_path.is_absolute():
        file_path = tests_dir / file_path

      add_slow_marker_to_file(file_path, dry_run=not args.apply)

  else:
    # Automatic mode: run pytest to find slow tests

    try:
      slow_tests = find_slow_tests_from_pytest(args.threshold)
    except subprocess.TimeoutExpired:
      sys.exit(1)
    except Exception:
      sys.exit(1)

    if not slow_tests:
      sys.exit(0)


    for file_path_str, _duration in sorted(
      slow_tests.items(),
      key=lambda x: x[1],
      reverse=True,
    ):
      file_path = Path(file_path_str)
      if not file_path.is_absolute():
        file_path = tests_dir / file_path


      if check_if_marked_slow(file_path):
        pass
      else:
        add_slow_marker_to_file(file_path, dry_run=not args.apply)

  if not args.apply:
    pass


if __name__ == "__main__":
  main()
