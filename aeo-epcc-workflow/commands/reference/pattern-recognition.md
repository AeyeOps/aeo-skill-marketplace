# Pattern Recognition & Exploration Methodology

Systematic exploration methodology and pattern recognition for the EXPLORE phase.

## Exploration Methodology

### Phase 1: Project Context & Instructions

**ALWAYS START HERE:**

Check for CLAUDE.md files in this order:
1. Project root CLAUDE.md
2. .claude/CLAUDE.md
3. User global ~/.claude/CLAUDE.md

Document ALL instructions found - these are mandatory requirements for the project.

### Phase 2: Project Structure Discovery

Use multiple approaches to understand structure:
- Directory listings (ls, tree if available)
- File finding (find, Glob)
- Key file identification (entry points, configs)

Adapt if one approach fails - try another.

### Phase 3: Technology Stack Identification

Systematically check for different project types:
- Python: pyproject.toml, requirements.txt, setup.py, Pipfile, poetry.lock
- JavaScript/TypeScript: package.json, tsconfig.json, yarn.lock, pnpm-lock.yaml
- Other languages: Gemfile, pom.xml, build.gradle, Cargo.toml, go.mod, composer.json

Document frameworks, libraries, versions, and tools found.

### Phase 4: Pattern Recognition (Multi-Strategy Search)

**Use persistent, multi-attempt searching:**

Example: Finding authentication patterns
1. Direct file search: `find . -name "*auth*"`
2. Content search: `grep -r "authenticate|login|session"`
3. Class/function search: `grep -r "class.*Auth|def.*login"`
4. Import search: `grep -r "from.*auth import"`
5. Directory check: `ls src/auth/ app/auth/`

**Document what you tried and what worked:**
- Track successful search strategies
- Note what didn't work and why
- Record patterns found with file locations

### Phase 5: Architectural Pattern Discovery

Look for common patterns systematically:
- MVC/MVT Pattern
- Repository Pattern
- Service Layer Pattern
- Factory Pattern
- Middleware/Decorator Pattern
- Observer/Event Pattern

Document each pattern with:
- Where it's used (file paths)
- How many implementations
- Example usage
- When to use it

### Phase 6: Dependency Mapping

Trace both external and internal dependencies:
- **External**: From package manifests (package.json, requirements.txt, etc.)
- **Internal**: Module imports, component relationships, data flow

Create dependency graphs showing relationships.

### Phase 7: Constraint & Risk Identification

Actively search for constraints:
- Performance constraints (timeouts, rate limits, caching)
- Security constraints (CORS, CSRF, authentication, encryption)
- Version constraints (language versions, compatibility)
- Environment constraints (env vars, deployment requirements)

### Phase 8: Similar Implementation Search

If exploring a specific feature, find similar existing code:
- Search for related functionality
- Find integration examples
- Review existing third-party integrations
- Identify reusable components

## Parallel Exploration Subagents

For **very large codebases or complex exploration tasks**, deploy specialized exploration agents **in parallel to save time**.

**Launch simultaneously** (all in same response):

```
@code-archaeologist Analyze [system] architecture and data flow.

Target: [System] implementation across codebase
Focus areas:
- [Component 1] flow
- [Component 2] approach
- [Component 3] implementation

Trace: [User action] → [step 1] → [step 2] → [outcome]
Document: Component interactions, data flow, patterns, technical debt areas.

@system-designer Document [system] architecture and component design.

Target: [System] structure
Analyze:
- Component boundaries and responsibilities
- Service layer architecture
- Database schema
- API endpoint design

Generate: Architecture diagram, component relationships, data models, integration points.
```

**Available agents:**
@code-archaeologist @system-designer @business-analyst @test-generator @documentation-agent

**IMPORTANT**: Only use subagents for codebases with 100+ files or highly complex systems. For typical projects, handle exploration directly and autonomously.

## Thoroughness-Based Exploration Heuristics

### Completion Criteria (NOT File Count Targets)

**Stop exploring when objectives are met**, not when you hit arbitrary file counts.

### Quick Exploration (--quick)
**Stop when you understand:**
- Entry points and main flow
- 2-3 key patterns that dominate the codebase
- Basic tech stack and dependencies
- CLAUDE.md instructions (if present)

### Medium Exploration (default)
**Stop when you understand:**
- All major architectural patterns with examples
- Cross-module relationships and data flow
- Test patterns and coverage approach
- Configuration and deployment approach

### Deep Exploration (--deep/--thorough)
**Stop when you've exhaustively documented:**
- All patterns with multiple examples each
- Complete dependency tree (internal + external)
- Historical context and technical debt areas
- Edge cases and performance considerations
- Security patterns and compliance requirements

**Heuristic Rule**: If reading another file of the same type teaches you nothing new, you're done with that pattern.
