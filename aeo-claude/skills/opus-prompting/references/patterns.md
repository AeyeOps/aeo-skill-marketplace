# Opus 4.5 Pattern Transformations

Comprehensive reference of deprecated patterns and their Opus 4.5 equivalents.

## Table of Contents

1. [Aggressive Language](#1-aggressive-language)
2. [Think Variants](#2-think-variants)
3. [Tool Invocation](#3-tool-invocation)
4. [Formatting](#4-formatting)
5. [Context and Motivation](#5-context-and-motivation)
6. [Over-Specification](#6-over-specification)
7. [Verbosity](#7-verbosity)
8. [XML Structure](#8-xml-structure)

---

## 1. Aggressive Language

Opus 4.5 is more responsive to system prompts. Aggressive language that was needed to ensure compliance in earlier models now causes over-triggering.

### Before/After Examples

```
# Before
CRITICAL: You MUST always validate user input before processing.
You MUST NEVER expose internal error messages to users.
IMPORTANT: ALWAYS check authentication before accessing resources.

# After
Validate user input before processing.
Avoid exposing internal error messages to users.
Check authentication before accessing resources.
```

```
# Before
REQUIRED: You MUST format all dates as ISO 8601.
NEVER use relative dates like "yesterday" or "next week".

# After
Format dates as ISO 8601 for consistency.
Prefer absolute dates over relative terms like "yesterday".
```

### Transformation Rules

| Deprecated | Opus 4.5 Equivalent |
|------------|---------------------|
| `CRITICAL:` | (remove) |
| `IMPORTANT:` | (remove) |
| `REQUIRED:` | (remove) |
| `You MUST` | `You should` or (remove) |
| `MUST` | `should` or (remove) |
| `NEVER` | `avoid` or `prefer not to` |
| `ALWAYS` | `prefer to` or (remove) |
| `DO NOT` | `avoid` |

---

## 2. Think Variants

When extended thinking is disabled, Opus 4.5 is particularly sensitive to the word "think" and its variants.

### Before/After Examples

```
# Before
Think step by step about this problem.
Let's think through the implications carefully.
Think about what could go wrong here.

# After
Consider this problem systematically.
Evaluate the implications carefully.
Reflect on what could go wrong here.
```

```
# Before
Think carefully before making changes.
I want you to think deeply about the architecture.

# After
Evaluate carefully before making changes.
Analyze the architecture thoroughly.
```

### Transformation Rules

| Deprecated | Opus 4.5 Equivalent |
|------------|---------------------|
| `think step by step` | `consider systematically` |
| `think carefully` | `evaluate carefully` |
| `think through` | `analyze` |
| `think about` | `consider` or `reflect on` |
| `think deeply` | `analyze thoroughly` |
| `let's think` | `let's consider` |

---

## 3. Tool Invocation

Old prompts designed to ensure tool usage now cause over-triggering. Use gentler invocation language.

### Before/After Examples

```
# Before
You MUST use the search tool for every question about current events.
ALWAYS call the database API when the user asks about data.
CRITICAL: Never respond to code questions without using the linter.

# After
Use the search tool for questions about current events.
Call the database API when the user requests data lookups.
Run the linter for code questions to catch issues.
```

```
# Before
If the user mentions files, you MUST ALWAYS use the file_read tool first.

# After
For file-related questions, use file_read to examine the content.
```

### Transformation Rules

| Deprecated | Opus 4.5 Equivalent |
|------------|---------------------|
| `MUST use [tool]` | `use [tool]` |
| `ALWAYS call [tool]` | `call [tool] when...` |
| `You MUST invoke` | `invoke` or `use` |
| `CRITICAL: use` | `use` |
| `Never respond without using` | `Use [tool] to...` |

---

## 4. Formatting

Match your prompt's formatting style to your desired output style.

### Before/After Examples

```
# Before (markdown prompt, wants plain output)
## Instructions
- **Never** use markdown in responses
- Output should be plain text only

# After (plain prompt, wants plain output)
Instructions:
Avoid markdown in responses.
Output should be plain text only.
```

```
# Before (wants structured output but unstructured prompt)
give me a list of the top 5 programming languages

# After (structured prompt for structured output)
List the top 5 programming languages:
1. [language]: [brief description]
2. ...
```

### Principles

1. **Tell instead of forbid**: Say what you want, not what you don't want
2. **Match styles**: Prompt format influences response format
3. **Use XML tags**: `<smoothly_flowing_prose>` guides output style
4. **Remove markdown from prompts** to reduce it in responses

---

## 5. Context and Motivation

Opus 4.5 generalizes better when you explain why. Add "because..." to commands.

### Before/After Examples

```
# Before
Never use ellipses in your response.
Always include timestamps in logs.
Don't use contractions.

# After
Avoid ellipses because your response will be read by a text-to-speech engine.
Include timestamps in logs because they're essential for debugging production issues.
Avoid contractions because this is formal documentation.
```

```
# Before
Keep responses under 100 words.

# After
Keep responses under 100 words because users are reading on mobile devices with limited screen space.
```

### Pattern

```
[Command] because [reason/context].
```

---

## 6. Over-Specification

Opus 4.5 follows instructions more literally. Over-specified examples can constrain unnecessarily.

### Before/After Examples

```
# Before
When writing code, always include:
- A header comment with author, date, version
- Type annotations for every parameter
- Docstrings for every function
- Error handling for every operation
- Logging for every function entry/exit
- Unit tests for every public method

# After
Write clean, well-documented code with appropriate error handling.
Follow the project's existing conventions for comments and type annotations.
```

```
# Before
Format JSON responses exactly like this:
{
  "status": "success",
  "data": {
    "id": 123,
    "name": "example",
    "created_at": "2024-01-01T00:00:00Z"
  },
  "meta": {
    "version": "1.0",
    "timestamp": "..."
  }
}

# After
Return JSON with status, data, and optional meta fields.
```

### Principles

1. **Trust the model**: Opus 4.5 understands conventions
2. **Fewer examples**: One good example > many redundant ones
3. **Guidelines over templates**: Describe intent, not exact format
4. **Avoid exhaustive lists**: Summarize patterns instead

---

## 7. Verbosity

Opus 4.5 generates more tokens than some alternatives. Optimize for conciseness.

### Before/After Examples

```
# Before
I would like you to please help me with writing some code. Specifically, I need you to write a Python function that takes a list of numbers as input and returns the sum of all the numbers in that list. Please make sure to include proper documentation and error handling. Thank you!

# After
Write a Python function that sums a list of numbers. Include docstring and error handling.
```

```
# Before
Can you please explain to me in detail how the authentication system works in this codebase? I want to understand the full flow from when a user enters their credentials to when they receive an access token.

# After
Explain the auth flow: credentials to access token.
```

### Principles

1. **Direct requests**: Skip pleasantries in system prompts
2. **Concise instructions**: One sentence per instruction
3. **Avoid redundancy**: Don't repeat the same instruction differently
4. **Use lists**: Bullet points over prose for multiple items

---

## 8. XML Structure

XML tags help Opus 4.5 parse document structure, identify mutable vs. reference sections, and follow workflows. Use XML for any prompt that will be read by agents across sessions.

### Use Cases

| Use Case | Tags | Purpose |
|----------|------|---------|
| Session handoff | `<on-session-start>` | Prescriptive first steps for new agent |
| State tracking | `<current-state>`, `<blocked>`, `<can-proceed>` | Mutable sections agent should update |
| Reference data | `<reference>`, `<config>` | Static data agent should not modify |
| Workflows | `<workflow name="...">` | Named procedures to follow |
| Context | `<mission>`, `<principles>` | Why and how guidance |

### Before/After Examples

```
# Before (flat markdown - agent doesn't know what to update)
## Current Status
- Task A: done
- Task B: in progress
- Task C: blocked

## Reference Data
Company: Acme Corp
EIN: 12-3456789

# After (XML-structured - agent knows what's mutable)
<current-state updated="2024-11-29">
## Status
- [x] Task A
- [ ] Task B (in progress)
<blocked reason="waiting-on-user">
- [ ] Task C - needs API key
</blocked>
</current-state>

<reference>
## Company Info
| Field | Value |
|-------|-------|
| Company | Acme Corp |
| EIN | 12-3456789 |
</reference>
```

```
# Before (instructions buried in prose)
When you start a new session, first check the status file,
then look at what's blocked, then proceed with available tasks.

# After (structured startup)
<on-session-start>
1. Review `<current-state>` section
2. Check `<blocked>` items for dependencies
3. Pick from `<can-proceed>` items
4. Before context runs low, update `<current-state>`
</on-session-start>
```

### Common Tags

| Tag | Attributes | Purpose |
|-----|------------|---------|
| `<on-session-start>` | - | First steps for agent |
| `<current-state>` | `updated="date"` | Mutable progress tracking |
| `<blocked>` | `reason="..."` | Items waiting on external input |
| `<can-proceed>` | - | Actionable items |
| `<reference>` | - | Static data (don't modify) |
| `<workflow>` | `name="..."` | Named procedure |
| `<principles>` | - | How to approach work |
| `<known-issues>` | - | Gotchas and edge cases |
| `<commands>` | - | Copy-paste ready commands |

### Principles

1. **Semantic tags**: Name tags by purpose, not appearance
2. **Mutable vs. immutable**: Make clear what agent should update
3. **Attributes for metadata**: Use `updated`, `reason`, `name` attributes
4. **Nest logically**: `<blocked>` inside `<current-state>` shows relationship
5. **Reference in instructions**: Tell agent to "update `<current-state>`" explicitly

---

## Quick Reference Card

| Category | Pattern | Fix |
|----------|---------|-----|
| Aggressive | `MUST`, `NEVER`, `CRITICAL` | Remove or soften |
| Think | `think step by step` | `consider systematically` |
| Tools | `MUST use [tool]` | `use [tool] when...` |
| Format | Markdown prompt + plain request | Match styles |
| Context | Commands without why | Add `because...` |
| Over-spec | Exhaustive examples | Trust the model |
| Verbose | Long requests | Direct, concise |
| Structure | Flat markdown for agents | Use XML tags |
