---
description: Create well-crafted prompts for Claude agentic execution — fights the tendency to over-prescribe inputs and procedural steps
argument-hint: "[description of what the prompt should do]"
disable-model-invocation: true
---

# Create Claude Prompt

<purpose>
You are creating a prompt that will be consumed by Claude in an agentic context.
Your natural tendency is to over-specify — treating prompts like procedural code
with prescribed inputs, enumerated steps, and constrained paths. This command
exists to counteract that instinct.
</purpose>

<prep>
Before writing anything:

- Use the claude-code-guide to learn current best practices for optimal
  prompting.
- Invoke the `opus-prompting@aeo-claude` skill for behavioral properties
  and pattern transformations. These are your content guardrails.
</prep>

<principles>

A good agentic prompt provides intent, context, output contract, and freedom.
A bad one provides embedded content, procedural steps, exhaustive enums, and
aggressive directives.

**Trust over control.** State the goal. Give starting file paths. Let the agent
explore. Do not enumerate investigation steps.

**Files over content.** If the agent has filesystem access, point to files.
The agent reads what it needs and skips what it doesn't. Embedding file content
wastes tokens and removes the agent's ability to selectively read.

**Natural language over directives.** "Investigate why X differs from Y" —
not "You MUST analyze the delta between X and Y by first reading A, then
comparing field B..."

**Bounded context via XML tags.** Use semantic tags (`<gap>`, `<context>`,
`<files>`) to structure inputs. The agent parses these naturally and they
separate mutable data from immutable instructions.

**Output contract as the only hard constraint.** The response schema is where
precision matters. Define it exactly. Everything else is guidance, not rules.

</principles>

<process>

## Step 1: Derive Context

Start from `$ARGUMENTS` and the current conversation context. Extract
everything you can about:

- What the prompt should accomplish
- Delivery format (file template, slash command, console, embedded string)
- Token replacement needs
- Output format and strictness
- Who or what consumes the output

Derive what you can confidently infer. For anything you cannot determine
with high confidence from the available context, use AskUserQuestion. Do
not guess or fabricate details — low-confidence gaps become questions, not
assumptions.

## Step 2: Validate Delivery Format

If not already clear, ask:

> How will this prompt be used?
> - **A) File template** — `.prompt.md` loaded by Python with `{TOKEN}` replacement
> - **B) Slash command** — reusable `/command` for Claude Code
> - **C) Direct console** — pasted into a session or piped via `claude -p`
> - **D) Embedded string** — hardcoded in Python/script source

If **B**: ask whether user-scoped or project-scoped, then invoke the
`slash-command-creator@aeo-claude` skill and hand off.

## Step 3: Validate Token Replacement

For formats A and D, confirm the dynamic values that will be injected at
runtime. For each token: name, data source, and an example value. Convention:
`{SINGLE_BRACE}` for `.prompt.md` files.

If tokens were described in `$ARGUMENTS` or conversation context, confirm
your understanding with the user. If any are ambiguous or missing, ask.
Tokens are the interface contract between calling code and prompt — they
deserve the same care as function signatures.

## Step 4: Validate Output Contract

Confirm:

- **Format**: YAML, JSON, plain text, markdown, or unconstrained?
- **Schema**: what fields, types, and enums?
- **Strictness**: should the agent respond with ONLY the structured block
  (for machine parsing), or is surrounding prose acceptable?

The strictness question matters when the calling code parses stdout
programmatically — if it will `yaml.safe_load(stdout)`, the prompt needs to
request bare structured output with no surrounding text. If a human reads
the output, prose is fine.

If the user says "just figure it out" — design the output schema yourself
based on the intent, present it for approval, then proceed.

## Step 5: Write the Prompt

Apply the principles above. Structure the prompt using XML tags to separate:
- Fixed instructions (the task description)
- Variable context (tokens, file paths)
- Output contract (the response schema)

Keep the prompt short. If you find yourself writing more than 30 lines of
instruction, you are probably over-specifying.

## Step 6: Self-Review

Before presenting, check against these failure modes:

<self-review>
- **Over-specified inputs?** Embedding file contents that could be paths?
  Listing every field when the agent could read the file?
- **Procedural steps?** More than 3 sequential imperatives ("first... then...
  next...") means you're writing a procedure, not a prompt. Cut it.
- **Exhaustive enums?** Would removing the list of possible causes/categories
  make the agent perform worse? If not, remove it.
- **Aggressive language?** Search for MUST, NEVER, CRITICAL, IMPORTANT,
  ALWAYS. Transform per opus-prompting rules.
- **Self-defeating constraints?** Does any instruction trigger the behavior
  it prevents?
- **Output ambiguity?** If the caller expects machine-parseable output, does
  the prompt make that unambiguous? Would the agent know whether to return
  bare YAML or wrap it in prose?
</self-review>

## Step 7: Present and Iterate

Show the prompt to the user. For file templates, recommend a file location.

Ask: "Does this capture the intent? Anything to adjust?"

Iterate until approved, then write the file.

</process>
