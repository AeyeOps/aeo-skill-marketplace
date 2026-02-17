# aeo-infra

AWS infrastructure operations skills for Claude Code.

## Skills

### aws-cli-operations

AWS CLI v2 expert covering cloud operations, resource management, and automation scripting.

**Trigger phrases:** "aws cli", "run aws command", "aws s3", "aws ec2", "assume role", "cross-account", "JMESPath query", "aws credentials", "aws sso", "aws login", "describe instances", "aws waiter", "create vpc", "lambda deploy", "dynamodb query"

**What it covers:**
- Pre-flight safety checks (identity and region verification)
- Authentication hierarchy: `aws login` (v2.32.0+), SSO, IAM Roles Anywhere, instance roles
- JMESPath queries and server-side filtering
- Pagination, waiters, output formatting, and exit codes
- Credential chain, cross-account patterns, and credential export
- S3 transfer optimization (CRT client, `--no-overwrite`, `--case-conflict`)
- Service patterns: VPC, Lambda, DynamoDB, RDS, CloudWatch, SSM, Security Groups
- Dangerous command awareness and safe alternatives
- v1-to-v2 migration (`aws-cli-migrate` tool)
- Scripting best practices

## Installation

```bash
# From marketplace
/plugin install aeo-infra@aeo-skill-marketplace

# Direct
/plugin install /opt/aeo/aeo-skill-marketplace/aeo-infra
```
