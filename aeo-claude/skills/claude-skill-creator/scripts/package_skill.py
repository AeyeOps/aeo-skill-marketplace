#!/usr/bin/env python3
"""
package_skill.py - Validate and package a Claude skill.

This script validates skill structure and creates a distributable package.
Reference: See ../SKILL.md for complete skill creation guidance.

Usage:
    python package_skill.py <skill-directory> [--output <file.skill>] [--no-package]

Examples:
    python package_skill.py ./my-skill
    python package_skill.py ./my-skill --output my-skill-v1.0.0.skill
    python package_skill.py ./my-skill --no-package  # Validate only
"""

import argparse
import os
import re
import sys
import zipfile
from pathlib import Path
from typing import Optional

# Validation constants
# Reference: SKILL.md > Frontmatter Structure > Requirements
MAX_NAME_LENGTH = 64
MAX_DESCRIPTION_LENGTH = 1024
MAX_SKILL_MD_LINES = 500
MAX_SUPPORTING_FILE_LINES = 500

# File count limits
# Reference: SKILL.md > CRITICAL RULES > Rule 4
FILE_COUNT_WARNING = 6
FILE_COUNT_MAX = 10
FILE_COUNT_NEVER = 15

# Files that should NOT be in skills
# Reference: SKILL.md > File Organization > What NOT to Include
DISALLOWED_FILES = frozenset([
    "README.md",
    "INSTALLATION_GUIDE.md",
    "CHANGELOG.md",
    "LICENSE",  # belongs in plugin, not skill
    ".git",
    ".gitignore",
    "__pycache__",
    ".DS_Store",
])


class ValidationError:
    """Represents a validation error with reference."""

    def __init__(self, message: str, reference: str, severity: str = "error"):
        self.message = message
        self.reference = reference
        self.severity = severity  # "error", "warning", "info"

    def __str__(self):
        prefix = {"error": "ERROR", "warning": "WARNING", "info": "INFO"}[self.severity]
        return f"[{prefix}] {self.message}\n         Reference: SKILL.md > {self.reference}"


class SkillValidator:
    """Validates skill structure and content."""

    def __init__(self, skill_dir: Path):
        self.skill_dir = skill_dir
        self.errors: list[ValidationError] = []
        self.skill_md_path = skill_dir / "SKILL.md"
        self.skill_md_content = ""
        self.frontmatter: dict = {}

    def validate(self) -> bool:
        """
        Run all validations.

        Returns True if no errors (warnings OK).
        """
        self._check_directory_exists()
        if self.errors:
            return False

        self._check_skill_md_exists()
        if self.errors:
            return False

        self._load_skill_md()
        self._validate_frontmatter()
        self._validate_file_count()
        self._validate_file_references()
        self._validate_file_sizes()
        self._check_disallowed_files()
        self._check_placeholder_files()

        # Return True if no errors (warnings are OK)
        return not any(e.severity == "error" for e in self.errors)

    def _check_directory_exists(self):
        """Verify skill directory exists."""
        if not self.skill_dir.exists():
            self.errors.append(ValidationError(
                f"Skill directory not found: {self.skill_dir}",
                "File Organization"
            ))
        elif not self.skill_dir.is_dir():
            self.errors.append(ValidationError(
                f"Path is not a directory: {self.skill_dir}",
                "File Organization"
            ))

    def _check_skill_md_exists(self):
        """Verify SKILL.md exists."""
        if not self.skill_md_path.exists():
            self.errors.append(ValidationError(
                "SKILL.md not found",
                "File Organization"
            ))

    def _load_skill_md(self):
        """Load and parse SKILL.md content."""
        try:
            self.skill_md_content = self.skill_md_path.read_text()
        except Exception as e:
            self.errors.append(ValidationError(
                f"Failed to read SKILL.md: {e}",
                "File Organization"
            ))
            return

        # Parse frontmatter
        self._parse_frontmatter()

    def _parse_frontmatter(self):
        """
        Parse YAML frontmatter from SKILL.md.

        Reference: SKILL.md > Frontmatter Structure
        """
        lines = self.skill_md_content.split('\n')

        # Check for opening delimiter
        if not lines or lines[0].strip() != '---':
            self.errors.append(ValidationError(
                "SKILL.md must start with '---' frontmatter delimiter",
                "Frontmatter Structure"
            ))
            return

        # Find closing delimiter
        closing_idx = None
        for i, line in enumerate(lines[1:], 1):
            if line.strip() == '---':
                closing_idx = i
                break

        if closing_idx is None:
            self.errors.append(ValidationError(
                "SKILL.md missing closing '---' frontmatter delimiter",
                "Frontmatter Structure"
            ))
            return

        # Parse frontmatter content
        frontmatter_lines = lines[1:closing_idx]
        for line in frontmatter_lines:
            if ':' in line:
                key, value = line.split(':', 1)
                self.frontmatter[key.strip()] = value.strip()

    def _validate_frontmatter(self):
        """
        Validate frontmatter fields.

        Reference: SKILL.md > Frontmatter Structure > Requirements
        """
        # Check required fields
        if 'name' not in self.frontmatter:
            self.errors.append(ValidationError(
                "Missing required field: name",
                "Frontmatter Structure > Requirements"
            ))
        else:
            name = self.frontmatter['name']
            if len(name) > MAX_NAME_LENGTH:
                self.errors.append(ValidationError(
                    f"Name exceeds {MAX_NAME_LENGTH} chars (got {len(name)})",
                    "Frontmatter Structure > Requirements"
                ))

            # Check format
            if not re.match(r'^[a-z][a-z0-9-]*$', name):
                self.errors.append(ValidationError(
                    "Name must be lowercase with hyphens only",
                    "Frontmatter Structure > Requirements"
                ))

            # Check for reserved words
            reserved = {'anthropic', 'claude', 'skill', 'plugin'}
            name_parts = set(name.split('-'))
            found = name_parts & reserved
            if found:
                self.errors.append(ValidationError(
                    f"Name contains reserved word(s): {', '.join(found)}",
                    "Frontmatter Structure > Requirements"
                ))

        if 'description' not in self.frontmatter:
            self.errors.append(ValidationError(
                "Missing required field: description",
                "Frontmatter Structure > Requirements"
            ))
        else:
            desc = self.frontmatter['description']
            if len(desc) > MAX_DESCRIPTION_LENGTH:
                self.errors.append(ValidationError(
                    f"Description exceeds {MAX_DESCRIPTION_LENGTH} chars (got {len(desc)})",
                    "Frontmatter Structure > Requirements"
                ))

            # Check for "what" and "when"
            if 'use when' not in desc.lower() and 'when' not in desc.lower():
                self.errors.append(ValidationError(
                    "Description should include 'Use when [trigger conditions]'",
                    "Frontmatter Structure > Description Formula",
                    severity="warning"
                ))

    def _validate_file_count(self):
        """
        Validate total file count.

        Reference: SKILL.md > CRITICAL RULES > Rule 4
        """
        all_files = list(self.skill_dir.rglob('*'))
        file_count = sum(1 for f in all_files if f.is_file())

        if file_count >= FILE_COUNT_NEVER:
            self.errors.append(ValidationError(
                f"CRITICAL: {file_count} files detected. 15+ files = NEVER allowed!",
                "CRITICAL RULES > Rule 4: FILE COUNT LIMITS"
            ))
        elif file_count > FILE_COUNT_MAX:
            self.errors.append(ValidationError(
                f"Too many files: {file_count}. Complex skills max 7-10 files.",
                "CRITICAL RULES > Rule 4: FILE COUNT LIMITS"
            ))
        elif file_count > FILE_COUNT_WARNING:
            self.errors.append(ValidationError(
                f"High file count: {file_count}. Most skills need only 1-3 files.",
                "CRITICAL RULES > Rule 4: FILE COUNT LIMITS",
                severity="warning"
            ))

    def _validate_file_references(self):
        """
        Validate all file references in SKILL.md exist.

        Reference: SKILL.md > CRITICAL RULES > Rule 2 & 3
        """
        # Find markdown links: [text](path)
        link_pattern = r'\[([^\]]+)\]\(([^)]+)\)'
        matches = re.findall(link_pattern, self.skill_md_content)

        for text, path in matches:
            # Skip external URLs
            if path.startswith(('http://', 'https://', '#')):
                continue

            # Resolve relative path
            ref_path = self.skill_dir / path
            if not ref_path.exists():
                self.errors.append(ValidationError(
                    f"Broken reference: [{text}]({path}) - file not found",
                    "CRITICAL RULES > Rule 2: NO PLACEHOLDERS"
                ))

    def _validate_file_sizes(self):
        """
        Validate file sizes are within limits.

        Reference: SKILL.md > Core Principles
        """
        # Check SKILL.md
        skill_md_lines = len(self.skill_md_content.split('\n'))
        if skill_md_lines > MAX_SKILL_MD_LINES:
            self.errors.append(ValidationError(
                f"SKILL.md exceeds {MAX_SKILL_MD_LINES} lines (got {skill_md_lines})",
                "Core Principles",
                severity="warning"
            ))

        # Check supporting files
        for f in self.skill_dir.rglob('*'):
            if f.is_file() and f != self.skill_md_path:
                if f.suffix in ('.md', '.txt', '.py'):
                    try:
                        lines = len(f.read_text().split('\n'))
                        if lines > MAX_SUPPORTING_FILE_LINES:
                            self.errors.append(ValidationError(
                                f"{f.name} exceeds {MAX_SUPPORTING_FILE_LINES} lines (got {lines})",
                                "File Organization",
                                severity="warning"
                            ))
                    except Exception:
                        pass  # Skip binary files

    def _check_disallowed_files(self):
        """
        Check for files that shouldn't be in skills.

        Reference: SKILL.md > File Organization > What NOT to Include
        """
        for f in self.skill_dir.iterdir():
            if f.name in DISALLOWED_FILES:
                self.errors.append(ValidationError(
                    f"File '{f.name}' should not be in skill directory",
                    "File Organization > What NOT to Include",
                    severity="warning"
                ))

    def _check_placeholder_files(self):
        """
        Check for empty placeholder files.

        Reference: SKILL.md > CRITICAL RULES > Rule 2
        """
        for f in self.skill_dir.rglob('*'):
            if f.is_file() and f.suffix in ('.md', '.txt'):
                try:
                    content = f.read_text().strip()
                    # Check for empty or placeholder content
                    if not content:
                        self.errors.append(ValidationError(
                            f"Empty file detected: {f.relative_to(self.skill_dir)}",
                            "CRITICAL RULES > Rule 2: NO PLACEHOLDERS"
                        ))
                    elif content in ('[TODO]', '[PLACEHOLDER]', 'TODO', 'TBD'):
                        self.errors.append(ValidationError(
                            f"Placeholder detected in: {f.relative_to(self.skill_dir)}",
                            "CRITICAL RULES > Rule 2: NO PLACEHOLDERS"
                        ))
                except Exception:
                    pass

    def print_report(self):
        """Print validation report."""
        print("\n" + "=" * 60)
        print("SKILL VALIDATION REPORT")
        print("=" * 60)

        print(f"\nSkill: {self.skill_dir}")
        if 'name' in self.frontmatter:
            print(f"Name: {self.frontmatter['name']}")

        errors = [e for e in self.errors if e.severity == "error"]
        warnings = [e for e in self.errors if e.severity == "warning"]

        print(f"\nErrors: {len(errors)}")
        print(f"Warnings: {len(warnings)}")

        if errors:
            print("\n" + "-" * 60)
            print("ERRORS (must fix)")
            print("-" * 60)
            for e in errors:
                print(f"\n{e}")

        if warnings:
            print("\n" + "-" * 60)
            print("WARNINGS (should fix)")
            print("-" * 60)
            for e in warnings:
                print(f"\n{e}")

        if not errors and not warnings:
            print("\nAll validations passed!")

        print("\n" + "=" * 60)


def create_package(skill_dir: Path, output_path: Optional[Path] = None) -> Path:
    """
    Create .skill zip package.

    Returns path to created package.
    """
    if output_path is None:
        output_path = skill_dir.parent / f"{skill_dir.name}.skill"

    with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        for f in skill_dir.rglob('*'):
            if f.is_file():
                # Skip hidden files and __pycache__
                if any(part.startswith('.') or part == '__pycache__'
                       for part in f.parts):
                    continue
                arcname = f.relative_to(skill_dir)
                zf.write(f, arcname)

    return output_path


def main():
    parser = argparse.ArgumentParser(
        description="Validate and package a Claude skill.",
        epilog="Reference: See SKILL.md for complete skill creation guidance."
    )

    parser.add_argument(
        "skill_dir",
        type=Path,
        help="Path to skill directory"
    )

    parser.add_argument(
        "--output", "-o",
        type=Path,
        help="Output package path (default: <skill-name>.skill)"
    )

    parser.add_argument(
        "--no-package",
        action="store_true",
        help="Validate only, don't create package"
    )

    parser.add_argument(
        "--quiet", "-q",
        action="store_true",
        help="Minimal output (exit code only)"
    )

    args = parser.parse_args()

    # Run validation
    validator = SkillValidator(args.skill_dir)
    is_valid = validator.validate()

    if not args.quiet:
        validator.print_report()

    if not is_valid:
        print("\nPackaging ABORTED due to errors.")
        print("Fix errors and re-run validation.")
        return 1

    # Create package if requested
    if not args.no_package:
        try:
            package_path = create_package(args.skill_dir, args.output)
            if not args.quiet:
                print(f"\nPackage created: {package_path}")
                print(f"Size: {package_path.stat().st_size:,} bytes")
        except Exception as e:
            print(f"\nError creating package: {e}")
            return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
