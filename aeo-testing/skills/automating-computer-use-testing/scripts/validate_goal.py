#!/usr/bin/env python3
"""Validates Gemini computer-use goal files for structural correctness.

Usage:
    python validate_goal.py <path_to_goal_file>

Checks:
- File exists and is readable
- Contains role description ("You are...")
- Contains goal statement ("Your goal is...")
- Has numbered test steps
- Defines success criteria
- Includes reporting structure
"""

import sys
from pathlib import Path


def validate_goal_file(file_path: Path) -> tuple[bool, list[str]]:
    """Validate goal file structure.

    Returns:
        (is_valid, errors) - Tuple of validation status and list of error messages
    """
    errors = []

    # Check file exists
    if not file_path.exists():
        errors.append(f"File not found: {file_path}")
        return False, errors

    # Read file content
    try:
        content = file_path.read_text(encoding="utf-8")
    except Exception as e:
        errors.append(f"Failed to read file: {e}")
        return False, errors

    # Check for role description
    if not ("You are" in content or "you are" in content):
        errors.append("Missing role description (expected 'You are...')")

    # Check for goal statement
    if not ("Your goal is" in content or "your goal is" in content):
        errors.append("Missing goal statement (expected 'Your goal is...')")

    # Check for test steps (numbered list)
    numbered_steps = [line for line in content.split('\n')
                      if line.strip() and line.strip()[0].isdigit() and '.' in line[:5]]
    if len(numbered_steps) < 3:
        errors.append(f"Insufficient test steps (found {len(numbered_steps)}, expected at least 3)")

    # Check for success criteria
    if not ("Success Criteria" in content or "success criteria" in content):
        errors.append("Missing success criteria section")

    # Check for reporting structure
    if not ("Reporting" in content or "reporting" in content or "Report" in content):
        errors.append("Missing reporting section")

    # Check for specific reporting elements
    if "What worked" not in content and "what worked" not in content:
        errors.append("Missing 'What worked' in reporting section")

    if "What broke" not in content and "what broke" not in content:
        errors.append("Missing 'What broke' in reporting section")

    # Validate file length (should have substantial content)
    if len(content) < 500:
        errors.append(f"Goal file too short ({len(content)} chars, expected at least 500)")

    is_valid = len(errors) == 0
    return is_valid, errors


def main():
    if len(sys.argv) != 2:
        print("Usage: python validate_goal.py <path_to_goal_file>")
        sys.exit(1)

    file_path = Path(sys.argv[1])
    is_valid, errors = validate_goal_file(file_path)

    if is_valid:
        print(f"✓ Goal file is valid: {file_path}")
        sys.exit(0)
    else:
        print(f"✗ Goal file validation failed: {file_path}")
        for error in errors:
            print(f"  - {error}")
        sys.exit(1)


if __name__ == "__main__":
    main()
