# aeo-infra

Infrastructure operations skills for Claude Code — AWS CLI v2 and Azure CLI.

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

### az-cli-operations

Azure CLI expert covering cloud operations, resource management, and automation scripting.

**Trigger phrases:** "az cli", "azure cli", "az login", "az account", "service principal", "managed identity", "az vm", "az storage", "az aks", "az keyvault", "az webapp", "az rest", "az graph query", "az bicep", "az role assignment", "cost management", "resource locks"

**What it covers:**
- Pre-flight safety checks (subscription and identity verification)
- Authentication: interactive, device code, managed identity, service principal, federated credentials (OIDC)
- JMESPath queries and output formatting
- `az wait` patterns and parallel operations
- `az rest` for direct REST API calls and cost management queries
- `az graph` (KQL) for cross-subscription resource inventory
- Service patterns: VMs, Storage, VNets/NSGs, Key Vault, App Service, AKS, RBAC
- Dangerous command awareness with tiered risk levels and safer alternatives
- `az bicep` commands and deployment what-if
- Multi-subscription loops and scripting best practices

## Installation

```bash
# From marketplace
/plugin install aeo-infra@aeo-skill-marketplace

# Direct
/plugin install /opt/aeo/aeo-skill-marketplace/aeo-infra
```
