---
name: aws-cli-operations
version: 1.0.0
description: >-
  This skill should be used when the user asks about "AWS CLI commands",
  "writing AWS CLI scripts", "querying AWS resources", "managing AWS
  credentials", "aws login", "aws configure sso", "assume role", "credential
  chain", or working with specific services via CLI (S3, EC2, IAM, Lambda,
  VPC, RDS, DynamoDB, CloudWatch, SSM). Also applies when the user needs help
  with "JMESPath query", "--query and --filters syntax", "CLI pagination",
  "aws cli waiter", "output formatting", "cross-account access",
  "safe destructive commands", "S3 sync dry run", "aws cli pager blocking
  script", or "migrating from AWS CLI v1 to v2".
---

# AWS CLI v2 Operations

Guidance for using the AWS Command Line Interface effectively and safely.

**Current version**: AWS CLI v2 is in the 2.33.x range. CLI v1 enters maintenance mode July 15, 2026 and reaches end of support July 15, 2027. All guidance here targets v2.

## Pre-Flight: Always Verify Context

Before executing ANY AWS CLI command, verify identity and region:

```bash
aws sts get-caller-identity
aws configure get region
```

**Never assume** which account or region is active. Environment variables, profile defaults, and SSO sessions can all silently change the target.

---

## Core Principles

1. **Verify before mutating** — Always `get-caller-identity` before write/delete operations
2. **Dry-run first** — Use `--dry-run` (EC2) or `--dryrun` (S3) before destructive actions
3. **Query server-side** — Use `--query` (JMESPath) and `--filters` to reduce response size
4. **Disable pager in scripts** — Set `AWS_PAGER=""` or `--no-cli-pager`; v2 enables pager by default which blocks scripts
5. **Script with `text` output** — Use `--output text` for pipeable, scriptable results
6. **Pin profiles explicitly** — Always pass `--profile` and `--region` in scripts; never rely on environment defaults
7. **Paginate consciously** — CLI v2 auto-paginates; use `--no-paginate` or `--max-items` when you need control
8. **Use `aws login` or SSO** — `aws login` (v2.32.0+) is the simplest browser-based auth; `aws configure sso` for org-managed Identity Center; IAM roles for machines; long-term keys as last resort

---

## Essential Command Patterns

### Resource Discovery

```bash
# List all EC2 instances with name, type, state as table
aws ec2 describe-instances \
  --query 'Reservations[].Instances[].{Name:Tags[?Key==`Name`].Value|[0],ID:InstanceId,Type:InstanceType,State:State.Name}' \
  --output table

# Find resources by tag across all services
aws resourcegroupstaggingapi get-resources \
  --tag-filters Key=Environment,Values=production

# List S3 buckets with creation dates
aws s3api list-buckets --query 'Buckets[].{Name:Name,Created:CreationDate}' --output table
```

### Safe Mutation Pattern

```bash
# Step 1: Verify identity
ACCOUNT=$(aws sts get-caller-identity --query Account --output text)
REGION=$(aws configure get region)
echo "Account: $ACCOUNT  Region: $REGION"

# Step 2: Dry-run the operation
aws ec2 run-instances --image-id ami-xxx --instance-type t3.micro \
  --region "$REGION" --dry-run

# Step 3: Execute with minimal scope
aws ec2 run-instances --image-id ami-xxx --instance-type t3.micro --count 1 \
  --region "$REGION" \
  --tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value=my-instance}]'
```

### Credential Management

```bash
aws login                              # browser-based (v2.32.0+, simplest)
aws login --remote                     # headless/SSH
aws configure sso                      # org-managed Identity Center
aws sso login --profile my-profile     # refresh SSO session
aws sts assume-role --role-arn ARN --role-session-name s --query Credentials  # cross-account
```

`aws login` auto-refreshes every 15 min (up to 12h), caches at `~/.aws/login/cache`. Requires `SignInLocalDevelopmentAccess` managed policy. Remove any `~/.aws/credentials` entries that might override login creds.

For full credential chain resolution, SSO session sharing, `[sso-session]` config, assumed-role export patterns, and credential gotchas, see [references/advanced-patterns.md#credential-chain-and-profiles](references/advanced-patterns.md#credential-chain-and-profiles).

### S3 Operations

```bash
aws s3 sync ./local s3://bucket/prefix --dryrun   # always dry-run first
aws s3 sync ./local s3://bucket/prefix --delete    # mirror mode
aws s3 cp large.zip s3://bucket/ --expected-size BYTES  # large file upload
aws s3 sync . s3://bucket --exclude "*.log" --exclude ".git/*"
```

For CRT transfer client (2-6x throughput), transfer acceleration, multipart tuning, `--no-overwrite` (v2.32.0+), and `--case-conflict` (v2.33+), see [references/advanced-patterns.md#s3-transfer-optimization](references/advanced-patterns.md#s3-transfer-optimization).

### Waiting for Resources

```bash
aws ec2 wait instance-running --instance-ids i-xxx
aws cloudformation wait stack-create-complete --stack-name my-stack
aws rds wait db-instance-available --db-instance-identifier mydb
```

Waiters timeout after ~10 min and return exit code 255. For advanced waiter patterns and chaining, see [references/advanced-patterns.md#waiter-patterns](references/advanced-patterns.md#waiter-patterns).

---

## Output and Filtering

### `--query` (JMESPath) vs `--filters`

| Feature | `--filters` | `--query` |
|---------|-------------|-----------|
| Where it runs | Server-side (API) | Client-side (CLI) |
| Reduces API data | Yes | No |
| Syntax | `Name=X,Values=Y` | JMESPath expressions |
| Combining | Use both together for best performance | Shapes output after filtering |

**Best practice**: Filter server-side with `--filters`, then shape output with `--query`:

```bash
aws ec2 describe-instances \
  --filters "Name=instance-state-name,Values=running" \
  --query 'Reservations[].Instances[].{ID:InstanceId,Type:InstanceType}'
```

For JMESPath gotchas, nested filtering, sort/limit, and pipe expressions, see [references/advanced-patterns.md#jmespath-queries](references/advanced-patterns.md#jmespath-queries).

### Output Format Selection

| Use Case | Format | Flag |
|----------|--------|------|
| Shell scripts | `text` | `--output text` |
| Debugging | `json` | `--output json` |
| Reports | `table` | `--output table` |
| Documentation | `yaml` | `--output yaml` |
| CI/CD | `json` + `--query` | Extract exact values |

---

## Script Safety Checklist

Verify before shipping:

- `set -euo pipefail` at script top
- `--tag-specifications` on every resource-creation call
- S3 versioning enabled on critical buckets before bulk operations
- Check `--help` for non-obvious required params on unfamiliar commands
- No `--no-verify-ssl` in production
- Sensitive output (keys, secrets) never piped to stdout unredacted
- No `--force` flags without understanding what they skip
- No `create-access-key` calls in automation scripts

---

## Common Gotchas

- **Pager blocks scripts**: v2 enables `less` by default. Fix: `export AWS_PAGER=""` or `--no-cli-pager`.
- **Pagination surprise**: v2 auto-paginates; a `describe-instances` with 10K instances returns ALL of them. Use `--max-items` to cap.
- **Text + query pagination trap**: `--output text` runs `--query` per page, not the full dataset. Use `json` or `yaml` when `--query` must operate on complete results.
- **Region mismatch**: Resources are region-scoped. Global services (IAM, Route53, CloudFront) use `us-east-1` implicitly.
- **S3 sync compares size + timestamp**, not content. Use `--exact-timestamps` for precision.
- **Filter vs query naming**: `--filters` uses API names (`instance-state-name`); `--query` uses response JSON names (`State.Name`).
- **Waiter timeouts**: ~10 min default, exit code 255 on timeout — crashes `set -e` scripts. Capture exit code explicitly.
- **SSO token expiry**: 1-8 hours typically. Run `aws sso login` to refresh. `aws login` auto-refreshes (15 min intervals, up to 12h).
- **CloudFormation drift**: `describe-stacks` shows template state, not actual. Use `detect-stack-drift` for truth.

For exit codes table, v1-to-v2 migration tool, and v2 behavioral changes, see [references/advanced-patterns.md#exit-codes-v2](references/advanced-patterns.md#exit-codes-v2).

---

## Dangerous Commands Reference

Before running any destructive AWS CLI command, consult the safety reference for tiered risk commands (irreversible data loss, service disruption, cost explosion), safer alternatives, and pre-execution checklists: [references/dangerous-commands.md](references/dangerous-commands.md).

---

## Advanced Patterns Reference

For JMESPath queries, pagination control, waiter patterns, output formats, credential chain and SSO session config, S3 transfer optimization, multi-account/cross-region loops, CLI aliases, and scripting templates: [references/advanced-patterns.md](references/advanced-patterns.md).

---

## Service Patterns Reference

For VPC provisioning, Lambda deployment, DynamoDB operations, RDS management, CloudWatch observability, SSM Parameter Store, and Security Groups: [references/service-patterns.md](references/service-patterns.md).
