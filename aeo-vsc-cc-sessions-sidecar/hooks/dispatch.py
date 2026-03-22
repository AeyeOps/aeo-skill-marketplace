#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import shutil
import sys
import tempfile
import time
from copy import deepcopy
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SCHEMA_VERSION = 2
PROCESS_RETENTION_SECONDS = 24 * 60 * 60
EVENT_MAX_BYTES = 2 * 1024 * 1024
EVENT_MAX_LINES = 2000
GC_INTERVAL_SECONDS = 60
COMPACT_SUMMARY_EXCERPT_CHARS = 512
PROMPT_TOOL_NAMES = {'AskUserQuestion', 'request_user_input', 'ExitPlanMode'}
ROOT_DIR_ENV = 'AEO_VSC_CC_SESSIONS_SIDECAR_ROOT'
VALIDATION_DIR_ENV = 'AEO_VSC_CC_SESSIONS_VALIDATION_DIR'
VALIDATION_LABEL_ENV = 'AEO_VSC_CC_SESSIONS_VALIDATION_LABEL'

SCRIPT_PATH = Path(__file__).resolve()
PLUGIN_ROOT = Path(os.environ.get('CLAUDE_PLUGIN_ROOT', SCRIPT_PATH.parent.parent))
WRITER_VERSION = (PLUGIN_ROOT / 'hooks' / 'VERSION').read_text(encoding='utf-8').strip()
DEFAULT_ROOT = Path.home() / '.claude' / 'aeo-vsc-cc-sessions'


@dataclass(frozen=True)
class ProcInfo:
  pid: int
  ppid: int | None
  start_ticks: int | None
  cmdline: list[str]


@dataclass(frozen=True)
class ProcessIdentity:
  hook_pid: int
  claude: ProcInfo
  ancestry: list[ProcInfo]

  @property
  def process_key(self) -> str:
    start_ticks = self.claude.start_ticks if self.claude.start_ticks is not None else 0
    return f'{self.claude.pid}:{start_ticks}'

  @property
  def process_dir_name(self) -> str:
    start_ticks = self.claude.start_ticks if self.claude.start_ticks is not None else 0
    return f'{self.claude.pid}-{start_ticks}'


def utc_now() -> datetime:
  return datetime.now(timezone.utc)


def isoformat(ts: datetime) -> str:
  return ts.isoformat(timespec='milliseconds').replace('+00:00', 'Z')


def parse_iso(ts: str | None) -> datetime | None:
  if not ts or not isinstance(ts, str):
    return None
  try:
    return datetime.fromisoformat(ts.replace('Z', '+00:00'))
  except ValueError:
    return None


def read_proc_stat(pid: int) -> tuple[int | None, int | None]:
  try:
    raw = Path(f'/proc/{pid}/stat').read_text(encoding='utf-8')
  except OSError:
    return None, None
  close = raw.rfind(')')
  if close == -1:
    return None, None
  fields = raw[close + 2:].split()
  if len(fields) < 20:
    return None, None
  try:
    return int(fields[1]), int(fields[19])
  except ValueError:
    return None, None


def read_cmdline(pid: int) -> list[str]:
  try:
    raw = Path(f'/proc/{pid}/cmdline').read_bytes()
  except OSError:
    return []
  return [part for part in raw.decode('utf-8', errors='replace').split('\0') if part]


def proc_info(pid: int) -> ProcInfo:
  ppid, start_ticks = read_proc_stat(pid)
  return ProcInfo(pid=pid, ppid=ppid, start_ticks=start_ticks, cmdline=read_cmdline(pid))


def looks_like_claude(cmdline: list[str]) -> bool:
  if not cmdline:
    return False
  executable = os.path.basename(cmdline[0]).lower()
  if executable in {'claude', 'claude.exe', 'claude.cmd'}:
    return True
  if executable in {'node', 'node.exe', 'bun', 'bun.exe'}:
    for arg in cmdline[1:]:
      normalized = arg.replace('\\', '/').lower()
      base = os.path.basename(normalized)
      if base in {'claude', 'claude.js', 'cli.js'} and 'claude' in normalized:
        return True
      if 'claude-code' in normalized or '@anthropic-ai' in normalized:
        return True
  return False


def resolve_process_identity() -> ProcessIdentity | None:
  ancestry: list[ProcInfo] = []
  seen: set[int] = set()
  current_pid = os.getpid()
  current = proc_info(current_pid)
  ancestry.append(current)
  seen.add(current.pid)

  cursor = current
  while cursor.ppid and cursor.ppid > 1 and cursor.ppid not in seen:
    cursor = proc_info(cursor.ppid)
    ancestry.append(cursor)
    seen.add(cursor.pid)
    if looks_like_claude(cursor.cmdline):
      return ProcessIdentity(hook_pid=current_pid, claude=cursor, ancestry=ancestry)

  return None


def sidecar_root() -> Path:
  return Path(os.environ.get(ROOT_DIR_ENV, str(DEFAULT_ROOT))).expanduser()


def load_json(path: Path) -> dict[str, Any] | None:
  try:
    return json.loads(path.read_text(encoding='utf-8'))
  except (OSError, json.JSONDecodeError):
    return None


def atomic_write_json(path: Path, payload: dict[str, Any]) -> None:
  path.parent.mkdir(parents=True, exist_ok=True)
  with tempfile.NamedTemporaryFile('w', encoding='utf-8', dir=path.parent, delete=False) as handle:
    json.dump(payload, handle, ensure_ascii=True, indent=2, sort_keys=True)
    handle.write('\n')
    temp_path = Path(handle.name)
  temp_path.replace(path)


def append_jsonl(path: Path, payload: dict[str, Any]) -> None:
  path.parent.mkdir(parents=True, exist_ok=True)
  with path.open('a', encoding='utf-8') as handle:
    handle.write(json.dumps(payload, ensure_ascii=True, sort_keys=True))
    handle.write('\n')


def capture_validation(
  identity: ProcessIdentity | None,
  payload: dict[str, Any],
  raw_stdin: str,
  event_record: dict[str, Any],
) -> None:
  root = os.environ.get(VALIDATION_DIR_ENV)
  if not root:
    return
  target = Path(root).expanduser()
  target.mkdir(parents=True, exist_ok=True)
  snapshot = {
    'ts': isoformat(utc_now()),
    'label': os.environ.get(VALIDATION_LABEL_ENV),
    'payload': payload,
    'raw_stdin': raw_stdin,
    'event_record': event_record,
    'resolved_process': None if identity is None else {
      'process_key': identity.process_key,
      'claude_pid': identity.claude.pid,
      'claude_pid_start_ticks': identity.claude.start_ticks,
      'cmdline': identity.claude.cmdline,
    },
    'ancestry': [
      {
        'pid': proc.pid,
        'ppid': proc.ppid,
        'start_ticks': proc.start_ticks,
        'cmdline': proc.cmdline,
      }
      for proc in ([] if identity is None else identity.ancestry)
    ],
  }
  append_jsonl(target / 'raw-captures.jsonl', snapshot)


def summarize_tool(tool_name: str | None, payload: dict[str, Any]) -> str | None:
  if not tool_name:
    return None
  tool_input = payload.get('tool_input')
  if not isinstance(tool_input, dict):
    tool_input = payload.get('input') if isinstance(payload.get('input'), dict) else {}
  if not isinstance(tool_input, dict):
    tool_input = {}
  if tool_name in {'Edit', 'Write', 'MultiEdit', 'NotebookEdit'}:
    file_path = tool_input.get('file_path')
    if isinstance(file_path, str) and file_path:
      return file_path
  if tool_name == 'Bash':
    command = tool_input.get('command')
    if isinstance(command, str) and command:
      return command
    description = tool_input.get('description')
    if isinstance(description, str) and description:
      return description
  if tool_name == 'Task':
    description = tool_input.get('description')
    if isinstance(description, str) and description:
      return description
  if tool_name in {'AskUserQuestion', 'request_user_input'}:
    questions = tool_input.get('questions')
    if isinstance(questions, list) and questions:
      first = questions[0]
      if isinstance(first, dict):
        question = first.get('question')
        if isinstance(question, str) and question:
          return question
  if tool_name == 'ExitPlanMode':
    plan = tool_input.get('plan')
    if isinstance(plan, str):
      for raw_line in plan.splitlines():
        line = raw_line.strip()
        if line:
          return line.removeprefix('#').strip()
  return None


def extract_tool_name(payload: dict[str, Any]) -> str | None:
  for key in ('tool_name', 'toolName', 'tool'):
    value = payload.get(key)
    if isinstance(value, str) and value:
      return value
  return None


def extract_text(payload: dict[str, Any], *keys: str) -> str | None:
  for key in keys:
    value = payload.get(key)
    if isinstance(value, str) and value:
      return value
  return None


def summarize_compact_text(compact_summary: str) -> str:
  compact_summary = compact_summary.strip()
  if len(compact_summary) <= COMPACT_SUMMARY_EXCERPT_CHARS:
    return compact_summary
  return compact_summary[:COMPACT_SUMMARY_EXCERPT_CHARS - 3].rstrip() + '...'


def map_notification_attention(notification_type: str | None) -> str | None:
  if notification_type == 'permission_prompt':
    return 'permission'
  if notification_type == 'idle_prompt':
    return 'idle'
  return None


def base_state(identity: ProcessIdentity, payload: dict[str, Any], now: datetime) -> dict[str, Any]:
  return {
    'schema_version': SCHEMA_VERSION,
    'writer_version': WRITER_VERSION,
    'updated_at': isoformat(now),
    'process_key': identity.process_key,
    'claude_pid': identity.claude.pid,
    'claude_pid_start_ticks': identity.claude.start_ticks,
    'cwd': extract_text(payload, 'cwd'),
    'current_session_id': extract_text(payload, 'session_id'),
    'current_transcript_path': extract_text(payload, 'transcript_path'),
    'state': 'idle',
    'needs_user_attention': False,
    'attention_kind': None,
    'permission_mode': extract_text(payload, 'permission_mode'),
    'tool_name': None,
    'tool_summary': None,
    'notification_type': None,
    'lineage': {
      'start_source': None,
      'previous_session_id': None,
      'previous_transcript_path': None,
    },
    'compact': {
      'pending': False,
      'trigger': None,
      'summary_path': None,
      'summary_excerpt': None,
    },
    'subagents': {
      'active_count': 0,
      'last_started_type': None,
      'last_started_at': None,
      'last_stopped_type': None,
    },
    'ended_reason': None,
    'last_event': {
      'hook_event_name': extract_text(payload, 'hook_event_name'),
      'ts': isoformat(now),
    },
  }


def normalize_state(existing: dict[str, Any] | None, identity: ProcessIdentity, payload: dict[str, Any], now: datetime) -> dict[str, Any]:
  if not isinstance(existing, dict):
    return base_state(identity, payload, now)
  state = deepcopy(existing)
  state['schema_version'] = SCHEMA_VERSION
  state['writer_version'] = WRITER_VERSION
  state['updated_at'] = isoformat(now)
  state['process_key'] = identity.process_key
  state['claude_pid'] = identity.claude.pid
  state['claude_pid_start_ticks'] = identity.claude.start_ticks
  state.setdefault('lineage', {})
  state.setdefault('compact', {})
  state.setdefault('subagents', {'active_count': 0, 'last_started_type': None, 'last_started_at': None, 'last_stopped_type': None})
  state.setdefault('last_event', {})
  return state


def event_record(identity: ProcessIdentity, payload: dict[str, Any], now: datetime) -> dict[str, Any]:
  tool_name = extract_tool_name(payload)
  record: dict[str, Any] = {
    'ts': isoformat(now),
    'process_key': identity.process_key,
    'claude_pid': identity.claude.pid,
    'claude_pid_start_ticks': identity.claude.start_ticks,
    'session_id': extract_text(payload, 'session_id'),
    'transcript_path': extract_text(payload, 'transcript_path'),
    'cwd': extract_text(payload, 'cwd'),
    'hook_event_name': extract_text(payload, 'hook_event_name'),
    'permission_mode': extract_text(payload, 'permission_mode'),
    'notification_type': extract_text(payload, 'notification_type', 'notificationType'),
    'tool_name': tool_name,
    'tool_summary': summarize_tool(tool_name, payload),
    'source': extract_text(payload, 'source'),
    'reason': extract_text(payload, 'reason'),
    'trigger': extract_text(payload, 'trigger'),
  }
  summary_path = extract_text(payload, 'summary_path', 'summaryPath')
  if summary_path:
    record['summary_path'] = summary_path
  compact_summary = extract_text(payload, 'compact_summary', 'compactSummary')
  if compact_summary:
    record['compact_summary'] = compact_summary
  error_type = extract_text(payload, 'error', 'error_type')
  if error_type:
    record['error_type'] = error_type
  error_details = extract_text(payload, 'error_details', 'errorDetails')
  if error_details:
    record['error_details'] = error_details
  agent_type = extract_text(payload, 'agent_type', 'agentType')
  if agent_type:
    record['agent_type'] = agent_type
  agent_id = extract_text(payload, 'agent_id', 'agentId')
  if agent_id:
    record['agent_id'] = agent_id
  return record


def apply_event(existing: dict[str, Any] | None, identity: ProcessIdentity, payload: dict[str, Any], now: datetime) -> tuple[dict[str, Any], dict[str, Any]]:
  state = normalize_state(existing, identity, payload, now)
  record = event_record(identity, payload, now)

  hook_event = record['hook_event_name']
  session_id = record['session_id']
  transcript_path = record['transcript_path']
  cwd = record['cwd']
  permission_mode = record['permission_mode']
  tool_name = record['tool_name']
  tool_summary = record['tool_summary']
  notification_type = record['notification_type']
  source = record['source']
  reason = record['reason']
  trigger = record['trigger']
  summary_path = record.get('summary_path')
  compact_summary = record.get('compact_summary')

  previous_session_id = state.get('current_session_id')
  previous_transcript_path = state.get('current_transcript_path')

  if cwd is not None:
    state['cwd'] = cwd
  if session_id is not None:
    state['current_session_id'] = session_id
  if transcript_path is not None:
    state['current_transcript_path'] = transcript_path
  if permission_mode is not None:
    state['permission_mode'] = permission_mode
  state['last_event'] = {
    'hook_event_name': hook_event,
    'ts': isoformat(now),
  }

  if hook_event == 'SessionStart':
    state['state'] = 'idle'
    state['needs_user_attention'] = False
    state['attention_kind'] = None
    state['tool_name'] = None
    state['tool_summary'] = None
    state['notification_type'] = None
    state['ended_reason'] = None
    state['lineage']['start_source'] = source
    if previous_session_id and previous_session_id != session_id:
      state['lineage']['previous_session_id'] = previous_session_id
      state['lineage']['previous_transcript_path'] = previous_transcript_path
    state['compact']['pending'] = False
    state['compact']['trigger'] = None
    state['compact']['summary_path'] = None
    state['compact']['summary_excerpt'] = None
    state['subagents']['active_count'] = 0
    state['subagents']['last_started_type'] = None
    state['subagents']['last_started_at'] = None
    state['subagents']['last_stopped_type'] = None
  elif hook_event == 'PermissionRequest':
    state['state'] = 'prompt'
    state['needs_user_attention'] = True
    state['attention_kind'] = 'permission'
    state['tool_name'] = tool_name
    state['tool_summary'] = tool_summary
  elif hook_event == 'Notification':
    state['notification_type'] = notification_type
    attention_kind = map_notification_attention(notification_type)
    if attention_kind:
      state['state'] = 'prompt'
      state['needs_user_attention'] = True
      state['attention_kind'] = attention_kind
      if tool_name:
        state['tool_name'] = tool_name
      if tool_summary:
        state['tool_summary'] = tool_summary
  elif hook_event == 'UserPromptSubmit':
    state['state'] = 'thinking'
    state['needs_user_attention'] = False
    state['attention_kind'] = None
    state['tool_name'] = None
    state['tool_summary'] = None
    state['notification_type'] = None
  elif hook_event == 'PreToolUse':
    if tool_name in PROMPT_TOOL_NAMES:
      state['state'] = 'prompt'
      state['needs_user_attention'] = True
      state['attention_kind'] = 'input'
    else:
      state['state'] = 'tool_pending'
      state['needs_user_attention'] = False
      state['attention_kind'] = None
    state['tool_name'] = tool_name
    state['tool_summary'] = tool_summary
    state['notification_type'] = None
  elif hook_event == 'PostToolUse':
    state['state'] = 'thinking'
    state['needs_user_attention'] = False
    state['attention_kind'] = None
    state['tool_name'] = None
    state['tool_summary'] = None
    state['notification_type'] = None
  elif hook_event == 'PostToolUseFailure':
    state['state'] = 'error'
    state['needs_user_attention'] = False
    state['attention_kind'] = None
    state['tool_name'] = tool_name
    state['tool_summary'] = tool_summary
    state['notification_type'] = None
  elif hook_event == 'PreCompact':
    state['state'] = 'compacting'
    state['compact']['pending'] = True
    state['compact']['trigger'] = trigger
  elif hook_event == 'PostCompact':
    state['state'] = 'thinking'
    state['compact']['pending'] = False
    state['compact']['trigger'] = trigger
    if isinstance(summary_path, str):
      state['compact']['summary_path'] = summary_path
    if isinstance(compact_summary, str):
      state['compact']['summary_excerpt'] = summarize_compact_text(compact_summary)
  elif hook_event == 'SessionEnd':
    state['state'] = 'ended'
    state['needs_user_attention'] = False
    state['attention_kind'] = None
    state['tool_name'] = None
    state['tool_summary'] = None
    state['notification_type'] = None
    state['ended_reason'] = reason
    state['subagents']['active_count'] = 0
  elif hook_event == 'Stop':
    if state['state'] not in ('error', 'ended', 'prompt'):
      state['state'] = 'idle'
      state['needs_user_attention'] = False
      state['attention_kind'] = None
      state['tool_name'] = None
      state['tool_summary'] = None
      state['notification_type'] = None
  elif hook_event == 'StopFailure':
    state['state'] = 'error'
    state['needs_user_attention'] = False
    state['attention_kind'] = None
    state['tool_name'] = None
    state['tool_summary'] = record.get('error_type')
    state['notification_type'] = None
  elif hook_event == 'SubagentStart':
    agent_type = record.get('agent_type')
    state['subagents']['active_count'] = max(0, state['subagents'].get('active_count', 0)) + 1
    state['subagents']['last_started_type'] = agent_type
    state['subagents']['last_started_at'] = isoformat(now)
  elif hook_event == 'SubagentStop':
    agent_type = record.get('agent_type')
    state['subagents']['active_count'] = max(0, state['subagents'].get('active_count', 0) - 1)
    state['subagents']['last_stopped_type'] = agent_type
  elif hook_event in {'Elicitation', 'ElicitationResult'}:
    pass

  return state, record


def should_trim_events(hook_event_name: str | None) -> bool:
  return hook_event_name in {'SessionStart', 'PostCompact', 'SessionEnd'}


def trim_events(path: Path) -> None:
  try:
    size = path.stat().st_size
  except OSError:
    return
  try:
    lines = path.read_text(encoding='utf-8').splitlines()
  except OSError:
    return
  if len(lines) <= EVENT_MAX_LINES and size <= EVENT_MAX_BYTES:
    return

  kept: list[str] = []
  kept_bytes = 0
  for line in reversed(lines):
    line_bytes = len(line.encode('utf-8')) + 1
    if kept and (len(kept) >= EVENT_MAX_LINES or kept_bytes + line_bytes > EVENT_MAX_BYTES):
      break
    kept.append(line)
    kept_bytes += line_bytes
  kept.reverse()
  path.write_text('\n'.join(kept) + ('\n' if kept else ''), encoding='utf-8')


def gc_process_root(root: Path, now: datetime) -> None:
  processes_root = root / 'processes'
  if not processes_root.exists():
    return
  cutoff = now.timestamp() - PROCESS_RETENTION_SECONDS
  for child in processes_root.iterdir():
    if not child.is_dir():
      continue
    state_path = child / 'state.json'
    if state_path.exists():
      state = load_json(state_path)
      updated_at = parse_iso(state.get('updated_at') if isinstance(state, dict) else None)
      state_name = state.get('state') if isinstance(state, dict) else None
      if state_name == 'ended' and updated_at and updated_at.timestamp() < cutoff:
        shutil.rmtree(child, ignore_errors=True)
      continue
    try:
      mtime = child.stat().st_mtime
    except OSError:
      continue
    if mtime < cutoff:
      shutil.rmtree(child, ignore_errors=True)


def maybe_gc(root: Path, now: datetime) -> None:
  stamp = root / '.last_gc_at'
  try:
    last_run = float(stamp.read_text(encoding='utf-8').strip())
  except (OSError, ValueError):
    last_run = 0.0
  if now.timestamp() - last_run < GC_INTERVAL_SECONDS:
    return
  root.mkdir(parents=True, exist_ok=True)
  gc_process_root(root, now)
  stamp.write_text(str(now.timestamp()), encoding='utf-8')


def run_self_test() -> int:
  test_root = Path(tempfile.mkdtemp(prefix='aeo-sidecar-selftest-'))
  os.environ[ROOT_DIR_ENV] = str(test_root)
  identity = ProcessIdentity(
    hook_pid=999,
    claude=ProcInfo(pid=1234, ppid=1, start_ticks=5678, cmdline=['claude']),
    ancestry=[],
  )
  now = utc_now()
  session_start = {
    'hook_event_name': 'SessionStart',
    'session_id': 'session-1',
    'transcript_path': '/tmp/session-1.jsonl',
    'cwd': '/tmp/project',
    'permission_mode': 'default',
    'source': 'startup',
  }
  state, record = apply_event(None, identity, session_start, now)
  process_dir = test_root / 'processes' / identity.process_dir_name
  atomic_write_json(process_dir / 'state.json', state)
  append_jsonl(process_dir / 'events.jsonl', record)

  prompt = {
    'hook_event_name': 'PermissionRequest',
    'session_id': 'session-1',
    'transcript_path': '/tmp/session-1.jsonl',
    'cwd': '/tmp/project',
    'permission_mode': 'default',
    'tool_name': 'Edit',
    'tool_input': {'file_path': '/tmp/project/demo.txt'},
  }
  state, record = apply_event(state, identity, prompt, utc_now())
  atomic_write_json(process_dir / 'state.json', state)
  append_jsonl(process_dir / 'events.jsonl', record)

  loaded = load_json(process_dir / 'state.json')
  if not isinstance(loaded, dict):
    return 1
  if loaded.get('state') != 'prompt':
    return 1
  if loaded.get('tool_name') != 'Edit':
    return 1
  if loaded.get('tool_summary') != '/tmp/project/demo.txt':
    return 1

  prompt_tool = {
    'hook_event_name': 'PreToolUse',
    'session_id': 'session-1',
    'transcript_path': '/tmp/session-1.jsonl',
    'cwd': '/tmp/project',
    'permission_mode': 'default',
    'tool_name': 'request_user_input',
    'tool_input': {
      'questions': [{'question': 'Choose one option'}],
    },
  }
  state, _ = apply_event(state, identity, prompt_tool, utc_now())
  if state.get('state') != 'prompt':
    return 1
  if state.get('attention_kind') != 'input':
    return 1
  if state.get('tool_summary') != 'Choose one option':
    return 1

  # Test unknown Notification type is inert (does not change state)
  # Transition to idle first so we can detect if the notification incorrectly changes state
  state, _ = apply_event(state, identity, {
    'hook_event_name': 'UserPromptSubmit',
    'session_id': 'session-1',
    'transcript_path': '/tmp/session-1.jsonl',
    'cwd': '/tmp/project',
  }, utc_now())
  state, _ = apply_event(state, identity, {
    'hook_event_name': 'Stop',
    'session_id': 'session-1',
    'transcript_path': '/tmp/session-1.jsonl',
    'cwd': '/tmp/project',
  }, utc_now())
  if state.get('state') != 'idle':
    return 1
  unknown_notification = {
    'hook_event_name': 'Notification',
    'session_id': 'session-1',
    'transcript_path': '/tmp/session-1.jsonl',
    'cwd': '/tmp/project',
    'notification_type': 'unvalidated_type',
  }
  state, _ = apply_event(state, identity, unknown_notification, utc_now())
  # Unknown notification type should NOT change state from idle
  if state.get('state') != 'idle':
    return 1
  # But should still record the notification_type
  if state.get('notification_type') != 'unvalidated_type':
    return 1
  # And should NOT set needs_user_attention
  if state.get('needs_user_attention') is True:
    return 1

  # Test Stop does NOT overwrite prompt state (prompt IS a guard state)
  state, _ = apply_event(state, identity, {
    'hook_event_name': 'PreToolUse',
    'session_id': 'session-1',
    'transcript_path': '/tmp/session-1.jsonl',
    'cwd': '/tmp/project',
    'tool_name': 'AskUserQuestion',
    'tool_input': {'questions': [{'question': 'Pick one'}]},
  }, utc_now())
  if state.get('state') != 'prompt':
    return 1
  state, _ = apply_event(state, identity, {
    'hook_event_name': 'Stop',
    'session_id': 'session-1',
    'transcript_path': '/tmp/session-1.jsonl',
    'cwd': '/tmp/project',
  }, utc_now())
  if state.get('state') != 'prompt':
    return 1

  # Test Stop -> idle from thinking state
  state, _ = apply_event(state, identity, {
    'hook_event_name': 'UserPromptSubmit',
    'session_id': 'session-1',
    'transcript_path': '/tmp/session-1.jsonl',
    'cwd': '/tmp/project',
  }, utc_now())
  if state.get('state') != 'thinking':
    return 1
  state, _ = apply_event(state, identity, {
    'hook_event_name': 'UserPromptSubmit',
    'session_id': 'session-1',
    'transcript_path': '/tmp/session-1.jsonl',
    'cwd': '/tmp/project',
  }, utc_now())
  if state.get('state') != 'thinking':
    return 1
  state, _ = apply_event(state, identity, {
    'hook_event_name': 'Stop',
    'session_id': 'session-1',
    'transcript_path': '/tmp/session-1.jsonl',
    'cwd': '/tmp/project',
  }, utc_now())
  if state.get('state') != 'idle':
    return 1
  if state.get('tool_name') is not None:
    return 1

  # Test Stop does NOT overwrite error state
  state, _ = apply_event(state, identity, {
    'hook_event_name': 'PostToolUseFailure',
    'session_id': 'session-1',
    'transcript_path': '/tmp/session-1.jsonl',
    'cwd': '/tmp/project',
    'tool_name': 'Bash',
  }, utc_now())
  if state.get('state') != 'error':
    return 1
  state, _ = apply_event(state, identity, {
    'hook_event_name': 'Stop',
    'session_id': 'session-1',
    'transcript_path': '/tmp/session-1.jsonl',
    'cwd': '/tmp/project',
  }, utc_now())
  if state.get('state') != 'error':
    return 1

  # Test StopFailure -> error with error type and event record fields
  state, record = apply_event(state, identity, {
    'hook_event_name': 'StopFailure',
    'session_id': 'session-1',
    'transcript_path': '/tmp/session-1.jsonl',
    'cwd': '/tmp/project',
    'error': 'rate_limit',
    'error_details': '429 Too Many Requests',
  }, utc_now())
  if state.get('state') != 'error':
    return 1
  if state.get('tool_summary') != 'rate_limit':
    return 1
  if record.get('error_type') != 'rate_limit':
    return 1
  if record.get('error_details') != '429 Too Many Requests':
    return 1

  # Test SubagentStart increments counter and event record carries agent fields
  state, record = apply_event(state, identity, {
    'hook_event_name': 'SubagentStart',
    'session_id': 'session-1',
    'transcript_path': '/tmp/session-1.jsonl',
    'cwd': '/tmp/project',
    'agent_type': 'Explore',
    'agent_id': 'agent-abc-123',
  }, utc_now())
  if state['subagents']['active_count'] != 1:
    return 1
  if state['subagents']['last_started_type'] != 'Explore':
    return 1
  if record.get('agent_type') != 'Explore':
    return 1
  if record.get('agent_id') != 'agent-abc-123':
    return 1

  # Test SubagentStop decrements counter and event record carries agent fields
  state, record = apply_event(state, identity, {
    'hook_event_name': 'SubagentStop',
    'session_id': 'session-1',
    'transcript_path': '/tmp/session-1.jsonl',
    'cwd': '/tmp/project',
    'agent_type': 'Explore',
    'agent_id': 'agent-abc-123',
  }, utc_now())
  if state['subagents']['active_count'] != 0:
    return 1
  if state['subagents']['last_stopped_type'] != 'Explore':
    return 1

  # Test SubagentStop clamps at 0
  state, _ = apply_event(state, identity, {
    'hook_event_name': 'SubagentStop',
    'session_id': 'session-1',
    'transcript_path': '/tmp/session-1.jsonl',
    'cwd': '/tmp/project',
    'agent_type': 'Plan',
  }, utc_now())
  if state['subagents']['active_count'] != 0:
    return 1

  return 0


def main() -> int:
  os.umask(0o077)

  if len(sys.argv) > 1 and sys.argv[1] == '--self-test':
    return run_self_test()

  raw_stdin = sys.stdin.read()
  if not raw_stdin.strip():
    return 0

  try:
    payload = json.loads(raw_stdin)
  except json.JSONDecodeError:
    return 0
  if not isinstance(payload, dict):
    return 0

  identity = resolve_process_identity()
  now = utc_now()
  event = {
    'ts': isoformat(now),
    'hook_event_name': extract_text(payload, 'hook_event_name'),
    'session_id': extract_text(payload, 'session_id'),
  }
  if identity is None:
    capture_validation(None, payload, raw_stdin, event)
    return 0

  root = sidecar_root()
  process_dir = root / 'processes' / identity.process_dir_name
  state_path = process_dir / 'state.json'
  events_path = process_dir / 'events.jsonl'
  existing = load_json(state_path)
  state, record = apply_event(existing, identity, payload, now)
  atomic_write_json(state_path, state)
  append_jsonl(events_path, record)
  if should_trim_events(record['hook_event_name']):
    trim_events(events_path)
  maybe_gc(root, now)
  capture_validation(identity, payload, raw_stdin, record)
  return 0


if __name__ == '__main__':
  raise SystemExit(main())
