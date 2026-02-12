---
name: epcc-explore
description: Explore phase of EPCC workflow - understand thoroughly before acting
version: 0.1.0
argument-hint: "[area-to-explore] [--deep|--quick|--refresh]"
---

# EPCC Explore Command

You are in the **EXPLORE** phase of the Explore-Plan-Code-Commit workflow. Your mission is to understand thoroughly before taking any action.

**Opening Principle**: High-quality exploration reveals not just what exists, but why it exists—enabling confident forward decisions without re-discovery.

**IMPORTANT**: This phase is for EXPLORATION ONLY. Do NOT write any implementation code. Focus exclusively on:
- Reading and understanding existing code
- Analyzing patterns and architecture
- Identifying constraints and dependencies
- Documenting everything in EPCC_EXPLORE.md

## Session Resume Detection

@reference/session-protocols.md

## Exploration Target
$ARGUMENTS

### Exploration Thoroughness

Parse thoroughness level from arguments:
- `--quick`: Fast surface-level exploration (key areas, basic patterns)
- `--deep` or `--thorough`: Comprehensive analysis (multiple locations, cross-referencing)
- **Default** (no flag): Medium thoroughness (balanced exploration)

## Autonomous Exploration Mode

This command operates as an **autonomous exploration agent**:

1. **Self-Directed Search**: Automatically tries multiple search strategies
2. **Comprehensive Coverage**: Systematically explores all relevant areas
3. **Pattern Recognition**: Identifies and documents coding patterns and conventions
4. **Persistent Investigation**: Doesn't give up easily - tries different approaches
5. **Complete Report**: Delivers comprehensive exploration report in EPCC_EXPLORE.md

## When to Ask Questions

This phase is designed to be **autonomous** - explore independently without frequent user interaction.

**Only ask when**: Exploration target genuinely unclear, multiple conflicting patterns and unclear which is canonical, completely blocked after trying multiple strategies.

**Don't ask when**: First search doesn't find something (try alternatives first), multiple patterns exist (document all), code is messy (document what you find).

**Problem-Solving Approach (instead of asking):**
1. Try multiple search strategies (different terms, patterns, directories)
2. Follow the trail (check imports, related files)
3. Document uncertainty ("Pattern X found in 3 places, Pattern Y in 2 places")
4. Note gaps ("No auth code found after checking [list of searches]")

## Handling Ambiguity

**EXPLORE phase is autonomous by design - avoid asking questions unless truly blocked.**

Before escalating to AskUserQuestion, ensure you've exhausted autonomous exploration:
- Try broad searches, platform-specific patterns, configuration checks
- If multiple patterns found: Document all, note which appears canonical
- If nothing found: Document what you searched, note this appears greenfield

## Exploration Strategy

**BE SYSTEMATIC AND THOROUGH:**

1. **Try multiple search approaches** if first attempt yields no results
2. **Follow the trail**: Found a relevant file? Check imports/dependencies
3. **Be comprehensive**: Don't stop at first match
4. **Document as you go**: Track what you've searched and found

## Exploration Objectives

1. **Review Project Instructions**: Check for CLAUDE.md files
2. **Map the Territory**: Project structure and architecture
3. **Identify Patterns**: Coding conventions and design patterns
4. **Discover Constraints**: Technical, business, and operational limitations
5. **Review Similar Code**: Existing implementations to learn from
6. **Assess Complexity**: Scope and difficulty
7. **Document Dependencies**: Internal and external
8. **Evaluate Test Coverage**: Testing approaches and gaps

## Exploration Methodology

@reference/pattern-recognition.md

## Thoroughness-Based Heuristics

See pattern recognition methodology above for thoroughness-specific guidance.

## Exploration Deliverables

### Output File: EPCC_EXPLORE.md

@reference/exploration-report-templates.md

## Exploration Best Practices

### DO:
- Try multiple search strategies if first attempt fails
- Read CLAUDE.md files first - they contain critical requirements
- Document your search process - helps identify gaps
- Follow the trail - check imports and related files
- Be comprehensive - explore multiple examples of patterns
- Note what you DON'T find - gaps are important information
- Provide file references with specific line numbers

### DON'T:
- Give up after one search - try different terms and patterns
- Skip CLAUDE.md - missing project requirements causes rework
- Assume patterns - verify with actual code examples
- Ignore test files - they reveal intended behavior
- Write code - this is exploration only
- Leave gaps undocumented

## Common Pitfalls

- **Giving Up After First Search Fails**: Try 3-5 search strategies before concluding
- **Hitting File Count Instead of Understanding**: Stop when pattern is understood
- **Skipping CLAUDE.md Files**: Read CLAUDE.md first (critical requirements)
- **Documenting Only "Happy Path"**: Document edge cases, error handling, constraints
- **Treating Exploration as Code Review**: Document what exists objectively
- **Asking User to Clarify Obvious Search Targets**: Try patterns first

## Second-Order Convergence Warnings

Even with this guidance, you may default to:
- Stopping at first pattern match (read 3-5 examples)
- Reading exactly N files per mode (stop when objectives met)
- Asking about every ambiguity (document multiple patterns, let PLAN decide)
- Documenting only implementation files (tests, configs, docs reveal critical context)
- Treating modes as rigid procedures (adapt to actual codebase complexity)

## Session Exit: Progress Logging

See exploration report templates above for session exit and progress logging format.

## Remember

**Time spent exploring saves time coding!**

**DO NOT**: Write code, create files, implement features, fix bugs, or modify anything

**DO**: Be persistent, try multiple approaches, follow the trail, document thoroughly, save to EPCC_EXPLORE.md
