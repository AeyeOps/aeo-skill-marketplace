# Nous Lens Prompt Realignment

Assessment and action plan for fixing domain bleed and off-project contamination in the nous extraction and reconciliation prompts.

## Status

Assessment complete. Implementation not started.

## Problem Statement

The two nous extraction lenses (learnings, knowledge) and the reconciliation command have prompt-level deficiencies that produce measurable misalignment between intended domains and actual outputs. The reconciliation pass compensates for extraction-time errors, but this is wasteful — the extraction prompts should produce clean output that reconciliation only needs to maintain.

## Measured Deficiencies

### Off-project contamination

Both lenses extract content about work done during a session regardless of whether that work relates to the project whose nous store receives the entries. The extraction runs against this project's store (`/opt/aeo/aeo-skill-marketplace/.claude/nous/`) but sessions may work on unrelated targets.

Measured contamination rate in unscored (recent) entries:
- Engram (learnings): 29 of 30 entries (97%) target off-project paths (`/opt/vpatch.sh`, `/opt/solve-for-wsl-voice.md`, `~/.claude/keybindings.json`)
- Cortex (knowledge): 45 of 58 entries (78%) target off-project paths

Root cause: `build_extraction_prompt()` in `base.py` injects `<project>{current.cwd}</project>` into `<session_context>`, but neither `LEARNINGS_PROMPT` nor `KNOWLEDGE_PROMPT` references this field or constrains extraction scope to it. Note: `current.cwd` and `current.workspace.project_dir` are currently identical but semantically distinct — `project_dir` is the git root while `cwd` could be a subdirectory. The scope constraint should work with either value since it references "directory tree."

### Learnings ↔ knowledge lens bleed

Direction: knowledge → learnings (facts misclassified as behavioral deltas). The reverse direction (learnings → knowledge) is not observed.

8 of 19 scored learnings entries at w >= 0.25 (42%) are declarative facts:

```
L3:  "AWS CLI --case-conflict flag does not accept 'rename'"       → declares what a flag accepts
L4:  "AWS SSO export-credentials does not support --format fish"    → declares valid values
L15: "Plan mode auto-assigns a new slug-based file per session"     → describes system behavior
L18: "claude -p invocation patterns for skill scripts"              → reference catalog
L22: "Entries with w: null are NOT bugs"                            → explains system behavior
L23: "Subagents do NOT carry agent_id or agent_type fields"         → states a system fact
L24: "nous-stop-guard.sh line 78 uses -gt"                         → bug report (what IS)
L25: "Claude Code's auto-compact fires before nous-stop-guard"     → system interaction fact
```

Pattern: all 8 start with a noun/proper name and use declarative framing ("X does not Y", "X uses Y", "X auto-assigns"). Correctly classified learnings start with imperative framing ("When X, do Y", "Before X, check Y", "Do not X").

### Extraction model

Both extraction and reconciliation run on Opus (`EXTRACTION_MODEL = "opus"` at `nous.py:90`, `model: opus` in `aeo-reconcile.md` frontmatter).

### Contributing prompt deficiencies

Six deficiencies compound to produce the misalignment above.

#### 1. No project scope constraint

Neither prompt tells the extractor to limit output to the project path. The knowledge prompt says "this project" but does not define what "this project" means or tie it to the `<project>` field in session_context. The learnings prompt does not mention project scope at all.

#### 2. "Look for" categories in learnings prompt use noun phrases that invite factual content

```
Current:
- Edge cases: Unexpected behaviors that change how to approach a task
- New patterns: Approaches that should replace previous defaults
```

"Edge cases" as a noun phrase invites the extractor to describe the edge case (fact) rather than the workaround (behavioral delta). "AWS --case-conflict doesn't accept rename" is extracted as an "edge case" because it was unexpected, but the entry describes what IS, not what to DO.

Compare with the action-oriented categories that produce correctly classified entries:
```
- Corrections: User redirected Claude's approach          → "When X, do Y instead"
- Rules: User stated a principle beyond this task         → "Always/Never X"
```

#### 3. No cross-lens awareness

Each extractor runs in isolation against the same transcript. Neither prompt mentions the other lens exists. When the learnings extractor encounters a valuable fact, it captures it rather than trusting the knowledge extractor to handle it. This produces dual extraction and directional lens bleed.

#### 4. Asymmetric exclusion fences

The knowledge prompt has a concrete exclusion:
```
Not knowledge: instructions on what to do (corrections, workarounds, preferences, process rules).
```

The learnings prompt has one sentence:
```
Capture what to do differently, not what exists. System facts belong in knowledge.
```

No examples, no enumeration of what "system facts" means, no decision aid for borderline cases.

#### 5. `suggested_target` hints in learnings prompt use knowledge vocabulary

The learnings prompt's target guidance says `"skills/**/*.md for domain knowledge"` and `"kb/*.md for project facts"`. These are knowledge-domain terms — "domain knowledge" and "project facts" are literally the other lens's domain. While `suggested_target` is downstream of the extraction decision (the model has already decided to extract before it picks a target), the vocabulary creates a semantic association that primes the extractor to consider knowledge-type content as in-scope for learnings.

#### 6. No litmus test for borderline entries

Neither prompt provides a binary decision test the extractor can apply to ambiguous items. The extractor must infer domain boundaries from brief positive descriptions, which fails on boundary cases.

### Reconciliation gap

The `aeo-reconcile.md` detection criteria cover: Stale, Misdirecting, Conflicting, Duplicated, Lens bleed, CLAUDE.md correction. They do NOT cover **off-project** entries as an explicit category. The reconciliation agents caught off-project entries in practice (the learnings agent classified 17 voice entries as "Off-project / wrong lens") but this was emergent behavior — the criterion is not in the prompt. Making it explicit improves reliability.

## What Does Not Need Changing

These elements are correctly designed and should be preserved:

- Output format enforcement sections in both prompts — strict JSONL constraints work well on Opus
- Schema differentiation — `category` field present in knowledge, absent in learnings — reinforces domain separation at the data model level
- The reconcile agent prompt structure — workflow steps, weight rubric reference, applying rules, verification ledger, lift-and-shift mechanics
- The `build_extraction_prompt()` template structure in `base.py` — XML-tagged sections are well-aligned with Opus prompt processing

## Completed: WEIGHT_RUBRIC constant propagation

Band boundaries in `WEIGHT_RUBRIC` now derive from named constants instead of hardcoded floats. Adjusting any constant automatically reshapes adjacent bands:

```python
DISCARD_THRESHOLD = 0.15       # discard band ceiling
NARROW_FLOOR = 0.25            # narrow band starts here
VERIFICATION_GATE = 0.45       # moderate+ bands require tool-verified confirmation
SOLID_FLOOR = 0.65             # solid band starts here
FOUNDATIONAL_FLOOR = 0.85      # foundational band starts here
```

The verification gate rule text and narrow band ceiling cap also reference these constants via f-string. Location: `aeo-nous/hooks/nous.py:102-112`.

## Action Plan

### Phase 1: LEARNINGS_PROMPT (highest impact)

The learnings prompt has the worst misalignment (97% off-project + 42% lens bleed). Six changes, applied to `LEARNINGS_PROMPT` in `aeo-nous/hooks/lenses/learnings.py`:

#### 1a. Add project scope constraint

After the opening question, before "Look for", add a scope gate that references the `<project>` field from `<session_context>`:

```
Only extract learnings relevant to the project at the path in <project>. If session work touched
files, tools, or systems outside this project's directory tree, those learnings are out of scope
even if they occurred during this session. The project store should only contain guidance that
helps future sessions working on THIS project.
```

#### 1b. Add cross-lens awareness

After the scope constraint, add:

```
A parallel knowledge worker extracts factual discoveries from this same transcript. You do not
need to capture system facts as learnings. If something describes what IS (a property, behavior,
or state of a system) rather than what to DO (a changed approach, a preference, a rule), the
knowledge worker will handle it.
```

#### 1c. Reframe "Look for" categories as action-oriented

Replace noun-phrase categories with action-phrase categories:

```
Current                                          → Proposed
Edge cases: Unexpected behaviors that             → Edge case workarounds: an unexpected behavior
  change how to approach a task                     that requires a DIFFERENT APPROACH going forward
New patterns: Approaches that should              → Approach changes: a method that should REPLACE
  replace previous defaults                         a previous default — state what to do now
```

Add an imperative-framing test after the list:

```
Each entry should be expressible as an imperative: "do X", "avoid Y", "prefer X over Y",
"when X happens, do Y". If the entry reads as a declarative statement — "X is Y", "X does
not support Y", "X uses Y" — it belongs in knowledge, not learnings.
```

#### 1d. Strengthen exclusion fence

Replace the single-sentence exclusion with a concrete enumeration:

```
NOT learnings — leave these for the knowledge worker:
- CLI flag reference information (what flags exist, what values they accept)
- System behavior descriptions (how a tool/script/hook works internally)
- Bug reports that state what IS wrong without stating what to DO about it
- Architecture facts (what components exist, how they connect)
- Path/version/config inventories
```

#### 1e. Add litmus test

Before the output format section, add:

```
Boundary test — apply to every candidate entry:
1. "Does this describe a FACT about a system, or a RULE for how to behave?" → FACT = knowledge
2. "Does this tell future sessions WHAT TO DO or WHAT EXISTS?"              → WHAT EXISTS = knowledge
3. "Can this be phrased as an imperative without distorting it?"             → NO = knowledge
```

Note: an earlier draft used "Would this be true regardless of what happened this session?" as test 1. This produces false positives — many valid learnings are universally true ("When a user rejects an edit, test in bash first") yet are behavioral rules, not facts. The FACT-vs-RULE test directly targets the declarative/imperative distinction that separates the lenses.

#### 1f. Reframe `suggested_target` vocabulary

Replace knowledge-domain terms in the target hints:

```
Current                                          → Proposed
- skills/**/*.md for domain knowledge            → skills/**/*.md for workflow patterns
- kb/*.md for project facts                      → (remove — project facts belong in knowledge lens)
```

### Phase 2: KNOWLEDGE_PROMPT (moderate impact)

Three changes, applied to `KNOWLEDGE_PROMPT` in `aeo-nous/hooks/lenses/knowledge.py`:

#### 2a. Add project scope constraint

After the opening question, add:

```
Only extract knowledge about the project at the path in <project>. Personal environment details
(dotfiles, editor configs, user tools at other paths) and off-project system facts are out of
scope. The one exception: environment facts that directly affect how THIS project builds, runs,
or deploys.
```

#### 2b. Add cross-lens awareness

After the scope constraint, add:

```
A parallel learnings worker extracts behavioral deltas from this same transcript. If your entry
tells future sessions what to DO — prefer, avoid, always, never, use X instead of Y — it
belongs in learnings, not knowledge. Knowledge entries describe what EXISTS and how it WORKS.
```

#### 2c. Normalize empty-output framing

After "If nothing interesting was discovered", add:

```
Returning nothing is a correct, successful outcome when the transcript contains no
project-relevant discoveries. Do not force extractions to avoid returning empty.
```

### Phase 3: AEO-RECONCILE.MD (low impact, additive)

One change, applied to the `<detection-criteria>` section in `aeo-nous/commands/aeo-reconcile.md`:

#### 3a. Add off-project detection criterion

Add to the detection criteria list:

```
- **Off-project** — entry describes facts or guidance about systems, tools, or files outside
  the project scope. Check `suggested_target` paths against the project root — targets outside
  the project tree are strong signals. These waste injection budget and dilute project-specific
  context.
```

## Future consideration: few-shot boundary examples

Research from Anthropic's prompting guidance identifies few-shot examples (particularly boundary cases) as the highest-leverage tool for classification consistency. One example showing "this looks like a learning but is actually knowledge" would reinforce the litmus test and exclusion fence. However, examples cost 50-100 tokens each in the `--print` prompt that already competes with transcript length for context budget. If the prose-based changes in Phases 1-2 don't reduce lens bleed below 10%, adding 1-2 boundary examples is the next step.

## Verification

After implementing, run a test extraction on a session transcript that contains mixed project and off-project work. Compare extraction output against the same transcript with the current prompts. Expected improvements:
- Off-project entries drop from >75% to <10% of extractions
- Declarative facts in the learnings store drop from ~42% to <10%
- Knowledge store maintains current quality (no regression)

Run a reconciliation pass on the updated stores. Off-project entries should now appear only rarely, and lens bleed moves should be minimal.

## References

- Lens prompt files: `aeo-nous/hooks/lenses/learnings.py`, `aeo-nous/hooks/lenses/knowledge.py`
- Prompt assembly: `aeo-nous/hooks/lenses/base.py:build_extraction_prompt()`
- Reconcile command: `aeo-nous/commands/aeo-reconcile.md`
- Extraction model: `aeo-nous/hooks/nous.py:90` — `EXTRACTION_MODEL = "opus"`
- Weight rubric: `aeo-nous/hooks/nous.py:WEIGHT_RUBRIC`
- Signal models: `aeo-nous/hooks/lenses/models.py` (LearningSignal, KnowledgeSignal)
