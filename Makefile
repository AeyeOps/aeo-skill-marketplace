# Build chain for the aeo-skill-marketplace.
#
# This repo ships no compiled artifact; "build" means the tree is provably
# installable. Validation is therefore the fail-fast root of the chain: every
# other target lists `validate` first, so nothing downstream runs against a
# tree that Claude Code would load with silently-dropped metadata (the v0.5.0
# audit found 7 plugins shipping exactly that).
#
# Per-plugin targets (validate-aeo-claude, ...) fail the chain on the first
# broken plugin and parallelize under `make -j`.

SHELL := bash
PLUGINS := $(sort $(wildcard aeo-*))

.PHONY: all build validate gates $(addprefix validate-,$(PLUGINS))

all: build

build: validate gates
	@echo "build OK: $(words $(PLUGINS)) plugins validated, gates clean"

validate: $(addprefix validate-,$(PLUGINS))

# Static pattern rule, not an implicit `validate-%` one: make skips implicit
# rule search for .PHONY targets, which would leave these recipe-less and
# silently "succeed" without ever invoking the CLI.
$(addprefix validate-,$(PLUGINS)): validate-%:
	@claude plugin validate ./$*

# Regression gates for defect classes fixed in v0.5.0. Each grep must come up
# empty; a hit reintroduces a bug class that once shipped, so the gate fails.
gates:
	@fail=0; \
	if grep -rEln "^description: [^\"'|>].*: " aeo-*/agents/ 2>/dev/null; then \
		echo "GATE FAIL: unquoted agent description with inner colon (frontmatter silently dropped at runtime)"; fail=1; fi; \
	if grep -rln "@reference/" aeo-*/commands/ 2>/dev/null; then \
		echo "GATE FAIL: reference docs under commands/ register as spurious slash commands"; fail=1; fi; \
	if grep -rn "^import fcntl" aeo-*/hooks/ 2>/dev/null; then \
		echo "GATE FAIL: unguarded top-level fcntl import crashes hooks on Windows"; fail=1; fi; \
	if grep -rln "claude --agent" aeo-*/commands/ 2>/dev/null; then \
		echo "GATE FAIL: 'claude --agent' is not a real CLI invocation"; fail=1; fi; \
	if ls aeo-*/commands/*.md >/dev/null 2>&1 && \
		grep -Lr "^---" --include="*.md" aeo-*/commands/ 2>/dev/null | grep .; then \
		echo "GATE FAIL: command file missing frontmatter"; fail=1; fi; \
	exit $$fail
