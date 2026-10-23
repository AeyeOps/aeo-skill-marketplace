# UX3 Product Design Harness

Review product decisions through User, Evidence and Business Flows, then validate review-to-execution handoffs against the approved scope. Outputs are structured review and context-pack JSON; the skill does not grant permission to execute a decision.

## Known source limitations

This is a review-only candidate, not Candidate Complete or a recommendation to adopt the current defective baseline. The source is pinned to [48965c6b501f61ebbb8130c9c2e4f9af08922b9f](https://github.com/cis2042/ux3-product-design-harness/tree/48965c6b501f61ebbb8130c9c2e4f9af08922b9f/skills/product-design-harness), preserving all 91 tracked skill files and the original MIT license unchanged.

- The override validator can accept a prohibited scope entry when surrounded by whitespace. [Upstream PR23](https://github.com/cis2042/ux3-product-design-harness/pull/23) addresses that defect but is not merged into this source.
- Three referenced images are absent: `ux3-model.svg`, `intersections.svg`, and `product-vs-coding-harness.svg`. [Upstream PR24](https://github.com/cis2042/ux3-product-design-harness/pull/24) adds them but is not merged into this source.

The file count proves preservation of that version, not correct behavior for all inputs or complete referenced images. Final source acceptance must wait for the upstream fixes and a separately verified version. This wrapper does not include either unmerged patch.

## Installation after maintainer acceptance

Only after the maintainer merges this plugin and it is available in the marketplace:

```text
/plugin install aeo-ux3-product-design-harness --marketplace AeyeOps/aeo-skill-marketplace
```

This candidate is not published. The command is not claimed to work before acceptance, and final source acceptance still requires the upstream fixes described above.

## Requirements and scope

The validators require Python and `jsonschema` in an existing environment. Optional external evidence needs host and user authorization; model or provider usage can incur costs. No credentials or provider access are included. The agent's existing tool permissions remain decisive.

This plugin contains only the existing skill folder. It adds no agents, commands, hooks, MCP servers, tools, automatic execution or permissions. Do not treat a product verdict as authorization to exceed the approved boundary.

The source skill is under `skills/product-design-harness/`. Read its `SKILL.md` and bundled documents for use and validation. Installing the folder does not prove Claude Code execution, security certification or successful product outcomes. No model execution or human review is claimed.

## License and contact

The original MIT text and copyright notice are preserved in the plugin root and skill folder. Report skill issues at the [upstream repository](https://github.com/cis2042/ux3-product-design-harness/issues). This wrapper is prepared with Codex assistance.
