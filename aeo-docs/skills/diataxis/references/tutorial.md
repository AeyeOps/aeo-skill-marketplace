# Tutorial mode — full reference

A tutorial is a **lesson, not a manual**. The reader is a beginner; you are leading them by the hand to a concrete, useful first achievement. Success is measured by *can they finish*, not by how much they learn along the way.

## Section template

```markdown
# Getting Started with [System]: Build Your First [Concrete Thing]

**What you'll learn**: By the end of this tutorial, you'll have [specific achievement] and be ready to [next logical step].

**Time required**: [X] minutes
**Prerequisites**: [Minimal — only the absolute essentials]

## What you'll build

[Describe the concrete, useful thing they'll create. Never a "toy" example — pick something that resembles real-world usage.]

### Why this tutorial matters

[One paragraph explaining why this example represents real work, not a contrived exercise.]

## Before we start

### Install the tools

[Complete installation instructions with verification steps.]

### Verify your setup

```bash
# Test command that should work
[command]
# Expected output: [exact output they should see]
```

**Checkpoint**: You should see [specific result]. If not, [troubleshooting link].

## Step 1: [First concrete action]

Let's start by [specific action]:

```[language]
# Complete code they can copy-paste
[working example]
```

**What just happened**: [Brief explanation of the immediate result, not how it works under the hood. Save the "how" for the explanation doc.]

**Checkpoint**: You should see [expected output]. This means [what success looks like].

## Step 2: [Build on previous step]

Now let's [next logical action]:

```[language]
# Add this to your existing code
[incremental addition]
```

**Try it**: [Command to run/test]
**Expected result**: [Exact output or behavior]

## Step 3..N: [Continue building]

Each step builds on the previous. Every step has its own checkpoint.

## What you've accomplished

✓ [Specific achievement 1]
✓ [Specific achievement 2]
✓ [Specific achievement 3]

## Next steps

- **Solve real problems** → `../how-to/[task].md`
- **Look up details** → `../reference/[component].md`
- **Understand the design** → `../explanation/[concept].md`

## Troubleshooting

**Problem**: [Common issue beginners face]
**Solution**: [Simple fix with explanation]

[Link to comprehensive troubleshooting](../how-to/troubleshoot-[topic].md)
```

## Quality checklist

- [ ] **Clear learning objective** — "By the end, you will..."
- [ ] **Concrete deliverable** — something real and useful, not a toy
- [ ] **Complete examples** — every code block works as written when copy-pasted into a fresh environment
- [ ] **Verification at each step** — reader knows immediately whether the step worked
- [ ] **Beginner-safe** — anticipates and prevents common mistakes
- [ ] **Single linear path** — no "or you could do X" branches
- [ ] **Tested fresh** — works on a clean system, not just the author's machine

## Anti-patterns

| Anti-pattern | What it looks like | Fix |
|--------------|--------------------|----|
| Museum piece | Tutorial builds something no one would actually use | Choose real, practical examples that solve actual problems |
| Explanation trap | Stopping to explain concepts mid-step | Brief "what just happened" notes; link out to explanation docs |
| Reference dump | Listing all options instead of one guided path | Show one good path; link to reference for full options |
| Cliff drop | Sudden complexity jump without preparation | Gradual progression with clear checkpoints |
| Debugging adventure | Including troubleshooting in the learning path | Design to prevent errors; troubleshooting goes in how-tos |
| Multiple-ways trap | "You can do this in three different ways..." | Pick one. Mention alternatives only at the very end if at all |

## Voice and register

- Inviting and patient. The reader is uncertain; reassure them with checkpoints.
- "We" works ("Now we'll add a database"); avoid "you should already know..." (assumes too much).
- Celebrate small victories at major milestones, but don't over-pad — every word fights for the reader's attention.
- When the reader gets something working, briefly name what it means ("You now have a working API server") so they internalize the achievement.

## Output

Path and filename conventions are in the parent SKILL.md ("Output conventions across all four modes"). For tutorials specifically, output goes to `docs/tutorials/`.

## Success and failure indicators

**Success**: A beginner can complete the tutorial without external help, leaves with confidence to try real tasks, knows what they built and why it's useful, has a natural next step.

**Failure**: User gets stuck, examples don't work, completes the tutorial without understanding what they did, or has no idea what to do next.
