---
description: Session retrospective that extracts improvements and reconciles stale guidance in CLAUDE.md files and project skills
allowed-tools: Read, Edit, Write, Glob, Grep, Bash, Skill
---

# Session Retrospective

Analyze the current session for improvement opportunities. Extract durable insights and codify them into the right destination: project SKILL.md, project CLAUDE.md (any level), or user CLAUDE.md.

## Step 1: Gather Context

Identify the project and session state:

```
Project root: current working directory
Project name: basename of the project root (used for skill directory naming)
```

Find all existing CLAUDE.md and .claude.local.md files in the hierarchy using Glob:

- `**/CLAUDE.md` -- all project-level CLAUDE.md files
- `**/.claude.local.md` -- personal/gitignored project files

Check for an existing project skill using Glob:

- `.claude/skills/<project-name>/SKILL.md`

Check user-level CLAUDE.md:

- Read `~/.claude/CLAUDE.md` (may not exist)

Read the full content of every file found above — not just confirming existence. Hold the content in working memory for the reconciliation step, because detecting stale or contradicted guidance requires comparing saved text against current session learnings.

If aeo-nous is enabled, check for a `.claude/nous/` directory. If present, glob for `**/*.jsonl` files under it and read a sample of entries from each to understand the schema (field names, structure, lens purpose). These files carry corrections and discoveries from prior sessions — both general and project-specific. Hold their content alongside CLAUDE.md/SKILL.md content for reconciliation.

## Step 2: Session Analysis

Review the full session transcript for improvement signals. Look for the same categories as nous learnings, but with a focus on what should be **persisted** into guidance files:

**Corrections** (highest priority)
- User redirected Claude's approach ("no, do X instead")
- Stated rules or principles ("we always...", "never...")
- Repeated the same feedback multiple times

**Discoveries**
- Non-obvious project patterns uncovered during the session
- Architecture decisions or constraints encountered
- Tool/command quirks specific to this project
- Integration patterns that worked (or didn't)

**Process improvements**
- Workflow gaps where instructions were missing
- Steps that should have been automated
- Quality gates that should be standard

**Missed context**
- Information Claude had to ask about or discover the hard way
- Assumptions that were wrong and needed correction
- Domain knowledge that would have saved time

For each signal, assess:
1. Is this durable (applies to future sessions, not just this task)?
2. Is this specific enough to be actionable?
3. Is this genuinely new (not already in CLAUDE.md or skills)?

Discard anything that fails these three checks.

## Step 2b: Knowledge Reconciliation

Compare current session insights against every piece of existing saved guidance. This step catches stale, contradicted, or superseded content that should be corrected — not just new content to add.

Sources of current truth for reconciliation:
- Session transcript (what happened during this session)
- Nous-injected context sections (if present in session start), which carry forward corrections from prior sessions
- Direct observations from tool calls and file reads

When nous entries and saved guidance conflict, use judgment rather than fixed priority — either source can be stale. Older nous entries may have been superseded by newer ones or by changes that occurred after they were written. When the truth is ambiguous, investigate the actual project state through Explore agents or direct file reads to resolve the conflict.

For each saved file found in Step 1, scan its content for:

**Direct contradictions**
- Saved guidance says X, but this session demonstrated or confirmed Y
- Example: CLAUDE.md says "run tests with `pytest -x`" but the session discovered the project migrated to vitest

**Superseded information**
- Guidance that was accurate when written but no longer reflects current state
- Example: "API rate limit is 100 req/min" when the provider increased it to 1000 req/min

**Stale references**
- File paths, command flags, API patterns, or tool names that have changed
- Example: a SKILL.md referencing a script that was renamed or moved

**Redundant or drifted entries**
- Multiple entries covering the same topic with slightly different (potentially conflicting) advice
- Consolidate into the most accurate version

**Outdated "current state"**
- Saved content describing pipeline state, task status, or progress that has since advanced
- Example: "migration to v3 API is in progress" when the migration completed this session

For each issue found, record:
1. The file and approximate location of the stale content
2. What it currently says (quote the relevant text)
3. What it should say based on current session knowledge
4. Confidence level: **certain** (session directly proved it wrong) vs. **likely** (strong inference)

Only flag items with "certain" confidence for automatic correction. Present "likely" items for user review because false corrections are worse than stale content.

## Step 3: Route Findings to Destinations

Classify each finding into exactly one destination:

**Project SKILL.md** (`.claude/skills/<project-name>/SKILL.md`)
- Project-specific conventions, patterns, and architecture
- Domain terminology and concepts unique to this codebase
- Integration patterns and API usage specific to this project
- "How this project works" knowledge
- Trigger: information a new Claude session needs to understand the project deeply

**Project CLAUDE.md** (at the appropriate level in the hierarchy)
- Build/test/lint commands discovered or corrected
- Code style patterns and conventions
- Environment setup and configuration
- Workflow instructions and gotchas
- Trigger: actionable instructions that help Claude work correctly in this repo
- Place items in the CLAUDE.md closest to the relevant code (subdirectory > root)

**Project .claude.local.md** (gitignored, personal per-project)
- Personal workflow preferences specific to this project
- Local environment quirks (paths, tokens, tool versions)
- Trigger: project-specific but shouldn't be committed to git

**User CLAUDE.md** (`~/.claude/CLAUDE.md`)
- Cross-project personal preferences and patterns
- General tool usage patterns (git, CLI, editor)
- Communication style preferences
- Trigger: applies to ALL projects, not just this one

**Corrections** (from Step 2b reconciliation)
- Route corrections to the file where the stale content lives — corrections are in-place updates, not new additions
- A correction replaces or removes existing content rather than appending
- Corrections take priority over additions when they cover the same topic, because adding content that contradicts something left uncorrected creates conflicting guidance

**Nous entries** (`.claude/nous/` JSONL files, if aeo-nous is enabled)
- When a nous entry is demonstrably stale or superseded, it can be corrected
- Correction approach: append a new entry with current timestamp that supersedes the stale one, rather than editing or deleting the original — this preserves correction history
- Match the exact format of existing entries in the target file — read a recent entry and replicate its field structure

## Step 4: Refine Content

Before proposing any additions or corrections, invoke the `aeo-claude:opus-prompting` skill and apply its patterns to refine all proposed content for clarity and natural instruction-following.

Each proposed item should:
- Read naturally, not as robotic imperatives
- Include rationale (`because...` explanations)
- Stay concise -- one line per concept where possible
- Use the format: `pattern or command` -- brief description with rationale

## Step 5: Create or Update Project Skill (if needed)

If findings include project-specific knowledge AND no project skill exists yet:

Invoke the `aeo-claude:claude-skill-creator` skill and follow its guidance to create `.claude/skills/<project-name>/SKILL.md`:

```yaml
---
name: <project-name>
description: >
  <Project-name> project conventions, architecture, and domain patterns.
  Use when working in this codebase to understand project-specific context
  that isn't captured in CLAUDE.md files.
---
```

The skill body should contain:
- A brief project overview (1-2 sentences)
- Sections organized by topic (architecture, conventions, domain, integrations)
- Only content classified as "Project SKILL.md" in Step 3

If the project skill already exists, propose additions to the appropriate section.

## Step 6: Present Proposals

Group proposals by destination. For each:

```
### Destination: <path>

**Action**: Create | Update

**Findings** (N items):

1. **Signal**: [what happened in the session]
   **Proposed addition**:
   ```diff
   + <the line to add>
   ```
   **Rationale**: [why this is durable and useful]
```

For corrections (from Step 2b), use before/after format:

```
### Corrections: <path>

1. **Stale content** (line ~N):
   ```diff
   - <what it currently says>
   + <what it should say>
   ```
   **Reason**: [why the current version is wrong, citing session evidence]
   **Confidence**: certain | likely
```

For nous entry corrections, use supersession format:

```
### Nous corrections: <jsonl file path>

1. **Stale entry** (identified by its timestamp field):
   **Original**: "<content of stale entry>"
   **Superseded by**: "<proposed new entry content>"
   **Reason**: [why the original is wrong]
   **Confidence**: certain | likely
```

Show all proposals before applying anything. Present corrections before additions, because fixing wrong guidance is higher priority than adding new guidance.

## Step 7: Apply with Approval

Ask the user which proposals to apply. Accept:
- "all" -- apply everything
- "skip <destination>" -- skip a whole destination
- Numbered selections -- apply specific items only
- "none" -- discard all (session still analyzed, just not persisted)

For approved changes:
- Use Edit tool to add to existing files (preserve structure, append to relevant sections)
- Use Write tool only for new files (project SKILL.md creation)
- Never rewrite or reorganize existing content -- only add new entries or apply targeted corrections from Step 2b
- For nous corrections: append a new JSONL entry to the appropriate file, matching the schema of existing entries in that file

## Constraints

- One concept per line -- compound entries get split
- Never remove existing content without explicit user request or an approved Step 2b correction
- Never add obvious/generic guidance (things any Claude session would know)
- Never duplicate content already present in the target file
- Project SKILL.md items must be genuinely project-specific, not general best practices
- User CLAUDE.md items must genuinely apply across all projects
- If nothing worth persisting was found, say so and stop -- don't force findings
- Corrections to existing content take priority over new additions -- fix what's wrong before adding more
- Only auto-apply corrections with "certain" confidence -- present "likely" corrections for user review
- When correcting, preserve the surrounding structure and style of the target file
- If a correction makes another existing entry redundant, propose removing the redundant entry too
- When correcting nous entries, append rather than edit or delete — preserve correction history
