---
description: Review and improve an existing Claude prompt — identifies over-specification, procedural anti-patterns, and missed agentic potential
argument-hint: "[path to prompt file or paste prompt text]"
---

# Review Claude Prompt

<purpose>
You are reviewing a prompt that will be consumed by Claude in an agentic context.
Your job is to identify where the prompt constrains the agent unnecessarily and
recommend changes that preserve intent while expanding the agent's freedom to
solve effectively.
</purpose>

<prep>
Invoke the `opus-prompting@aeo-claude` skill and read the behavioral properties
and pattern transformations. These define the anti-patterns you are looking for.
</prep>

<context>
Identify the prompt to review from `$ARGUMENTS` or conversation context. If
`$ARGUMENTS` is a file path, read it. If it is prompt text, use it directly.
If neither is provided, use AskUserQuestion to ask for the prompt.
</context>

<review-lens>

Evaluate the prompt through these lenses. For each, note whether the prompt
passes or has issues, with specific line-level examples.

**1. Content embedding vs file references**

Is the prompt injecting file contents that the agent could read from disk?
Every embedded file is wasted tokens and removed agency. The agent should
choose what to read and how deep to go.

- Passing: `Start with these files: {ASSESSMENT_PATH}, {JE_PATH}`
- Failing: `<assessment>\n{ASSESSMENT_YAML}\n</assessment>` where YAML is
  the entire file content

**2. Procedural prescription vs intent**

Is the prompt telling the agent HOW to investigate step by step, or WHAT
outcome to produce? Count sequential imperatives ("first... then... next...").
More than three suggests a procedure disguised as a prompt.

- Passing: "Investigate why the derived balance differs from the assessment"
- Failing: "First read the journal entries. Then trace account 1120 through
  each JE. Then compare the net balance against the assessment value. Then
  check if the prior year CB..."

**3. Exhaustive cause/category lists**

Does the prompt enumerate possible answers the agent should choose from?
These become menus the agent picks from rather than hypotheses it generates.
Remove the list and check: would the agent perform worse without it? If the
agent has domain knowledge (which Claude does), the list constrains more
than it helps.

- Passing: no list, or a brief "common causes include..." as orientation
- Failing: a numbered list of 6+ specific causes the agent is expected to
  evaluate one by one

**4. Aggressive language**

Search for MUST, NEVER, CRITICAL, IMPORTANT, ALWAYS, DO NOT, REQUIRED.
These cause overtriggering in Claude — the model over-indexes on the
directive and applies it even where inappropriate. Transform per
opus-prompting patterns.

**5. Output contract clarity**

Is the expected response format unambiguous? If the caller parses the output
programmatically, does the prompt make clear that only the structured block
should be returned? If a human reads it, is prose acceptable?

Ambiguity here causes the most common integration failure: the agent returns
prose when the caller expected bare YAML, or vice versa.

**6. Context boundary**

Does the prompt give the agent too much or too little context? Too much:
full pipeline state, multiple years, irrelevant background. Too little:
no file paths, no orientation on what the data represents.

The right amount: enough to orient, with pointers to explore further.

**7. Self-defeating instructions**

Does any instruction trigger the behavior it prevents? "Do not be verbose"
is verbose. "Avoid overthinking" invites overthinking. These should be cut
entirely — their absence is more effective than their presence.

</review-lens>

<output>

Present findings as:

1. **Summary verdict**: one sentence — is this prompt effective as-is, needs
   minor tuning, or needs significant rework?
2. **Issues found**: for each lens that surfaced problems, quote the specific
   passage and explain why it's an anti-pattern
3. **Proposed revision**: rewrite the prompt applying the fixes. Show the
   full revised prompt, not a diff — the user should be able to copy-paste
   the result directly.

After presenting, ask: "Should I write this revision to the file?" (if the
source was a file path).

</output>
