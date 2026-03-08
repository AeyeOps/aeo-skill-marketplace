"""Shared utilities for skill-creator scripts."""

import os
import subprocess
import sys
from pathlib import Path


def _is_wsl() -> bool:
    """Detect WSL by checking /proc/version for the WSL kernel tag (e.g. 'WSL2').

    Guards against false positives on native Windows, where Python can read
    /proc/version through WSL filesystem interop.
    """
    if sys.platform != "linux":
        return False
    try:
        return "wsl" in Path("/proc/version").read_text().lower()
    except OSError:
        return False


def _has_windows_browser() -> bool:
    """Check whether $BROWSER resolves to a Windows-side process.

    Returns True if $BROWSER is a .exe, lives under /mnt/, or is a shell
    script that references a Windows binary.
    """
    browser = os.environ.get("BROWSER", "")
    if not browser:
        return False
    if browser.endswith(".exe") or "/mnt/" in browser:
        return True
    try:
        content = Path(browser).read_text()[:4096]
        return ".exe" in content or "/mnt/c" in content
    except (OSError, UnicodeDecodeError):
        return False


def browser_open_path(file_path: str) -> str:
    """Convert a local file path for webbrowser.open().

    On WSL with a Windows-side browser, converts Linux paths to Windows UNC
    paths via wslpath so the browser can resolve them. URLs and non-WSL
    environments pass through unchanged.
    """
    if file_path.startswith(("http://", "https://", "file://")):
        return file_path
    if not _is_wsl() or not _has_windows_browser():
        return file_path
    try:
        result = subprocess.run(
            ["wslpath", "-w", file_path],
            capture_output=True, text=True, timeout=5,
        )
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip()
    except (OSError, subprocess.TimeoutExpired):
        pass
    return file_path



def parse_skill_md(skill_path: Path) -> tuple[str, str, str]:
    """Parse a SKILL.md file, returning (name, description, full_content)."""
    content = (skill_path / "SKILL.md").read_text()
    lines = content.split("\n")

    if lines[0].strip() != "---":
        raise ValueError("SKILL.md missing frontmatter (no opening ---)")

    end_idx = None
    for i, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            end_idx = i
            break

    if end_idx is None:
        raise ValueError("SKILL.md missing frontmatter (no closing ---)")

    name = ""
    description = ""
    frontmatter_lines = lines[1:end_idx]
    i = 0
    while i < len(frontmatter_lines):
        line = frontmatter_lines[i]
        if line.startswith("name:"):
            name = line[len("name:"):].strip().strip('"').strip("'")
        elif line.startswith("description:"):
            value = line[len("description:"):].strip()
            # Handle YAML multiline indicators (>, |, >-, |-)
            if value in (">", "|", ">-", "|-"):
                continuation_lines: list[str] = []
                i += 1
                while i < len(frontmatter_lines) and (frontmatter_lines[i].startswith("  ") or frontmatter_lines[i].startswith("\t")):
                    continuation_lines.append(frontmatter_lines[i].strip())
                    i += 1
                description = " ".join(continuation_lines)
                continue
            else:
                description = value.strip('"').strip("'")
        i += 1

    return name, description, content
