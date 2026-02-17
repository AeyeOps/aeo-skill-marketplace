# Dangerous AWS CLI Commands Reference

Commands that destroy data, incur costs, or affect production. Always confirm account and region before executing.

## Tier 1: Irreversible Data Loss

These commands **permanently delete data** with no recovery path:

| Command | Risk | Safer Alternative |
|---------|------|-------------------|
| `aws s3 rb s3://bucket --force` | Deletes bucket and ALL objects | List contents first: `aws s3 ls s3://bucket --recursive --summarize` |
| `aws s3 rm s3://bucket --recursive` | Deletes all objects in bucket | Use `--dryrun` first, then `--include`/`--exclude` filters |
| `aws ec2 terminate-instances` | Destroys instances permanently | Enable termination protection: `aws ec2 modify-instance-attribute --disable-api-termination` |
| `aws rds delete-db-instance --skip-final-snapshot` | Deletes DB with no backup | Always use `--final-db-snapshot-identifier` |
| `aws dynamodb delete-table` | Drops table and all items | Enable PITR first, export to S3 |
| `aws ecr batch-delete-image` | Removes container images | Use lifecycle policies for automated cleanup |
| `aws cloudformation delete-stack` | Destroys entire stack resources | Review with `--retain-resources` for stateful resources |
| `aws ecs deregister-task-definition` | Removes task definition | Deregistration is permanent; keep at least one revision |

## Tier 2: Service Disruption

These commands cause **immediate outages** or **access loss**:

| Command | Risk | Mitigation |
|---------|------|------------|
| `aws iam delete-role` | Breaks services using the role | Check `aws iam list-role-policies` and `list-attached-role-policies` first |
| `aws iam delete-user` | Revokes all access | Check `aws iam list-access-keys` and `list-mfa-devices` first |
| `aws ec2 revoke-security-group-ingress` | Blocks network access | Document current rules before modifying |
| `aws route53 change-resource-record-sets DELETE` | Removes DNS records | Export zone first: `aws route53 list-resource-record-sets` |
| `aws lambda delete-function` | Removes function and all versions | Check event source mappings and triggers first |
| `aws ecs update-service --desired-count 0` | Stops all tasks | Ensure you mean to scale down, not just redeploy |
| `aws elasticache delete-replication-group` | Destroys Redis cluster | Create final snapshot with `--final-snapshot-identifier` |
| `aws kms schedule-key-deletion` | Schedules encryption key destruction — data encrypted with it becomes unrecoverable | Set maximum waiting period (30 days); use `cancel-key-deletion` to reverse |
| `aws ec2 release-address` | Releases Elastic IP — may not get it back | Verify no running instances depend on it |

## Tier 3: Cost Explosion

These commands can **unexpectedly spike costs**:

| Command | Risk | Mitigation |
|---------|------|------------|
| `aws ec2 run-instances --count N` | Launches N instances (billing starts immediately) | Double-check instance type and count; use `--dry-run` |
| `aws s3 cp --recursive` (cross-region) | Data transfer charges | Check source and destination regions |
| `aws ec2 create-nat-gateway` | ~$32/month per gateway + data processing | Consider VPC endpoints for S3/DynamoDB |
| `aws rds create-db-instance` (multi-AZ) | 2x the cost of single-AZ | Verify `--multi-az` flag is intentional |
| `aws ec2 request-spot-instances` (on-demand fallback) | Spot interruption → on-demand pricing | Set `--spot-price` ceiling |

## Pre-Execution Safety Checklist

Before any destructive command:

```bash
# 1. Verify identity and account
aws sts get-caller-identity

# 2. Verify region
aws configure get region
# or check: echo $AWS_DEFAULT_REGION

# 3. Dry-run when supported
aws ec2 terminate-instances --instance-ids i-xxx --dry-run

# 4. For S3 operations, always dry-run first
aws s3 rm s3://bucket/prefix --recursive --dryrun

# 5. For CloudFormation, review change sets
aws cloudformation create-change-set --stack-name X --change-set-name review
aws cloudformation describe-change-set --change-set-name review --stack-name X
```

## Account-Level Guardrails

Recommend enabling these before using destructive commands:

```bash
# Enable S3 versioning on critical buckets
aws s3api put-bucket-versioning --bucket BUCKET --versioning-configuration Status=Enabled

# Enable RDS deletion protection
aws rds modify-db-instance --db-instance-identifier ID --deletion-protection

# Enable EC2 termination protection
aws ec2 modify-instance-attribute --instance-id ID --disable-api-termination

# Enable CloudTrail for audit trail
aws cloudtrail describe-trails
```
