# Gantt Charts

**Keyword:** `gantt`

**Purpose:** Project timeline and task scheduling.

## Table of Contents
- [Basic Syntax](#basic-syntax)
- [Task Definition](#task-definition)
- [Sections](#sections)
- [Milestones](#milestones)
- [Vertical Markers](#vertical-markers)
- [Date Configuration](#date-configuration)
- [Excluding Dates](#excluding-dates)
- [Task States](#task-states)
- [Compact Mode](#compact-mode)
- [Key Limitations](#key-limitations)
- [When to Use](#when-to-use)

## Basic Syntax

```mermaid
gantt
    title Project Schedule
    dateFormat YYYY-MM-DD
    section Phase 1
    Task 1: task1, 2025-01-01, 30d
    Task 2: task2, after task1, 20d
```

## Task Definition

**Syntax:** `Task name: [taskId], [startDate/dependency], [duration/endDate]`

**Duration formats:**
- `30d` - 30 days
- `2w` - 2 weeks
- `1m` - 1 month

**Dependencies:**
```mermaid
gantt
    Task A: a1, 2025-01-01, 10d
    Task B: a2, after a1, 5d
    Task C: a3, after a1 a2, 3d
```

## Sections

```mermaid
gantt
    section Planning
    Requirements: plan1, 2025-01-01, 10d
    Design: plan2, after plan1, 5d

    section Development
    Implementation: dev1, after plan2, 20d
    Testing: dev2, after dev1, 10d
```

## Milestones

```mermaid
gantt
    Task A: 2025-01-01, 10d
    Milestone 1: milestone, 2025-01-11, 0d
```

## Vertical Markers

```mermaid
gantt
    dateFormat YYYY-MM-DD
    Task: 2025-01-01, 30d
    vert Deadline: 2025-01-15
```

## Date Configuration

```mermaid
gantt
    dateFormat YYYY-MM-DD
    axisFormat %b %d
    tickInterval 1week

    Task: 2025-01-01, 14d
```

**Date formats:** Use JavaScript date format tokens
- `%Y-%m-%d` - 2025-01-15
- `%b %d` - Jan 15
- `%d/%m/%Y` - 15/01/2025

## Excluding Dates

```mermaid
gantt
    excludes weekends
    excludes 2025-12-25

    Task: 2025-01-01, 10d
```

## Task States

```mermaid
gantt
    Task A: done, a1, 2025-01-01, 5d
    Task B: active, a2, after a1, 3d
    Task C: crit, a3, after a2, 5d
    Task D: a4, after a3, 2d
```

States: `done`, `active`, `crit` (critical)

## Compact Mode

```yaml
---
displayMode: compact
---
gantt
    Task A: 2025-01-01, 10d
    Task B: 2025-01-01, 5d
```

## Key Limitations
- Date parsing depends on `dateFormat` setting
- Excluded dates extend tasks rightward
- Complex dependencies may require manual calculation

## When to Use
- Project planning
- Sprint scheduling
- Resource allocation
- Milestone tracking
