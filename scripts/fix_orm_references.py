#!/usr/bin/env python3
"""Script to fix all remaining XOrm references in the codebase.

This script:
1. Finds all files with XOrm references
2. Replaces XOrm with X in type hints, variable names, and imports
3. Updates imports from praxis.backend.models.orm to praxis.backend.models.domain
"""

import re
from pathlib import Path
from typing import Dict, List, Tuple

# Mapping of Orm names to domain names
ORM_TO_DOMAIN: Dict[str, str] = {
    "Asset": "Asset",
    "Deck": "Deck",
    "DeckDefinition": "DeckDefinition",
    "DeckPositionDefinition": "DeckPositionDefinition",
    "Machine": "Machine",
    "MachineDefinition": "MachineDefinition",
    "Resource": "Resource",
    "ResourceDefinition": "ResourceDefinition",
    "ProtocolRun": "ProtocolRun",
    "FunctionProtocolDefinition": "FunctionProtocolDefinition",
    "ParameterDefinition": "ParameterDefinition",
    "AssetRequirement": "AssetRequirement",
    "FunctionCallLog": "FunctionCallLog",
    "FunctionDataOutput": "FunctionDataOutput",
    "WellDataOutput": "WellDataOutput",
    "ScheduleEntry": "ScheduleEntry",
    "AssetReservation": "AssetReservation",
    "ScheduleHistory": "ScheduleHistory",
    "User": "User",
    "Workcell": "Workcell",
    "ProtocolSourceRepository": "ProtocolSourceRepository",
    "FileSystemProtocolSource": "FileSystemProtocolSource",
    "StateResolutionLog": "StateResolutionLog",
}


def find_files_with_orm_references(base_path: Path) -> List[Path]:
    """Find all Python files with ORM references in restricted directories."""
    files_with_orm = []
    
    # Only search in praxis/ and tests/ by default if path is .
    search_dirs = [base_path]
    if str(base_path) == ".":
        search_dirs = [Path("praxis"), Path("tests")]
    
    for search_dir in search_dirs:
        if not search_dir.exists():
            continue
            
        for file_path in search_dir.glob("**/*.py"):
            if "__pycache__" in str(file_path):
                continue

            try:
                content = file_path.read_text()
                # Check for XOrm naming or orm imports
                if re.search(r'\b\w+Orm\b', content) or "praxis.backend.models.orm" in content:
                    files_with_orm.append(file_path)
            except Exception as e:
                print(f"Error reading {file_path}: {e}")

    return files_with_orm


def fix_imports(content: str) -> str:
    """Fix imports from praxis.backend.models.orm to domain."""
    # Pattern: from praxis.backend.models.orm[.submodule] import ...
    pattern = r'from praxis\.backend\.models\.orm(?:\.\w+)? import \('
    replacement = r'from praxis.backend.models.domain import ('
    content = re.sub(pattern, replacement, content)

    # Single line imports
    pattern = r'from praxis\.backend\.models\.orm(?:\.\w+)? import ([^(].*?)$'
    replacement = r'from praxis.backend.models.domain import \1'
    content = re.sub(pattern, replacement, content, flags=re.MULTILINE)

    return content


def replace_orm_names(content: str) -> str:
    """Replace all XOrm references with X."""
    for model_name, domain_name in ORM_TO_DOMAIN.items():
        # Replace as whole words only (not part of other identifiers)
        pattern = r'\b' + re.escape(model_name) + r'\b'
        content = re.sub(pattern, domain_name, content)

    # General replacements for variable names and methods
    content = re.sub(r'(\w)_orm\b', r'\1_model', content)
    content = re.sub(r'\borm_(\w)', r'model_\1', content)
    # Handle CamelCase names where Orm is a suffix or part of name
    content = re.sub(r'([a-z])Orm([A-Z])', r'\1Model\2', content)
    content = re.sub(r'([a-z])Orm\b', r'\1Model', content)

    return content


def process_file(file_path: Path, dry_run: bool = False) -> Tuple[bool, str]:
    """Process a single file to fix XOrm references.

    Returns:
        (changed, message) tuple
    """
    try:
        original_content = file_path.read_text()
        content = original_content

        # Fix imports
        content = fix_imports(content)

        # Replace XOrm names
        content = replace_orm_names(content)

        if content != original_content:
            if not dry_run:
                file_path.write_text(content)
            return True, f"✓ Modified: {file_path}"
        else:
            return False, f"  Skipped: {file_path} (no changes needed)"

    except Exception as e:
        return False, f"✗ Error processing {file_path}: {e}"


def main():
    """Main function to fix all XOrm references."""
    import argparse

    parser = argparse.ArgumentParser(description="Fix XOrm references in codebase")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be changed without modifying files"
    )
    parser.add_argument(
        "--path",
        type=Path,
        default=Path("."),
        help="Base path to search for files (default: . - searches praxis/ and tests/)"
    )

    args = parser.parse_args()

    print(f"Scanning for files with XOrm references in {args.path}...")
    files = find_files_with_orm_references(args.path)

    if not files:
        print("No files with XOrm references found!")
        return

    print(f"Found {len(files)} files with XOrm references")

    if args.dry_run:
        print("\n=== DRY RUN MODE (no files will be modified) ===\n")

    modified_count = 0
    for file_path in sorted(files):
        changed, message = process_file(file_path, dry_run=args.dry_run)
        print(message)
        if changed:
            modified_count += 1

    print(f"\n{'Would modify' if args.dry_run else 'Modified'} {modified_count} files")

    if args.dry_run:
        print("\nRun without --dry-run to apply changes")


if __name__ == "__main__":
    main()
