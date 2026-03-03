#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="${1:?Usage: reconcile_nous_entries.sh <project-dir>}"
HOOKS_DIR="$(cd "$(dirname "$0")/../hooks" && pwd)"

HOOKS_DIR="$HOOKS_DIR" PROJECT_DIR="$PROJECT_DIR" python3 -c "
import os, sys
sys.path.insert(0, os.environ['HOOKS_DIR'])
from nous import reconcile_nous_entries
from pathlib import Path
import json
result = reconcile_nous_entries(Path(os.environ['PROJECT_DIR']))
print(json.dumps(result, indent=2))
"
