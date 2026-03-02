---
name: az-cli-operations
version: 1.0.0
description: >-
  This skill should be used when the user asks about "Azure CLI commands",
  "writing Azure CLI scripts", "managing Azure resources", "az login",
  "az account", "service principal", "managed identity", "credential chain",
  or working with specific Azure services via CLI (VMs, Storage, VNets, NSGs,
  Key Vault, App Service, AKS, RBAC). Also applies when the user needs help
  with "JMESPath query", "--query syntax", "az graph query", "CLI pagination",
  "az wait", "output formatting", "multi-subscription", "resource locks",
  "safe destructive commands", "az rest API calls", "az bicep",
  "CLI extensions", "cost management", "cost analysis", "spending",
  or "az resource" for services without dedicated CLI commands.
---

# Azure CLI Operations

Guidance for using the Azure Command-Line Interface effectively and safely.

**Current version**: Azure CLI 2.83.0 (released 2026-02-03). MFA is mandatory for user identity logins since October 2025.

## Pre-Flight: Always Verify Context

Before executing ANY Azure CLI command, verify subscription and identity:

```bash
az account show --query "{Sub:name, ID:id, Tenant:tenantId}" --output table
```

**Never assume** which subscription is active. Environment variables, config defaults, and recent `az account set` calls can silently change the target.

---

## Core Principles

1. **Verify before mutating** — Always `az account show` before write/delete operations
2. **What-if first** — Use `az deployment group what-if` before ARM/Bicep deployments; no native `--dry-run` for individual `az` commands
3. **Query server-side** — Use `--query` (JMESPath) to reduce output; use `az graph query` (KQL) for cross-subscription inventory
4. **Use `tsv` for scripting** — `--output tsv` gives clean values without quotes; `--output none` when only exit code matters
5. **Pin subscription explicitly** — Always pass `--subscription` in scripts; never rely on the default context
6. **Use `--only-show-errors`** — Suppress warnings in scripts; let errors flow to stderr
7. **Prefer managed identity** — `az login --identity` for Azure-hosted workloads; service principal with certificate for CI/CD; federated credentials (OIDC) for GitHub Actions
8. **Resource locks for safety** — `az lock create --lock-type CanNotDelete` on production resource groups

---

## Essential Command Patterns

### Resource Discovery

```bash
# List all VMs with power state
az vm list --show-details \
  --query "[].{Name:name,RG:resourceGroup,State:powerState,Size:hardwareProfile.vmSize}" \
  --output table

# Find resources by tag across the subscription
az resource list \
  --tag Environment=production \
  --query "[].{Name:name,Type:type,RG:resourceGroup}" --output table

# Cross-subscription inventory via Resource Graph (KQL)
az graph query -q \
  "Resources | where type =~ 'Microsoft.Compute/virtualMachines' | project name, location, resourceGroup | order by name"
```

### Safe Mutation Pattern

```bash
# Step 1: Verify subscription
SUB=$(az account show --query name --output tsv)
echo "Subscription: $SUB"

# Step 2: What-if for Bicep/ARM deployments
az deployment group what-if \
  --resource-group myRG \
  --template-file main.bicep \
  --parameters @params.json

# Step 3: Deploy with confirmation
az deployment group create \
  --resource-group myRG \
  --template-file main.bicep \
  --confirm-with-what-if
```

### Authentication

```bash
az login                               # interactive browser (WAM on Windows)
az login --use-device-code             # headless/SSH
az login --identity                    # managed identity (Azure-hosted)
az login --service-principal \
  --username "$AZURE_CLIENT_ID" \
  --certificate /path/to/cert.pem \
  --tenant "$AZURE_TENANT_ID"          # certificate-based SP (preferred for CI/CD)
```

MFA is mandatory for user identities since October 2025. This does NOT affect service principals or managed identities. For full credential chain, federated credentials (OIDC), WAM, multi-tenant patterns, and token caching details, see [references/advanced-patterns.md#authentication-and-credential-chain](references/advanced-patterns.md#authentication-and-credential-chain).

### Storage Operations

```bash
# Upload blob (always use --auth-mode login over key auth)
az storage blob upload \
  --account-name mystorageacct \
  --container-name mycontainer \
  --file ./local.txt --name remote.txt \
  --auth-mode login

# Sync directory
az storage azcopy blob sync \
  --container mycontainer \
  --account-name mystorageacct \
  --source "./local-dir"
```

### Waiting for Resources

```bash
az vm wait -g myRG -n myVM --created
az deployment group wait -g myRG -n my-deployment --created
az group wait -n myRG --deleted
```

`az wait` polls with `--interval` (default 30s) and `--timeout` (default 3600s). Use `--custom` for JMESPath conditions. For parallel wait patterns and `--ids`, see [references/advanced-patterns.md#az-wait-patterns](references/advanced-patterns.md#az-wait-patterns).

---

## Output and Filtering

### `--query` (JMESPath)

All Azure CLI commands support `--query`. Queries execute client-side on the JSON response.

```bash
# Filter + project
az vm list --show-details \
  --query "[?powerState=='VM running'].{Name:name,IP:publicIps}" \
  --output table

# Scalar capture (tsv strips quotes)
VM_ID=$(az vm show -g myRG -n myVM --query id --output tsv)

# Built-in functions
az vm list --query "sort_by([], &name)[0:5].name" --output tsv
```

For JMESPath gotchas, filter predicates, and pipe expressions, see [references/advanced-patterns.md#jmespath-query-patterns](references/advanced-patterns.md#jmespath-query-patterns).

### Output Format Selection

- Shell scripts — `tsv` — `--output tsv`
- Debugging — `json` / `jsonc` — `--output json`
- Reports — `table` — `--output table`
- Documentation — `yaml` — `--output yaml`
- Fire-and-forget — `none` — `--output none`

---

## Script Safety Checklist

Verify before shipping:

- `set -euo pipefail` at script top
- `--only-show-errors` on all commands (or `az config set core.only_show_errors=true`)
- `--subscription` explicit on every command (never rely on default)
- `az account show` at script start to verify context
- No `--yes --no-wait` on destructive commands in production (swallows errors)
- Resource locks (`CanNotDelete`) on production resource groups
- Sensitive output (secrets, tokens) never piped to stdout unredacted
- No bare `az role assignment delete` without `--assignee` and `--role` (may match unintended assignments)

---

## Common Gotchas

- **MFA blocks automation**: User identity `az login -u/-p` fails with MFA since October 2025. Migrate to service principal or managed identity.
- **`az vm delete` orphans resources**: Disks, NICs, public IPs, and NSGs are NOT deleted. Clean up manually or delete the resource group.
- **`az vm stop` still bills**: Use `az vm deallocate` to actually stop billing for compute.
- **`--auth-mode login` for storage**: Default is key auth which bypasses Entra RBAC. Always pass `--auth-mode login`.
- **Basic LB retired**: Basic Load Balancer and default outbound access retired 2025-09-30. Use Standard LB.
- **Key Vault purge protection is irreversible**: Once enabled, cannot be disabled. Don't enable on dev/test vaults.
- **Exit code 3 = not found**: Azure CLI returns 3 (not 1) when a resource doesn't exist. Handle in `set -e` scripts.
- **`az role assignment delete` without `--assignee`**: May match and delete more assignments than intended at the given scope. Always specify `--assignee` and `--role`.
- **Azure Linux 2.0 EOL**: Node images removed March 31, 2026. Migrate AKS node pools to AzureLinux3 or Ubuntu.
- **Subscription selector prompt**: CLI 2.61.0+ shows interactive subscription picker after `az login`. Disable with `az config set core.login_experience_v2=off`.
- **No `az cost` command**: Cost Management has no CLI command group. Use `az rest` against the CostManagement query API. See [references/advanced-patterns.md#cost-management-queries-via-az-rest](references/advanced-patterns.md#cost-management-queries-via-az-rest).
- **Some resource types lack CLI commands**: CodeSigning, Purview (preview extension), Portal Dashboards have no dedicated `az` command group. Use `az resource show/list/delete` or `az rest`. See [references/advanced-patterns.md#resources-without-dedicated-cli-commands](references/advanced-patterns.md#resources-without-dedicated-cli-commands).
- **Preview extensions auto-install with warnings**: Extensions like `purview` only have preview releases and auto-install with noisy warnings. Suppress with `--only-show-errors`.

---

## Dangerous Commands Reference

Before running any destructive Azure CLI command, consult the safety reference for tiered risk commands (irreversible data loss, service disruption, cost explosion), safer alternatives, resource locks, and the `--yes`/`--no-wait` danger matrix: [references/dangerous-commands.md](references/dangerous-commands.md).

---

## Advanced Patterns Reference

For JMESPath queries, output formats, pagination, `az wait`, `az rest`, CLI extensions, `az configure`, environment variables, `az graph` (KQL), scripting best practices, exit codes, `az bicep`, multi-subscription loops, authentication and credential chain: [references/advanced-patterns.md](references/advanced-patterns.md).

---

## Service Patterns Reference

For Virtual Machines, Storage Accounts, Virtual Networks and NSGs, Key Vault, App Service, AKS, and RBAC role assignments: [references/service-patterns.md](references/service-patterns.md).
