#!/usr/bin/env python3
"""
init_skill.py - Initialize a new Claude skill with proper structure.

This script scaffolds a new skill following best practices from SKILL.md.
Reference: See ../SKILL.md for complete skill creation guidance.

Usage:
    python init_skill.py <skill-name> [--path <output-dir>] [--with-scripts] [--with-references]

Examples:
    python init_skill.py my-skill
    python init_skill.py processing-pdfs --path ./skills --with-scripts
    python init_skill.py analyzing-data --with-references
"""

import argparse
import os
import re
import sys
from pathlib import Path
from typing import Optional

# Reserved words that cannot be used in skill names
# Reference: SKILL.md > Frontmatter Structure > Requirements
RESERVED_WORDS = frozenset([
    "anthropic", "claude", "skill", "plugin", "system", "admin",
    "root", "config", "settings", "internal", "core", "base"
])

# Maximum lengths per spec
# Reference: SKILL.md > Frontmatter Structure > Requirements
MAX_NAME_LENGTH = 64
MAX_DESCRIPTION_LENGTH = 1024


def validate_skill_name(name: str) -> tuple[bool, str]:
    """
    Validate skill name against requirements.

    Reference: SKILL.md > Frontmatter Structure > Requirements
    - Lowercase, hyphens only
    - No reserved words (anthropic, claude, etc.)
    - Max 64 characters

    Returns:
        (is_valid, error_message)
    """
    # Check length
    if len(name) > MAX_NAME_LENGTH:
        return False, f"Name exceeds {MAX_NAME_LENGTH} characters (got {len(name)})"

    # Check format: lowercase letters, numbers, hyphens only
    if not re.match(r'^[a-z][a-z0-9-]*[a-z0-9]$', name) and len(name) > 1:
        if not re.match(r'^[a-z]$', name):  # Single letter is ok
            return False, "Name must be lowercase with hyphens only (e.g., 'processing-pdfs')"

    # Check for reserved words
    name_parts = set(name.split('-'))
    reserved_found = name_parts & RESERVED_WORDS
    if reserved_found:
        return False, f"Name contains reserved word(s): {', '.join(reserved_found)}"

    # Check for double hyphens
    if '--' in name:
        return False, "Name cannot contain consecutive hyphens"

    # Check doesn't start or end with hyphen
    if name.startswith('-') or name.endswith('-'):
        return False, "Name cannot start or end with a hyphen"

    return True, ""


def suggest_gerund_name(name: str) -> Optional[str]:
    """
    Suggest gerund form if name doesn't follow convention.

    Reference: SKILL.md > Frontmatter Structure > Naming Convention (Gerund Form)
    - Use verb + -ing: 'processing-pdfs' not 'pdf-processor'
    """
    # Common patterns to convert
    conversions = {
        '-processor': '-processing',
        '-analyzer': '-analyzing',
        '-generator': '-generating',
        '-validator': '-validating',
        '-handler': '-handling',
        '-manager': '-managing',
        '-builder': '-building',
        '-creator': '-creating',
        '-parser': '-parsing',
        '-formatter': '-formatting',
    }

    for old, new in conversions.items():
        if name.endswith(old):
            suggested = name.replace(old, new)
            # Reorder if needed (pdf-processing -> processing-pdfs)
            parts = suggested.split('-')
            if len(parts) == 2 and parts[1].endswith('ing'):
                return f"{parts[1]}-{parts[0]}s" if not parts[0].endswith('s') else f"{parts[1]}-{parts[0]}"

    return None


def generate_skill_md(name: str, description: str = "") -> str:
    """
    Generate SKILL.md content with valid frontmatter.

    Reference: SKILL.md > Frontmatter Structure
    """
    if not description:
        description = f"[Description of what {name} does]. Use when [trigger conditions]."

    return f'''---
name: {name}
description: {description}
---

# {name.replace('-', ' ').title()}

[Brief overview of what this skill does - keep under 500 lines total]

## Quick Start

[Essential usage information that Claude needs immediately]

## Core Features

### Feature 1
[Description]

### Feature 2
[Description]

## Additional Resources

For advanced features, see supporting files:
- [Add references as needed]

---

*Reference: Created with init_skill.py following SKILL.md guidelines.*
'''


def generate_reference_file(name: str, topic: str) -> str:
    """Generate a reference file template."""
    return f'''# {topic.title()} Reference

Detailed {topic} documentation for {name}.

## Overview

[Add detailed content here]

## Sections

### Section 1
[Content]

### Section 2
[Content]

---

*Reference: See main [SKILL.md](../SKILL.md) for complete guidance.*
'''


def generate_script_file(name: str, script_type: str) -> str:
    """Generate a Python script template."""
    return f'''#!/usr/bin/env python3
"""
{script_type}.py - {script_type.replace('_', ' ').title()} for {name}.

Reference: See ../SKILL.md for skill documentation.
"""

import argparse
import sys
from pathlib import Path


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="{script_type.replace('_', ' ').title()}")
    # Add arguments here
    args = parser.parse_args()

    # Implementation here
    print(f"Running {script_type} for {name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
'''


def create_skill(
    name: str,
    output_path: Path,
    with_scripts: bool = False,
    with_references: bool = False,
    description: str = ""
) -> bool:
    """
    Create skill directory structure.

    Reference: SKILL.md > File Organization > Directory Patterns
    - Simple: 1 file (SKILL.md only)
    - With References: 3-4 files
    - With Scripts: 5-7 files

    CRITICAL: Start small! Only add files you'll complete NOW.
    Reference: SKILL.md > CRITICAL RULES
    """
    skill_dir = output_path / name

    # Check if already exists
    if skill_dir.exists():
        print(f"Error: Directory already exists: {skill_dir}")
        return False

    # Create base directory
    skill_dir.mkdir(parents=True)
    print(f"Created: {skill_dir}/")

    # Create SKILL.md (always required)
    skill_md_path = skill_dir / "SKILL.md"
    skill_md_path.write_text(generate_skill_md(name, description))
    print(f"Created: {skill_md_path}")

    # Track file count for warning
    file_count = 1

    # Create references/ if requested
    if with_references:
        ref_dir = skill_dir / "references"
        ref_dir.mkdir()
        print(f"Created: {ref_dir}/")

        # Create one reference file as starter
        ref_file = ref_dir / "guide.md"
        ref_file.write_text(generate_reference_file(name, "guide"))
        print(f"Created: {ref_file}")
        file_count += 1

    # Create scripts/ if requested
    if with_scripts:
        scripts_dir = skill_dir / "scripts"
        scripts_dir.mkdir()
        print(f"Created: {scripts_dir}/")

        # Create one script as starter
        script_file = scripts_dir / "main.py"
        script_file.write_text(generate_script_file(name, "main"))
        script_file.chmod(0o755)
        print(f"Created: {script_file}")
        file_count += 1

    return True


def print_next_steps(name: str, skill_dir: Path, file_count: int):
    """
    Print guidance for next steps.

    Reference: SKILL.md > 6-Step Creation Process
    """
    print("\n" + "=" * 60)
    print("SKILL INITIALIZED SUCCESSFULLY")
    print("=" * 60)

    print(f"\nSkill: {name}")
    print(f"Location: {skill_dir}")
    print(f"Files created: {file_count}")

    # Warning if approaching limits
    # Reference: SKILL.md > CRITICAL RULES > Rule 4: FILE COUNT LIMITS
    if file_count > 3:
        print(f"\nWARNING: You have {file_count} files. Most skills need only 1-3.")
        print("Reference: SKILL.md > CRITICAL RULES > Rule 4")

    print("\n" + "-" * 60)
    print("NEXT STEPS (Reference: SKILL.md > 6-Step Creation Process)")
    print("-" * 60)

    print("""
1. EDIT SKILL.md
   - Update the description in frontmatter
   - Add your skill's core content
   - Keep under 500 lines

2. COMPLETE BEFORE LINKING (CRITICAL!)
   - Write each referenced file BEFORE adding links
   - Never create placeholder files
   - Reference: SKILL.md > CRITICAL RULES > Rule 2 & 3

3. VALIDATE
   - Run: python package_skill.py {skill_dir}
   - Fix any reported issues

4. TEST
   - Use three-agent testing pattern
   - Reference: SKILL.md > Testing
""".format(skill_dir=skill_dir))

    print("-" * 60)
    print("REMEMBER THE CRITICAL RULES:")
    print("-" * 60)
    print("""
- START SMALL: Max 3 files for new skills
- NO PLACEHOLDERS: Every file must have content
- COMPLETE BEFORE LINKING: Write file, then add link
- 15+ FILES = NEVER: You are over-engineering

Reference: SKILL.md > CRITICAL RULES (top of file)
""")


def main():
    parser = argparse.ArgumentParser(
        description="Initialize a new Claude skill with proper structure.",
        epilog="Reference: See SKILL.md for complete skill creation guidance."
    )

    parser.add_argument(
        "name",
        help="Skill name (lowercase, hyphens, e.g., 'processing-pdfs')"
    )

    parser.add_argument(
        "--path",
        type=Path,
        default=Path.cwd(),
        help="Output directory (default: current directory)"
    )

    parser.add_argument(
        "--with-scripts",
        action="store_true",
        help="Include scripts/ directory with starter script"
    )

    parser.add_argument(
        "--with-references",
        action="store_true",
        help="Include references/ directory with starter file"
    )

    parser.add_argument(
        "--description",
        type=str,
        default="",
        help="Skill description for frontmatter"
    )

    parser.add_argument(
        "--force",
        action="store_true",
        help="Skip confirmation prompts"
    )

    args = parser.parse_args()

    # Validate name
    is_valid, error = validate_skill_name(args.name)
    if not is_valid:
        print(f"Error: Invalid skill name - {error}")
        print("Reference: SKILL.md > Frontmatter Structure > Requirements")
        return 1

    # Suggest gerund form if applicable
    suggested = suggest_gerund_name(args.name)
    if suggested and not args.force:
        print(f"Note: Consider using gerund form: '{suggested}' instead of '{args.name}'")
        print("Reference: SKILL.md > Frontmatter Structure > Naming Convention")
        response = input("Continue with original name? [y/N]: ").strip().lower()
        if response != 'y':
            print(f"Tip: Re-run with: python init_skill.py {suggested}")
            return 0

    # Validate description length if provided
    if args.description and len(args.description) > MAX_DESCRIPTION_LENGTH:
        print(f"Error: Description exceeds {MAX_DESCRIPTION_LENGTH} characters")
        print("Reference: SKILL.md > Frontmatter Structure > Requirements")
        return 1

    # Calculate expected file count
    expected_files = 1  # SKILL.md
    if args.with_references:
        expected_files += 1
    if args.with_scripts:
        expected_files += 1

    # Warn about file count
    # Reference: SKILL.md > CRITICAL RULES > Rule 1
    if expected_files > 3 and not args.force:
        print(f"\nWARNING: This will create {expected_files} files.")
        print("CRITICAL RULE: Maximum files for new skill is 3")
        print("Reference: SKILL.md > CRITICAL RULES > Rule 1")
        response = input("Continue anyway? [y/N]: ").strip().lower()
        if response != 'y':
            return 0

    # Create the skill
    success = create_skill(
        name=args.name,
        output_path=args.path,
        with_scripts=args.with_scripts,
        with_references=args.with_references,
        description=args.description
    )

    if not success:
        return 1

    # Print next steps
    skill_dir = args.path / args.name
    print_next_steps(args.name, skill_dir, expected_files)

    return 0


if __name__ == "__main__":
    sys.exit(main())
