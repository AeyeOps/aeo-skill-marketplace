---
name: aeo-repo-sanitize
version: 0.4.3
description: Scan repo for security risks, PII, secrets, local environment leaks, and supply chain issues before public push
argument-hint: "[--auto-approve]"
allowed-tools: Read, Edit, Write, Glob, Grep, Bash, Agent
---

# Repository Security & Privacy Scan

**Flags** (detected from `$ARGUMENTS`):
- **--auto-approve**: After presenting the report, apply the recommended option's remediations without prompting.
- **--include-untracked**: Also scan untracked files (`git ls-files --others --exclude-standard`). Use before `git add -A` to catch issues in new files before they enter the index.

## Step 1: Determine Scan Scope

Identify what to scan:

```
Repo root: current working directory
Remote: git remote -v (check if public/private)
```

Collect the file inventory. Exclude `.git/`, `.venv/`, `node_modules/`, `__pycache__/`, and binary files.

```
Tracked files:    git ls-files
Staged new files: git diff --cached --name-only --diff-filter=A
Untracked files:  git ls-files --others --exclude-standard   (only if --include-untracked)
```

Default scope is tracked + staged only — untracked files are not pushed and scanning them without intent wastes focus. Pass `--include-untracked` when you intend to run `git add -A` and want to catch issues in new files before they enter the index.

## Step 2: Deep Scan

Use Explore agents (subagent_type=Explore) to parallelize the scan. Launch up to 4 agents covering different categories simultaneously.

**Scaling heuristic**: For repos under ~1000 tracked files, agents read every file. For larger repos, grep-first triage — pattern match to find candidates, then read flagged files for context.

### Category 1: Secrets & Credentials
Scan for:
- API keys, tokens, passwords — note whether each is EXAMPLE (placeholder like `your-key-here`) or potentially REAL
- AWS access keys (`AKIA...`), GCP service account JSON, Azure connection strings
- Private keys (RSA/EC/ED25519 headers, `.pem` content)
- OAuth client secrets, JWT signing keys, database connection strings with embedded credentials
- `.env` files or env-like key=value pairs with real-looking values
- Hardcoded bearer tokens, session cookies, webhook URLs with embedded secrets

### Category 2: PII & Local Environment
Scan for:
- **Absolute paths** — classify as EXAMPLE (generic placeholder like `/home/user/`) or REAL (specific developer path like `/home/jdoe/`). Read surrounding context to decide.
- **Machine-specific references**: hostnames, internal DNS, private-range IPs
- **Real personal info**: names tied to accounts, real email addresses (not @example.com), phone numbers
- **Internal URLs**: intranet, VPN endpoints, private service/repo URLs
- **Session artifacts**: embedded log output, stack traces with local paths, IDE configs with machine paths
- **Git author leaks**: `.mailmap` or commit templates exposing emails the author didn't intend to publish (e.g., corporate email on a personal project). The repo owner's own email in their own commits is intentional git configuration, not a leak.
- **Personal account details**: billing/subscription references in changelogs

### Category 3: Supply Chain & Operational Risk
Scan for:
- **Pinning gaps**: dependencies without version pins or with overly broad ranges
- **Lockfile presence**: verify lockfiles exist where dependency files exist
- **Build script risks**: `curl | bash`, downloads from arbitrary URLs, elevated privileges
- **Untrusted code execution**: scripts that download and execute code from arbitrary URLs, or install packages from non-standard indexes without verification
- **Sensitive tracked files**: `.env`, `credentials.json`, `*.key`, `*.pem`, `id_rsa`
- **Docker risks**: running as root, hardcoded registry credentials, `--privileged`
- **CI/CD leaks**: workflow files that echo secrets, use insecure action versions
- **Gitignore gaps**: check whether `.env`, `*.key`, `*.pem`, `credentials*`, `secrets*` are covered — missing patterns become findings in the main table
- **Large tracked files**: anything over 10MB

### Category 4: Documentation & Skill Content
Apply specifically to `.md`, `.txt`, and other prose/documentation files. These files often embed real environment context that slips past code-focused scans.

Scan for:
- **Real absolute paths in prose** — paths containing specific usernames or machine names (e.g., `/home/jdoe/`, `/Users/jdoe/`, `/opt/company-internal/`) embedded in skill reference tables, code blocks, or setup guides. Distinguish from generic tutorial paths like `/home/user/` (LOW) or repo-relative paths like `./scripts/` (not a finding).
- **Machine-specific hostnames and internal FQDNs** — references to internal hostnames, `.local` domains, VPN hostnames, or intranet FQDNs in skill examples or config snippets.
- **Private-range IPs beyond documented device defaults** — private IPs (10.x, 172.16–31.x, 192.168.x) that are environment-specific rather than device-default values documented by the product (e.g., `192.168.8.1` as a router's factory default is LOW; `192.168.1.50` as a specific machine's address is MEDIUM).
- **Non-public URLs in content** — URLs pointing to intranet, VPN portals, private registries, internal CI/CD, or staging environments embedded in documentation or skill reference tables.
- **Environment-specific config values in reference tables** — Quick Reference tables or config examples that contain real server addresses, account IDs, tenant IDs, or subscription identifiers rather than placeholders.
- **Real usernames in path examples or SSH commands** — `ssh user@...` or `cp /home/realname/...` where `realname` matches a real person rather than a generic placeholder.
- **Hardware fingerprinting** — specific chip model names (e.g., M5 Max, M4 Pro), exact RAM amounts (e.g., "128 GB machine", "137 GB"), GPU identifiers (e.g., `applegpu_g17s`), or storage capacities used as prose context that together identify the developer's specific rig. Generic tier descriptions ("high-RAM Mac", "Apple Silicon") are fine; specific model+capacity combinations are not.
- **Internal service and agent names** — references to internal tools, agents, services, or systems by their internal names (e.g., "hermes-agent", "internal-proxy") embedded in documentation or comments that ship publicly. Replace with generic descriptions of the role the service performs.
- **Changelog or commit message oversharing** — change descriptions that reference internal ticket systems, internal team names, private repo URLs, internal tooling names, or specific hardware configurations not visible to the public.

Calibration for Category 4:
- Router/device factory-default IPs documented in official product specs → LOW (public product information)
- `192.168.8.1` as GL-iNet's documented default admin IP → LOW
- Generic tutorial usernames (user, username, yourname, admin) → not a finding
- Public third-party service URLs (GitHub, NordVPN, Tailscale dashboard) → not a finding
- Repo-relative paths (`./skills/`, `aeo-claude/`) → not a finding
- "Apple Silicon Mac" or "high-RAM machine" → not a finding (generic tier, not fingerprinting)
- "M5 Max", "128 GB machine", `applegpu_g17s` in prose → MEDIUM (identifies specific rig)
- "deploy-agent", "internal-proxy", internal service names in shipped docs → MEDIUM
- "AeyeOps internal tool" or org-internal references in documentation that ships publicly → MEDIUM

<viability-gate>
Before passing a finding to Step 3, verify that the stated risk is actually realizable in the execution context where the flagged code runs. A risk whose premise cannot manifest is not a valid finding — drop it entirely.

For each candidate finding, ask:
- Is this risk unique to the flagged pattern, or would it apply equally to any standard alternative? If the standard alternative carries the same risk, the pattern isn't the problem.
- Is the flagged behavior appropriate for its execution context, or genuinely anomalous? Understand how the code is actually invoked before judging whether its behavior is surprising.
- Would the proposed remediation improve the actual security posture, or just move the same risk to a different form?
</viability-gate>

## Step 3: Compile and Deduplicate Findings

Agents will produce overlaps. Merge into single entries — keep the most detailed description and the highest severity.

Drop clean confirmations ("no large files found", "no CI workflows exist"). Only report what needs attention or awareness because the user reads a diff, not a compliance checklist.

Gitignore coverage gaps are findings in the main table, not a separate section.

Assign each deduplicated finding a severity:

- **CRITICAL** — Active secret exposure, private key in repo, real credentials that grant access
- **HIGH** — Real PII exposure, execution of code from untrusted sources (`curl|sh` from unknown URLs, installs from non-standard package indexes)
- **MEDIUM** — Scanner false-positive magnets, open-ended dependency pins, missing `.gitignore` patterns, documentation normalizing insecure patterns
- **LOW** — Clearly-fake example credentials, generic placeholder paths, intentional public contact info

<reference>
Calibration — these prevent common misclassifications:
- `support@company.com` in project metadata → LOW (intentional), not HIGH
- `sk_live_abc123` in a "BAD example" code block → MEDIUM (scanner noise), not CRITICAL
- `/home/user/.config/app` in a tutorial → LOW (generic example), not HIGH
- `pip install popular-package` in a hook's `except ImportError` → LOW (standard dependency management, equivalent to requirements.txt)
- `pip install` from a custom `--index-url` or installing an obscure package → HIGH (untrusted source)
- Repo owner's personal email in their own git commits → not a finding (intentional git configuration)
</reference>

## Step 4: Final Verification

Re-read each deduplicated finding in its full file context. Drop any finding where:
- The risk was already mitigated by another mechanism visible in the codebase
- The finding depends on an assumption that other findings disproved
- The remediation would not improve the actual security posture

This catches findings that passed the viability gate individually but are invalidated by the broader picture.

## Step 5: Present Report

Structure the output exactly as shown below. The report ends with selectable next-step options — this is the primary decision point for the user.

```
## Scan Summary

- Repo: <name> (<public/private>)
- Files scanned: <count>
- Findings: <count> (CRITICAL: N, HIGH: N, MEDIUM: N, LOW: N)

## Findings

| # | Sev | Title | File:Line | Action |
|---|-----|-------|-----------|--------|
| 1 | HIGH | <title> | `<file>:<line>` | <short remediation> |
| 2 | MEDIUM | <title> | `<file>:<line>` | <short remediation> |
| ... | ... | ... | ... | ... |

## Details

Only include a details section for findings that need more context than fits
in a table row (multi-file findings, nuanced risks, content quotes).
Reference by finding number.

**#1 — <title>**
Content: `<the problematic content>`
Risk: <why this matters>

## Recommended Next Steps

Group actionable findings (MEDIUM and above) into up to 3 themed options
based on remediation affinity — findings that can be fixed in one pass
belong together. LOW findings need no option; they are in the table for
awareness only.

Mark one option as recommended — pick the option with the highest-severity
findings or the best effort-to-impact ratio.

**Option A: <theme>** ⭐ Recommended
Addresses: #1, #4, #5
<One sentence: what this fixes and why it's the priority.>

**Option B: <theme>**
Addresses: #2, #6
<One sentence: what this fixes.>

**Option C: <theme>** (only if warranted)
Addresses: #7
<One sentence.>

Select an option to proceed, or address findings individually.
```

**If `--auto-approve`**: After presenting the report, apply the recommended option's remediations immediately, then present the remaining options for selection.

**Otherwise**: Present the report and wait for the user to select an option.

## Constraints

- Report everything found — let the user decide what matters
- If a secret appears in git history (not just the working tree), warn that removing it from the current tree is insufficient because the secret remains in the reflog and should be rotated
- Warn about force-push consequences before suggesting `git filter-branch` or `BFG`
- Test fixture data with clearly fake values (Alice/Bob, @example.com, 555-0100) is LOW
- Flag tracked files over 10MB because large binaries in git are an operational risk
