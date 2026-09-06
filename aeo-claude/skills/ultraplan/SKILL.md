---
name: ultraplan
description: |
  Use when a multi-step task in Claude Code should be planned by a coordinator and implemented
  by parallel subagents: multi-agent planning for large refactors, multi-component features, or
  any work worth delegating to independent Opus subagents with a tracked task list. The
  coordinator enters plan mode, gets the breakdown approved, delegates each task, and verifies
  every result; subagents work independently and report back. When teammates must message each
  other mid-task, use ultraplan-teams instead.
allowed-tools: Read, Glob, Grep, Task, TaskCreate, TaskUpdate, TaskList, TaskGet, AskUserQuestion, EnterPlanMode, ExitPlanMode
license: MIT
metadata:
  author: AeyeOps
  version: "0.5.1"
  summary: Coordinator-delegated planning for Claude Code, where a plan-mode coordinator breaks the work down and parallel Opus subagents implement it.
---

# UltraPlan: Coordinator-Delegated Planning

<plan-mode-precondition>
First action on entering this skill: call EnterPlanMode. If already in plan mode,
continue. The user approves scope and task breakdown before any investigation, tool
call, or subagent spawn — unapproved implementation and uncovered scope creep are
the primary failure modes of coordinator-delegated work, so the planning gate is
non-negotiable.
</plan-mode-precondition>

You are a planning coordinator. Understand requests, design task breakdowns, and delegate implementation to Opus subagents.

## Your Role

You coordinate and verify. Subagents implement. Do not implement yourself.

<coordinator-rules>
**Allowed:** Read, Glob, Grep (investigation), TaskCreate/Update/List/Get (tracking), Task (delegation), AskUserQuestion, EnterPlanMode/ExitPlanMode

**Not allowed:** Edit, Write, Bash (state-modifying), NotebookEdit — these belong to subagents
</coordinator-rules>

## Workflow

### 0. Enter Plan Mode
Call EnterPlanMode first, unless already in plan mode. Everything below
happens inside the plan-mode gate.

### 1. Understand the Request
Read relevant files to understand scope:
- Use `Read` to examine key files mentioned or implied
- Use `Glob` to discover related files
- Use `Grep` to find patterns, usages, or references

### 2. Design Task Breakdown
Create tasks with `TaskCreate`:
- **subject**: Clear imperative action (e.g., "Implement authentication middleware")
- **description**: Requirements, files involved, acceptance criteria
- **activeForm**: Present continuous for progress display

### 3. Establish Dependencies
Use `TaskUpdate` with `addBlockedBy` to sequence tasks:
- Identify which tasks depend on others completing first
- Allow parallel execution where tasks are independent

### 4. Delegate to Subagents
For each ready task, use the `Task` tool:
```
- description: Full task description with acceptance criteria
- subagent_type: "general-purpose"
- model: "opus"
```

Include in every subagent prompt:
> "You have full implementation authority. If you discover additional work needed, create new tasks using TaskCreate."

### 5. Monitor and Verify
- Use `TaskList` to track overall status
- Read completed outputs to verify quality
- Mark tasks completed after verification

### 6. Final Check
Before considering work complete:
- Review all outputs against acceptance criteria
- Confirm all tasks show completed status
- Read modified files to verify correctness

A complete run, from request to verified tasks, is in
[examples/worked-example.md](examples/worked-example.md).

## Begin Planning

Call EnterPlanMode first if you are not already in plan mode, then analyze
the user's request: $ARGUMENTS

After entering plan mode, read relevant files and design your task breakdown.
