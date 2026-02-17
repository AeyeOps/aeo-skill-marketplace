# Advanced AWS CLI Patterns

## JMESPath Queries

Client-side output shaping that reduces what you see and avoids piping to `jq`:

```bash
# Get instance IDs in running state
aws ec2 describe-instances \
  --query 'Reservations[].Instances[?State.Name==`running`].InstanceId' \
  --output text

# Get Lambda function names and runtimes as table
aws lambda list-functions \
  --query 'Functions[].[FunctionName, Runtime, MemorySize]' \
  --output table

# Get S3 bucket names created after a date
aws s3api list-buckets \
  --query 'Buckets[?CreationDate>=`2025-01-01`].Name'

# Nested filtering: security groups with open SSH
aws ec2 describe-security-groups \
  --query 'SecurityGroups[?IpPermissions[?FromPort==`22` && IpRanges[?CidrIp==`0.0.0.0/0`]]].GroupId'

# Sort and limit: top 5 largest EBS volumes
aws ec2 describe-volumes \
  --query 'sort_by(Volumes, &Size)[-5:].{ID:VolumeId, Size:Size, State:State}'
```

### JMESPath Gotchas

- **Backticks for literals**: Inside `--query`, JMESPath string literals use backticks (`` `running` ``), not single or double quotes
- **Flattening**: `[]` flattens nested arrays; `[*]` preserves structure
- **Pipe expressions**: `| [0]` takes first result after filtering
- **Multi-select hash**: `{Name:Tags[?Key=='Name'].Value | [0]}` extracts tag values
- **Type mismatch**: Comparing string to number silently returns empty — cast with `to_number()`

## Pagination

AWS CLI v2 auto-paginates by default. Control it explicitly when needed:

```bash
# Disable auto-pagination (get raw API response with NextToken)
aws s3api list-objects-v2 --bucket my-bucket --no-paginate --max-items 100

# Manual pagination with starting token
aws s3api list-objects-v2 --bucket my-bucket \
  --max-items 100 --starting-token TOKEN_FROM_PREVIOUS

# Page size (controls API calls, not total results)
aws dynamodb scan --table-name my-table --page-size 25

# Combine with query for efficient large-result processing
aws ec2 describe-instances \
  --query 'Reservations[].Instances[].InstanceId' \
  --max-items 50
```

### Pagination Gotchas

- `--max-items` limits total returned results (client-side)
- `--page-size` controls per-API-call batch size (server-side)
- `--no-paginate` returns only first page — use when you explicitly want one page
- Some commands don't support pagination: check `aws <service> <command> help`

## Waiter Patterns

Wait for resources to reach a desired state before proceeding:

```bash
# Wait for instance to be running, then get its public IP
aws ec2 run-instances --image-id ami-xxx --instance-type t3.micro \
  --query 'Instances[0].InstanceId' --output text | xargs -I {} sh -c '
  aws ec2 wait instance-running --instance-ids {} && \
  aws ec2 describe-instances --instance-ids {} \
    --query "Reservations[0].Instances[0].PublicIpAddress" --output text'

# Wait for RDS to be available
aws rds wait db-instance-available --db-instance-identifier mydb

# Wait for CloudFormation stack to complete
aws cloudformation wait stack-create-complete --stack-name my-stack

# Wait for ECS service to stabilize
aws ecs wait services-stable --cluster my-cluster --services my-service
```

### Waiter Gotchas

- Default timeout is ~10 minutes (40 attempts, 15s interval)
- No built-in custom timeout — wrap with `timeout` command for safety
- Not all resources have waiters — fall back to polling with `watch`
- Waiter failure exits non-zero — chain with `&&` for safe scripts

## Output Formats

```bash
# JSON (default) — best for piping to jq
aws ec2 describe-instances --output json

# Table — best for human reading
aws ec2 describe-instances --output table

# Text — best for scripting (tab-separated, one value per line)
aws ec2 describe-instances --query 'Reservations[].Instances[].InstanceId' --output text

# YAML — best for readability of complex nested structures
aws ec2 describe-instances --output yaml
```

### Format Selection Rules

| Use Case | Format | Why |
|----------|--------|-----|
| Script input | `text` | Easy to `xargs`, `awk`, `cut` |
| Debugging | `json` + `jq` | Full structure visible |
| Reports/dashboards | `table` | Human-readable |
| Config/documentation | `yaml` | Clean nested display |
| CI/CD pipelines | `json` + `--query` | Precise extraction, no external deps |

## Credential Chain and Profiles

### Authentication Hierarchy (Recommended Order)

1. **`aws login`** (v2.32.0+) — browser-based, no stored keys, auto-refresh every 15 min
2. **IAM Identity Center SSO** (`aws configure sso`) — PKCE-based (default since v2.22.0), org-managed
3. **IAM Roles Anywhere** — certificate-based, no access keys
4. **EC2 Instance Metadata / ECS Task Role** — automatic, no config needed
5. **Environment variables** (`AWS_ACCESS_KEY_ID` + `AWS_SECRET_ACCESS_KEY`) — CI/CD, containers
6. **Long-term access keys** (`~/.aws/credentials`) — **last resort**, rotate frequently

### Credential Resolution Chain

AWS CLI resolves credentials in this order (simplified; see [AWS docs](https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-authentication.html) for full chain):
1. Command line `--profile` flag
2. `AWS_PROFILE` environment variable
3. `AWS_ACCESS_KEY_ID` / `AWS_SECRET_ACCESS_KEY` / `AWS_SESSION_TOKEN` env vars
4. `~/.aws/login/cache` (from `aws login`)
5. `~/.aws/credentials` default profile
6. AWS SSO / Identity Center cached tokens
7. EC2 instance metadata / ECS task role / Lambda execution role
8. `~/.aws/config` credential_process

```bash
# Browser-based login (simplest — v2.32.0+)
aws login                              # opens browser
aws login --profile my-dev-profile     # named profile
aws login --remote                     # headless/SSH
aws logout                             # end session

# Configure SSO (Identity Center) — preferred for org-managed access
aws configure sso
# Follow prompts: SSO start URL, region, account, role

# Login to SSO session
aws sso login --profile my-sso-profile

# Use named profile
aws s3 ls --profile production

# Assume role for cross-account access
aws sts assume-role \
  --role-arn arn:aws:iam::123456789012:role/CrossAccountRole \
  --role-session-name my-session \
  --query 'Credentials' --output json

# Export assumed-role credentials
eval $(aws sts assume-role \
  --role-arn arn:aws:iam::123456789012:role/Role \
  --role-session-name s \
  --query 'Credentials.[AccessKeyId,SecretAccessKey,SessionToken]' \
  --output text | awk '{print "export AWS_ACCESS_KEY_ID="$1" AWS_SECRET_ACCESS_KEY="$2" AWS_SESSION_TOKEN="$3}')
```

### `aws login` Profile Config (`~/.aws/config`)

After running `aws login`, the CLI writes a `login_session` key (an IAM ARN) into the profile:

```ini
[default]
login_session = arn:aws:iam::123456789012:user/myuser
region = us-east-1

# Share login creds with other tools via credential_process
[profile shared]
credential_process = aws configure export-credentials --profile default --format process
region = us-east-1
```

### SSO Session Sharing (`[sso-session]`)

For IAM Identity Center, define a shared `[sso-session]` section so multiple profiles reuse one SSO start URL:

```ini
# Define the SSO session once
[sso-session my-org]
sso_start_url = https://my-org.awsapps.com/start
sso_region = us-east-1
sso_registration_scopes = sso:account:access

# Profiles reference the session by name
[profile dev]
sso_session = my-org
sso_account_id = 111111111111
sso_role_name = DeveloperAccess
region = us-east-1

[profile staging]
sso_session = my-org
sso_account_id = 222222222222
sso_role_name = DeveloperAccess
region = us-west-2
```

```bash
# Login once, both profiles authenticate via the shared SSO session
aws sso login --profile dev
aws s3 ls --profile staging   # no second login needed
```

### Credential Gotchas

- `aws login` sessions auto-refresh every 15 min, valid up to 12h. `~/.aws/credentials` entries override login creds — remove old access keys.
- SSO tokens expire (typically 1-8 hours) — re-run `aws sso login`
- `AWS_PROFILE` overrides `--profile` in some contexts — be explicit
- Environment variables take precedence over config file profiles
- Never commit `~/.aws/credentials` or long-lived access keys to git
- Use `credential_process` for custom credential providers (vault, 1password, etc.)

## Auto-Prompt

Interactive command completion built into CLI v2:

```bash
# Enable permanently (prompts on every command)
aws configure set cli_auto_prompt on

# Partial mode (prompts only for incomplete commands)
aws configure set cli_auto_prompt on-partial

# One-time usage
aws ec2 describe-instances --cli-auto-prompt

# Disable for a single command (in scripts)
aws s3 ls --no-cli-auto-prompt
```

## Skeleton Generation and Input Files

```bash
# Generate input skeleton for complex commands
aws ec2 run-instances --generate-cli-skeleton > input.json
# Edit input.json, then:
aws ec2 run-instances --cli-input-json file://input.json

# Export credentials for external tools
eval "$(aws configure export-credentials --profile myprofile --format env)"
# Also supports: env-no-export, powershell, windows-cmd, process

# Fish shell (v2.33.7+)
aws configure export-credentials --format fish | source

# Process format (for credential_process in config, or legacy SDK support with aws login)
aws configure export-credentials --profile signin --format process
```

## S3 Transfer Optimization

```bash
# Parallel uploads with multipart (automatic for files >8MB)
aws s3 cp large-file.zip s3://bucket/ --expected-size 1073741824

# Sync with delete (mirror local to S3)
aws s3 sync ./local/ s3://bucket/prefix/ --delete --dryrun

# Transfer acceleration (must be enabled on bucket)
aws s3api put-bucket-accelerate-configuration \
  --bucket my-bucket --accelerate-configuration Status=Enabled
aws s3 cp file.zip s3://my-bucket/ --endpoint-url https://s3-accelerate.amazonaws.com

# CRT transfer client (best performance for large transfers)
aws configure set default.s3.preferred_transfer_client crt
aws configure set default.s3.target_bandwidth 10Gb/s

# Configure multipart thresholds
aws configure set default.s3.multipart_threshold 64MB
aws configure set default.s3.multipart_chunksize 16MB
aws configure set default.s3.max_concurrent_requests 20

# Skip existing files (v2.32.0+)
aws s3 cp local-dir/ s3://bucket/prefix/ --recursive --no-overwrite
aws s3 sync local-dir/ s3://bucket/prefix/ --no-overwrite

# Handle case-insensitive filesystem conflicts on download (v2.33+)
aws s3 sync s3://bucket/prefix/ local-dir/ --case-conflict rename

# Exclude patterns during sync
aws s3 sync . s3://bucket --exclude "*.log" --exclude ".git/*" --include "*.py"
```

### CRT Client Notes
- **2-6x throughput improvement** for large file transfers
- Automatically tunes parallelization based on CPU, memory, and network
- Auto-enabled on p4d, p5, and trn1 instance types
- Does NOT support S3-to-S3 copies or region redirects
- Ignores `max_concurrent_requests`/`max_queue_size`/`multipart_threshold` settings (auto-tuned)
- Requires `awscrt` Python package (bundled in standard CLI install)

## Multi-Account and Cross-Region

```bash
# Loop across regions
for region in $(aws ec2 describe-regions --query 'Regions[].RegionName' --output text); do
  echo "=== $region ==="
  aws ec2 describe-instances --region "$region" \
    --query 'Reservations[].Instances[].{ID:InstanceId,Type:InstanceType}' --output table
done

# Cross-account with profile switching
for profile in dev staging production; do
  echo "=== $profile ==="
  aws sts get-caller-identity --profile "$profile"
  aws ec2 describe-instances --profile "$profile" --query 'Reservations[].Instances[].InstanceId'
done

# Resource tagging for multi-account governance
aws resourcegroupstaggingapi get-resources \
  --tag-filters Key=Environment,Values=production \
  --query 'ResourceTagMappingList[].ResourceARN'
```

## CLI Shortcuts and Aliases

Configure in `~/.aws/cli/alias`:

```ini
[toplevel]
whoami = sts get-caller-identity
running = ec2 describe-instances --query 'Reservations[].Instances[?State.Name==`running`].[InstanceId,InstanceType,Tags[?Key==`Name`].Value|[0]]' --output table
myip = ec2 describe-instances --filters Name=tag:Owner,Values=$USER --query 'Reservations[].Instances[].PublicIpAddress' --output text
sg-open = ec2 describe-security-groups --query 'SecurityGroups[?IpPermissions[?IpRanges[?CidrIp==`0.0.0.0/0`]]].{ID:GroupId,Name:GroupName}' --output table
# Linux (GNU coreutils):
costs = ce get-cost-and-usage --time-period Start=$(date -d '30 days ago' +%Y-%m-%d),End=$(date +%Y-%m-%d) --granularity MONTHLY --metrics BlendedCost --query 'ResultsByTime[].Total.BlendedCost'
# macOS (BSD date): replace $(date -d '30 days ago' ...) with $(date -v-30d +%Y-%m-%d)
```

## Scripting Best Practices

```bash
#!/usr/bin/env bash
set -euo pipefail
export AWS_PAGER=""

# Always verify identity first
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
echo "Operating on account: $ACCOUNT_ID"

# Use --output text for scripting
INSTANCE_IDS=$(aws ec2 describe-instances \
  --filters "Name=tag:Environment,Values=staging" \
  --query 'Reservations[].Instances[].InstanceId' \
  --output text)

# Check for empty results
if [[ -z "$INSTANCE_IDS" ]]; then
  echo "No instances found" >&2
  exit 1
fi

# Process results safely (handles spaces in values)
# Note: $INSTANCE_IDS is intentionally unquoted — AWS CLI expects space-separated IDs
# For large result sets (100+), batch with xargs to avoid ARG_MAX limits
while IFS=$'\t' read -r id type state; do
  echo "Instance: $id ($type) - $state"
done < <(aws ec2 describe-instances \
  --instance-ids $INSTANCE_IDS \
  --query 'Reservations[].Instances[].[InstanceId,InstanceType,State.Name]' \
  --output text)
```

## Exit Codes (v2)

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | General error |
| 2 | Usage/parameter error |
| 130 | SIGINT (Ctrl+C) |
| 252 | Command syntax error |
| 253 | Configuration error |
| 254 | Service-side error |
| 255 | General CLI error |

Scripts using `set -e` should handle these explicitly. Waiters return 255 on timeout.

## v1-to-v2 Migration

Use the `aws-cli-migrate` static linter to detect breaking changes in bash scripts:
```bash
pip install aws-cli-migrate
migrate-aws-cli --script deploy.sh              # detect only
migrate-aws-cli --script deploy.sh --fix         # auto-fix
migrate-aws-cli --script deploy.sh --interactive  # review each fix
```
CLI v1 enters maintenance mode July 15, 2026 and end of support July 15, 2027.

### v2 Behavioral Changes from v1
- **Timestamps**: v2 returns ALL timestamps in ISO 8601 (v1 varied by service). Use `cli_timestamp_format = wire` for raw API format.
- **Binary values**: v2 defaults to base64 encoding for all binary input/output.
- **S3 copies**: `s3 cp`/`s3 sync` now copy tags and metadata by default (increases API calls). Control with `--copy-props`.
- **ECR login**: `aws ecr get-login` is removed in v2. Use `aws ecr get-login-password | docker login --username AWS --password-stdin <url>`.
- **Empty CloudFormation changesets**: v2 returns exit code 0 (v1 returned error). Use `--fail-on-empty-changeset`.
- **S3 us-east-1 endpoint**: v2 uses `s3.us-east-1.amazonaws.com` (regional) instead of `s3.amazonaws.com` (global). Set region to `aws-global` to force global endpoint.
- **STS endpoints**: v2 uses regional endpoints by default (`sts.{region}.amazonaws.com`).
