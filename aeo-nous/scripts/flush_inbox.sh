#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="${1:?Usage: flush_inbox.sh <project-dir>}"
HOOKS_DIR="$(cd "$(dirname "$0")/../hooks" && pwd)"

HOOKS_DIR="$HOOKS_DIR" PROJECT_DIR="$PROJECT_DIR" python3 -c "
import os, sys
sys.path.insert(0, os.environ['HOOKS_DIR'])
from lenses.base import flush_inbox
from lenses.knowledge import KNOWLEDGE_LENS
from lenses.learnings import LEARNINGS_LENS
from pathlib import Path
project = Path(os.environ['PROJECT_DIR'])
k = flush_inbox(KNOWLEDGE_LENS, project)
l = flush_inbox(LEARNINGS_LENS, project)
print(f'Flushed: cortex={k}, engram={l}')
"
