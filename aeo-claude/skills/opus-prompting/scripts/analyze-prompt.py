#!/usr/bin/env python3
"""
Opus 4.5 Prompt Analyzer

Analyzes prompts for deprecated patterns and suggests optimizations.
Reads from stdin or file argument, outputs analysis to stdout.

Usage:
    echo "Your prompt" | python3 analyze-prompt.py
    python3 analyze-prompt.py prompt.txt
    python3 analyze-prompt.py --optimize prompt.txt
"""

import argparse
import json
import re
import sys
from pathlib import Path


def load_config() -> dict:
    """Load configuration from config.json."""
    config_path = Path(__file__).parent / "config.json"
    try:
        with open(config_path) as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"min_words": 1, "enabled": True}


def count_words(text: str) -> int:
    """Count words in text."""
    return len(text.split())


def analyze_prompt(prompt: str) -> list[dict]:
    """
    Analyze prompt for deprecated patterns.
    Returns list of issues with descriptions and suggestions.
    """
    issues = []

    # Pattern 1: Aggressive language
    aggressive_patterns = [
        (r'\bCRITICAL\b', 'CRITICAL'),
        (r'\bMUST\b', 'MUST'),
        (r'\bNEVER\b', 'NEVER'),
        (r'\bALWAYS\b', 'ALWAYS'),
        (r'\bIMPORTANT\b', 'IMPORTANT'),
        (r'\bREQUIRED\b', 'REQUIRED'),
    ]

    aggressive_count = 0
    found_aggressive = []
    for pattern, name in aggressive_patterns:
        matches = re.findall(pattern, prompt, re.IGNORECASE)
        if matches:
            aggressive_count += len(matches)
            found_aggressive.append(name)

    if aggressive_count >= 2:
        issues.append({
            "type": "aggressive_language",
            "description": f"Aggressive language: {', '.join(set(found_aggressive))}",
            "suggestion": "Opus 4.5 responds well to gentler language. Use 'Use when...' or 'Prefer X because...'",
        })

    # Pattern 2: "Think" variants
    think_patterns = [
        r'\bthink\s+step\s+by\s+step\b',
        r'\bthink\s+carefully\b',
        r'\bthink\s+through\b',
        r'\blet\'?s?\s+think\b',
    ]

    for pattern in think_patterns:
        if re.search(pattern, prompt, re.IGNORECASE):
            issues.append({
                "type": "think_sensitivity",
                "description": "Contains 'think' variants",
                "suggestion": "Replace with 'consider', 'evaluate', 'reflect', or 'analyze'",
            })
            break

    # Pattern 3: Tool over-triggering
    tool_trigger_patterns = [
        (r'\bMUST\s+(use|call|invoke)\b', "MUST use/call"),
        (r'\bALWAYS\s+(use|call|invoke)\b', "ALWAYS use/call"),
        (r'\bYou\s+MUST\b', "You MUST"),
    ]

    for pattern, name in tool_trigger_patterns:
        if re.search(pattern, prompt, re.IGNORECASE):
            issues.append({
                "type": "tool_over_trigger",
                "description": f"Tool over-triggering: '{name}'",
                "suggestion": "Use 'Use [tool] when...' instead",
            })
            break

    # Pattern 4: Missing context/motivation
    command_patterns = [
        r'\bNever\s+\w+',
        r'\bDo\s+not\s+\w+',
        r'\bDon\'t\s+\w+',
        r'\bAvoid\s+\w+',
    ]

    has_command = any(re.search(p, prompt, re.IGNORECASE) for p in command_patterns)
    has_motivation = bool(re.search(
        r'\bbecause\b|\bsince\b|\bas\s+\w+\s+will\b|\bto\s+ensure\b',
        prompt, re.IGNORECASE
    ))

    if has_command and not has_motivation:
        issues.append({
            "type": "missing_context",
            "description": "Commands without explanation",
            "suggestion": "Add 'because...' to explain why. Opus 4.5 generalizes better with context.",
        })

    # Pattern 5: Markdown formatting mismatch
    has_markdown = bool(re.search(r'```|#{1,6}\s|\*\*|\*\s|-\s\[', prompt))
    wants_plain = bool(re.search(
        r'\bplain\s+text\b|\bno\s+markdown\b|\bwithout\s+formatting\b',
        prompt, re.IGNORECASE
    ))

    if has_markdown and wants_plain:
        issues.append({
            "type": "format_mismatch",
            "description": "Markdown prompt requests plain output",
            "suggestion": "Match prompt style to desired output. Remove markdown to reduce it in response.",
        })

    return issues


def generate_optimized_prompt(prompt: str, issues: list[dict]) -> str:
    """Generate an optimized version of the prompt based on issues found."""
    optimized = prompt

    for issue in issues:
        if issue["type"] == "aggressive_language":
            optimized = re.sub(r'\bCRITICAL:\s*', '', optimized, flags=re.IGNORECASE)
            optimized = re.sub(r'\bYou\s+MUST\b', 'You should', optimized, flags=re.IGNORECASE)
            optimized = re.sub(r'\bMUST\b', 'should', optimized, flags=re.IGNORECASE)
            optimized = re.sub(r'\bNEVER\b', 'avoid', optimized, flags=re.IGNORECASE)
            optimized = re.sub(r'\bALWAYS\b', 'prefer to', optimized, flags=re.IGNORECASE)

        elif issue["type"] == "think_sensitivity":
            optimized = re.sub(
                r'\bthink\s+step\s+by\s+step\b',
                'consider systematically',
                optimized, flags=re.IGNORECASE
            )
            optimized = re.sub(
                r'\bthink\s+carefully\b',
                'evaluate carefully',
                optimized, flags=re.IGNORECASE
            )
            optimized = re.sub(
                r'\bthink\s+through\b',
                'analyze',
                optimized, flags=re.IGNORECASE
            )
            optimized = re.sub(
                r'\blet\'?s?\s+think\b',
                "let's consider",
                optimized, flags=re.IGNORECASE
            )

        elif issue["type"] == "tool_over_trigger":
            optimized = re.sub(
                r'\bMUST\s+use\b',
                'should use',
                optimized, flags=re.IGNORECASE
            )
            optimized = re.sub(
                r'\bMUST\s+call\b',
                'should call',
                optimized, flags=re.IGNORECASE
            )
            optimized = re.sub(
                r'\bALWAYS\s+use\b',
                'use',
                optimized, flags=re.IGNORECASE
            )

    return optimized.strip()


def format_output(issues: list[dict], optimized: str | None = None, json_output: bool = False) -> str:
    """Format analysis output."""
    if json_output:
        result = {"issues": issues}
        if optimized:
            result["optimized"] = optimized
        return json.dumps(result, indent=2)

    if not issues:
        return "No deprecated patterns detected."

    lines = ["Issues detected:", ""]
    for issue in issues:
        lines.append(f"  [{issue['type']}] {issue['description']}")
        lines.append(f"    -> {issue['suggestion']}")
        lines.append("")

    if optimized:
        lines.append("Suggested version:")
        lines.append("-" * 40)
        lines.append(optimized)
        lines.append("-" * 40)

    return "\n".join(lines)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Analyze prompts for Opus 4.5 compatibility"
    )
    parser.add_argument(
        "file",
        nargs="?",
        help="File containing prompt (reads stdin if omitted)"
    )
    parser.add_argument(
        "--optimize", "-o",
        action="store_true",
        help="Include optimized version in output"
    )
    parser.add_argument(
        "--json", "-j",
        action="store_true",
        help="Output as JSON"
    )
    args = parser.parse_args()

    config = load_config()
    if not config.get("enabled", True):
        return

    # Read prompt
    if args.file:
        try:
            with open(args.file) as f:
                prompt = f.read()
        except FileNotFoundError:
            print(f"Error: File not found: {args.file}", file=sys.stderr)
            sys.exit(1)
    else:
        prompt = sys.stdin.read()

    if not prompt.strip():
        return

    # Check word count threshold
    min_words = config.get("min_words", 1)
    if count_words(prompt) < min_words:
        return

    # Analyze
    issues = analyze_prompt(prompt)

    if not issues and not args.json:
        print("No deprecated patterns detected.")
        return

    # Generate optimized version if requested
    optimized = None
    if args.optimize and issues:
        optimized = generate_optimized_prompt(prompt, issues)

    # Output
    print(format_output(issues, optimized, args.json))


if __name__ == "__main__":
    main()
