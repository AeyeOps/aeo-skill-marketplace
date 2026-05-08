# How-to guide mode — full reference

A how-to guide is a **goal-oriented procedure** for someone who already knows the basics. The reader has a problem; you give them a solution that works in real conditions, not just the happy path. Shortest reasonable distance from problem to solution.

## Section template

```markdown
# How to [achieve specific goal]

> **Goal**: [Specific outcome the user wants to achieve]
> **Use case**: [When someone would need this]
> **Time required**: [Realistic estimate]

## Prerequisites

Before starting, you should:
- Be familiar with [basic concepts]
- Have [specific tools] installed and configured
- Have access to [required resources]

## Problem context

[Brief description of the real-world problem this solves. One paragraph max — the reader is here because they already have the problem.]

## Solution overview

We'll solve this by [brief approach description]:

1. [High-level step 1]
2. [High-level step 2]
3. [High-level step 3]

**Why this approach**: [One sentence on the rationale. If this needs more than a sentence, the rationale belongs in an explanation doc and you should link to it instead.]

## Step 1: [Action-oriented task]

[Imperative voice: "Set the X to Y", "Run the migration", not "You should set..."]

```[language]
# Specific, working example
[practical code]
```

**Expected result**: [What success looks like at this step]

## Step 2..N: [Next actions]

Continue with the next logical task. Each step verifiable.

```bash
# Commands that work in real environments
[actual commands with realistic parameters]
```

**Verify it worked**: [How to check this step succeeded]

## Verification

Confirm the whole solution works:

```bash
# Test commands
[verification steps]
# Expected output: [what indicates success]
```

## Troubleshooting

**Problem**: [Common failure scenario]
**Symptoms**: [How user knows this is the issue]
**Cause**: [Why this happens]
**Solution**: [How to fix it]

```bash
# Fix commands
[specific solution]
```

[Repeat for the 2-4 most common failure modes. If a problem is rare, leave it out — the reader's time is the budget.]

## Alternative approaches

### For [different scenario]

If you're working with [specific conditions], consider:

**Approach**: [Alternative method]
**Pros**: [Benefits]
**Cons**: [Limitations]
**When to use**: [Specific conditions that favor this]

## Best practices

- ✅ [Practical tip for success]
- ✅ [Security/performance consideration]
- ⚠️ [Important warning about a common mistake]

## Related tasks

- [Related task](../how-to/[related-task].md)

## Further reading

- **New to [system]?** → `../tutorials/getting-started-[topic].md`
- **Need technical details?** → `../reference/[component].md`
- **Want to understand why?** → `../explanation/[concept].md`
```

## Quality checklist

- [ ] **Specific goal** — concrete problem being solved, not "general guidance for X"
- [ ] **Stated prerequisites** — what the reader needs to know to follow along
- [ ] **Working solution** — commands and code that execute successfully in a realistic environment
- [ ] **Verification steps** — how to confirm success at each step
- [ ] **Troubleshooting** — the 2-4 most common failure modes covered
- [ ] **Real-world focused** — addresses how this actually plays out, not just the demo
- [ ] **Imperative voice** throughout

## Anti-patterns

| Anti-pattern | What it looks like | Fix |
|--------------|--------------------|----|
| Academic exercise | Solving problems no one actually has | Address real problems from actual usage |
| Tutorial disguise | Teaching concepts instead of solving the problem | Assume competence, focus on the practical solution, link to a tutorial for the basics |
| Reference manual | Explaining every option instead of solving the specific problem | Show one good solution, link to reference for full options |
| One true way | Not acknowledging that other approaches exist | Include "Alternative approaches" when the choice is non-obvious |
| Perfect-world solution | Solutions that only work in ideal conditions | Address real-world constraints and edge cases |

## Voice and register

- Imperative throughout: "Set", "Configure", "Run", not "You can set" or "It's possible to configure".
- Assume the reader knows the basics — don't pause to explain what `git` is, what an environment variable is, etc. State prerequisites and trust them.
- Trade-offs and warnings get one line each, not paragraphs. The reader is busy.

## Output

- **Path**: `docs/how-to/`
- **Filename**: kebab-case, lead with the action verb
  - `configure-[feature].md`
  - `integrate-[system].md`
  - `troubleshoot-[problem].md`
  - `migrate-[from]-to-[to].md`
  - `deploy-[target].md`
  - `optimize-[aspect].md`

## Common how-to categories

- **Setup and configuration** — environment setup, service config, integration config
- **Deployment and operations** — deployment strategies, monitoring/alerting setup, backup/recovery
- **Development workflows** — code review processes, testing strategies, CI/CD pipelines
- **Troubleshooting and debugging** — performance, error diagnosis, security incidents
- **Integration and migration** — data migration, third-party service integration, legacy migration

## Success and failure indicators

**Success**: Reader solves their specific problem efficiently, the solution works in real conditions, troubleshooting prevents support requests, the reader can adapt the solution to their context.

**Failure**: Solution doesn't work in practice, reader needs extensive additional research, problems arise that aren't covered in troubleshooting, the solution is too generic to be useful.
