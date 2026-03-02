# Azure CLI Advanced Patterns

## Contents

- [Authentication and Credential Chain](#authentication-and-credential-chain)
- [JMESPath Query Patterns](#jmespath-query-patterns)
- [Output Formats](#output-formats)
- [Pagination](#pagination)
- [`az wait` Patterns](#az-wait-patterns)
- [`az rest` for Direct REST API Calls](#az-rest-for-direct-rest-api-calls)
- [Cost Management Queries (via `az rest`)](#cost-management-queries-via-az-rest)
- [Resources Without Dedicated CLI Commands](#resources-without-dedicated-cli-commands)
- [Extensions System](#extensions-system)
- [`az configure` and Environment Variables](#az-configure-and-environment-variables)
- [`az graph` (Azure Resource Graph)](#az-graph-azure-resource-graph)
- [`az bicep` Commands](#az-bicep-commands)
- [Multi-Subscription Loops](#multi-subscription-loops)
- [Scripting Best Practices](#scripting-best-practices)
- [Exit Codes](#exit-codes)
- [Quick Reference: Key Flags](#quick-reference-key-flags)

---

## Authentication and Credential Chain

### Login methods

```bash
az login                                 # interactive browser (WAM on Windows)
az login --use-device-code               # headless/SSH
az login --identity                      # managed identity (Azure-hosted)
az login --identity --client-id <ID>     # user-assigned managed identity
az login --service-principal \
  --username "$AZURE_CLIENT_ID" \
  --certificate /path/to/cert.pem \
  --tenant "$AZURE_TENANT_ID"            # certificate-based SP (preferred for CI/CD)
az login --service-principal \
  --username "$AZURE_CLIENT_ID" \
  --password "$AZURE_CLIENT_SECRET" \
  --tenant "$AZURE_TENANT_ID"            # secret-based SP (use cert instead when possible)
```

MFA is mandatory for user identities since October 2025. Service principals and managed identities are **not** affected.

### Credential preference (most to least secure)

1. **Managed identity** — zero credential management, Azure-hosted workloads only
2. **Federated credentials (OIDC)** — no secret at all; GitHub Actions, Kubernetes
3. **Certificate-based SP** — phishing-resistant, supports conditional access
4. **Client secret SP** — requires rotation; store in Key Vault

### Federated credentials (GitHub Actions OIDC)

```bash
# Create SP and federated credential
az ad sp create-for-rbac --name "github-sp" --role Contributor \
  --scopes /subscriptions/<SUB_ID>/resourceGroups/<RG> --json-auth

az ad app federated-credential create --id <APP_ID> --parameters '{
  "name": "github-main",
  "issuer": "https://token.actions.githubusercontent.com",
  "subject": "repo:<OWNER>/<REPO>:ref:refs/heads/main",
  "audiences": ["api://AzureADTokenExchange"]
}'
```

### DefaultAzureCredential chain (Azure SDKs)

Resolution order — first credential to return a token wins:

1. EnvironmentCredential (`AZURE_CLIENT_ID` + `AZURE_CLIENT_SECRET` or `AZURE_CLIENT_CERTIFICATE_PATH`)
2. WorkloadIdentityCredential (`AZURE_FEDERATED_TOKEN_FILE`)
3. ManagedIdentityCredential (Azure-hosted resources)
4. VisualStudioCredential / VSCodeCredential
5. **AzureCliCredential** (`az login` session — calls `az account get-access-token`)
6. AzurePowerShellCredential / AzureDeveloperCliCredential

### Token management

```bash
# Get ARM token
TOKEN=$(az account get-access-token --query accessToken --output tsv)

# Get token for specific resource
az account get-access-token --resource https://graph.microsoft.com
az account get-access-token --resource https://vault.azure.net

# Token cache: ~/.azure/msal_token_cache.json (Linux, plaintext)
# Always az logout before leaving shared machines
```

---

## JMESPath Query Patterns

All Azure CLI commands support `--query`. Queries execute client-side on JSON before output formatting.

```bash
# Dictionary access
az vm show -g MyRG -n MyVM --query "osProfile.adminUsername"

# Multiselect hash (renamed keys)
az vm show -g MyRG -n MyVM \
  --query "{VMName:name, Admin:osProfile.adminUsername, Location:location}"

# Array projection
az vm list -g MyRG \
  --query "[].{Name:name, OS:storageProfile.osDisk.osType}" --output table

# Filter with [?predicate]
az vm list -g MyRG --show-details \
  --query "[?powerState=='VM running'].{Name:name,IP:publicIps}" --output table

# Numeric comparison (backtick-quoted literals)
az vm list -g MyRG \
  --query "[?storageProfile.osDisk.diskSizeGb>=\`50\`].name"

# Built-in functions
az vm list -g MyRG --query "sort_by([], &name)[0:5].name" --output tsv
az vm list -g MyRG --query "[?contains(name,'web')].name"

# Scalar capture (tsv strips quotes)
VM_ID=$(az vm show -g MyRG -n MyVM --query id --output tsv)

# Pipe expression
az vm list -g MyRG \
  --query "[].{Name:name, Storage:storageProfile.osDisk.managedDisk.storageAccountType} | [?contains(Storage,'SSD')]"
```

**JMESPath gotchas:**
- String literals use single quotes inside the query: `'VM running'`
- Numeric literals use backticks: `` `50` ``
- `[]` flattens arrays; `[*]` preserves structure
- Queries are case-sensitive
- `--output tsv` with `--query` strips quotes — use for shell variable capture

---

## Output Formats

| Format | Flag | Use case |
|--------|------|----------|
| json | `--output json` | Default; piping to `jq`, scripting |
| jsonc | `--output jsonc` | Colorized JSON for terminals |
| table | `--output table` | Human-readable overview |
| tsv | `--output tsv` | Shell variable capture; piping |
| yaml | `--output yaml` | Readable alternative to JSON |
| none | `--output none` | Fire-and-forget (only exit code matters) |

```bash
# tsv — scalar capture without quotes
USER=$(az vm show -g MyRG -n MyVM --query "osProfile.adminUsername" --output tsv)

# tsv — multi-value (use --query to enforce column order)
az vm list -g MyRG --query "[].{Name:name, RG:resourceGroup}" --output tsv

# none — fire-and-forget
az vm start --ids "$VM_ID" --output none
```

---

## Pagination

```bash
# Basic pagination
az vm list --max-items 20
az vm list --max-items 20 --next-token "<token-from-previous>"

# Azure Resource Graph pagination (max 1000 per query)
az graph query -q "Resources | project name, type" --first 100
az graph query -q "Resources | project name, type" --first 100 --skip 100
```

---

## `az wait` Patterns

Polls a resource until a condition is met. Default: 30s interval, 3600s timeout.

```bash
# Wait for VM to finish provisioning
az vm wait -g MyRG -n MyVM --created

# Wait for resource group deletion
az group delete -n OldRG --yes --no-wait
az group wait -n OldRG --deleted

# Custom JMESPath condition
az vm wait -g MyRG -n MyVM \
  --custom "instanceView.statuses[?code=='PowerState/running']"

# Parallel creation with synchronized wait
VM1_ID=$(az vm create -g MyRG -n vm01 --image Ubuntu2204 --no-wait --query id --output tsv)
VM2_ID=$(az vm create -g MyRG -n vm02 --image Ubuntu2204 --no-wait --query id --output tsv)
az vm wait --created --ids "$VM1_ID" "$VM2_ID"

# Wait for deployment
az deployment group create -g MyRG --template-file main.bicep --no-wait
az deployment group wait -g MyRG -n <deployment-name> --created
```

Flags: `--created`, `--deleted`, `--exists`, `--updated`, `--custom <jmespath>`, `--interval N`, `--timeout N`

---

## `az rest` for Direct REST API Calls

Use when no dedicated CLI command exists. Automatically injects the Bearer token from your current login.

```bash
# GET
az rest --method get \
  --url "https://management.azure.com/subscriptions/$SUB/resourceGroups/$RG/providers/Microsoft.ContainerRegistry/registries/$ACR?api-version=2023-01-01-preview"

# PUT (create/replace)
az rest --method put --url "https://management.azure.com/..." \
  --body "{'location': 'westus', 'sku': {'name': 'Standard'}}"

# POST
az rest --method post --url "https://management.azure.com/.../regenerateCredential?api-version=..." \
  --body "{'name': 'password'}"

# Microsoft Graph
az rest --method GET --url "https://graph.microsoft.com/v1.0/applications/<app-object-id>"

# Body from file
az rest --method put --url "https://management.azure.com/..." --body @payload.json
```

---

## Cost Management Queries (via `az rest`)

There is no `az cost` or `az consumption` command group in the stable CLI. Use `az rest` against the CostManagement API to query spending data.

```bash
SUB_ID=$(az account show --query id --output tsv)

# Month-to-date cost grouped by resource group
az rest --method post \
  --url "https://management.azure.com/subscriptions/${SUB_ID}/providers/Microsoft.CostManagement/query?api-version=2023-11-01" \
  --body '{
    "type": "ActualCost",
    "timeframe": "MonthToDate",
    "dataset": {
      "granularity": "None",
      "aggregation": {"totalCost": {"name": "Cost", "function": "Sum"}},
      "grouping": [{"type": "Dimension", "name": "ResourceGroupName"}]
    }
  }' --query "properties.rows" --output json

# Custom date range, grouped by service
az rest --method post \
  --url "https://management.azure.com/subscriptions/${SUB_ID}/providers/Microsoft.CostManagement/query?api-version=2023-11-01" \
  --body '{
    "type": "ActualCost",
    "timeframe": "Custom",
    "timePeriod": {"from": "2026-02-01T00:00:00Z", "to": "2026-02-28T23:59:59Z"},
    "dataset": {
      "granularity": "None",
      "aggregation": {"totalCost": {"name": "Cost", "function": "Sum"}},
      "grouping": [{"type": "Dimension", "name": "ServiceName"}]
    }
  }' --query "properties.rows" --output json
```

**Supported timeframes:** `MonthToDate`, `BillingMonthToDate`, `WeekToDate`, `Custom` (requires `timePeriod`). The value `TheLastMonth` is **not** supported despite appearing in some documentation.

**Grouping dimensions:** `ResourceGroupName`, `ServiceName`, `ResourceType`, `ResourceLocation`, `MeterCategory`, `MeterSubCategory`, `ChargeType`, `PublisherType`.

**Rate limits:** The CostManagement API enforces aggressive throttling (~30 requests/5 minutes per subscription). Batch queries and add delays between calls when scripting multiple date ranges.

---

## Resources Without Dedicated CLI Commands

Some Azure resource types have no dedicated CLI command group. Use `az resource` for CRUD operations on these.

```bash
# Show a resource by full ID (works for any resource type)
az resource show \
  --ids "/subscriptions/<SUB>/resourceGroups/<RG>/providers/Microsoft.CodeSigning/codeSigningAccounts/<NAME>" \
  --query "{State:properties.provisioningState,SKU:sku}" --output json

# List resources of a specific type across the subscription
az resource list \
  --resource-type "Microsoft.CodeSigning/codeSigningAccounts" \
  --query "[].{Name:name,RG:resourceGroup,State:properties.provisioningState}" --output table

# Delete by resource ID
az resource delete --ids "/subscriptions/<SUB>/resourceGroups/<RG>/providers/<PROVIDER>/<TYPE>/<NAME>"
```

**Common resource types without CLI commands:** `Microsoft.CodeSigning/codeSigningAccounts`, `Microsoft.PortalServices/dashboards`, `Microsoft.Purview/accounts` (requires preview extension).

For more complex operations (custom request bodies, non-standard API versions), fall back to `az rest` with the full ARM URL.

---

## Extensions System

Extensions provide preview, experimental, and partner commands as Python wheels.

```bash
# Install by name
az extension add --name resource-graph    # az graph query
az extension add --name aks-preview       # AKS preview features
az extension add --name azure-devops      # az devops

# List installed / available
az extension list --output table
az extension list-available --output table

# Update / remove
az extension update --name <name>
az extension remove --name <name>

# Dynamic install (auto-install on first use)
az config set extension.use_dynamic_install=yes_without_prompt   # good for CI
az config set extension.use_dynamic_install=yes_prompt           # interactive

# Some extensions only have preview versions (e.g., purview, costmanagement)
# By default, preview-only extensions auto-install with warnings
# To suppress or control preview install behavior:
az config set extension.dynamic_install_allow_preview=true       # allow without prompting
az config set extension.dynamic_install_allow_preview=false      # block preview installs
```

**Preview extension behavior:** When a command requires an extension that only has a preview release (no stable version), the CLI auto-installs it and emits three warnings: "Preview version disabled by default", "The command requires the extension", and "The installed extension is in preview." These warnings are noisy but harmless — suppress them in scripts with `--only-show-errors`. Known preview-only extensions: `purview`, `costmanagement`, `fleet`, `connectedk8s`.

---

## `az configure` and Environment Variables

```bash
# Set defaults (saves typing --resource-group and --location)
az config set defaults.group=MyRG defaults.location=eastus2

# Suppress warnings (scripts)
az config set core.only_show_errors=true

# Default output format
az config set core.output=table

# Disable subscription selector prompt (2.61.0+)
az config set core.login_experience_v2=off

# Disable telemetry
az config set core.collect_telemetry=false
```

### Environment variables (override config file)

```bash
export AZURE_DEFAULTS_GROUP=MyRG
export AZURE_DEFAULTS_LOCATION=eastus2
export AZURE_CORE_ONLY_SHOW_ERRORS=true
export AZURE_CORE_OUTPUT=json

# Isolate config for concurrent scripts (CI matrix jobs)
export AZURE_CONFIG_DIR=$(mktemp -d)
az login --service-principal -u "$APP_ID" --certificate /path/to/cert.pem --tenant "$TENANT"
# ... do work ...
rm -rf "$AZURE_CONFIG_DIR"
```

Config file location: `~/.azure/config` (Linux/macOS), `%USERPROFILE%\.azure\config` (Windows).

---

## `az graph` (Azure Resource Graph)

Requires `resource-graph` extension. Uses Kusto Query Language (KQL). Cross-subscription by default.

```bash
az extension add --name resource-graph

# Count all resources
az graph query -q "Resources | summarize count()"

# VMs by OS type
az graph query -q "Resources
  | where type =~ 'Microsoft.Compute/virtualMachines'
  | extend os = properties.storageProfile.osDisk.osType
  | summarize count() by tostring(os)"

# Find resources by tag
az graph query -q "Resources
  | where tags.environment=~'production'
  | project name, resourceGroup, tags"

# Expand nested arrays (subnets in VNets)
az graph query -q "Resources
  | where type == 'microsoft.network/virtualnetworks'
  | extend subnets = properties.subnets
  | mv-expand subnets
  | project name, subnets.name, subnets.properties.addressPrefix"

# Find unassociated NSGs
az graph query -q "Resources
  | where type =~ 'microsoft.network/networksecuritygroups'
  | where isnull(properties.networkInterfaces) and isnull(properties.subnets)
  | project name, resourceGroup"

# Query specific subscription
az graph query -q "Resources | summarize count()" --subscriptions "$SUB_ID"
```

Max 1000 records per query. Use `--first` and `--skip` for pagination.

---

## `az bicep` Commands

```bash
# Install / upgrade
az bicep install
az bicep upgrade

# Build (Bicep → ARM JSON)
az bicep build --file main.bicep
az bicep build --file main.bicep --outdir ./output/

# Decompile (ARM JSON → Bicep)
az bicep decompile --file main.json

# Lint
az bicep lint --file main.bicep

# Deploy Bicep directly (no build step needed)
az deployment group create -g MyRG \
  --template-file main.bicep \
  --parameters @params.json --parameters location=eastus2

# What-if before deploying
az deployment group what-if -g MyRG \
  --template-file main.bicep --parameters @params.json

# Publish module to registry
az bicep publish --file module.bicep \
  --target "br:myregistry.azurecr.io/modules/mymodule:v1.0"
```

---

## Multi-Subscription Loops

```bash
# List all enabled subscriptions
az account list --query "[?state=='Enabled'].{Name:name, ID:id}" --output table

# Per-command override (no global switch needed)
az vm list --subscription "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx" --output table

# Loop across all subscriptions
while IFS=$'\t' read -r sub_id sub_name; do
  echo "=== $sub_name ($sub_id) ==="
  az account set --subscription "$sub_id"
  az group list --output table
done < <(az account list --query "[?state=='Enabled'].[id, name]" --output tsv)

# Cross-tenant: login with target tenant
az login --tenant <target-tenant-id>
# Or login as SP in target tenant
az login --service-principal -u "$APP_ID" --certificate /path/to/cert.pem --tenant "$TENANT_ID"
```

---

## Scripting Best Practices

```bash
#!/usr/bin/env bash
set -euo pipefail

# Always verify identity first
SUB=$(az account show --query name --output tsv)
echo "Operating on subscription: $SUB"

# Use --only-show-errors to suppress warnings
az vm list --only-show-errors --output table

# Use --subscription explicitly in scripts (never rely on default)
az vm list --subscription "$SUB_ID" --output table

# Parallel operations with --ids
az vm list -g MyRG --show-details \
  --query "[?powerState=='VM running'].id" --output tsv \
  | az vm stop --ids @-

# xargs for parallel fan-out
az vm list -g MyRG --show-details \
  --query "[?powerState=='VM stopped'].id" --output tsv \
  | xargs -I {} -P 5 az vm start --ids "{}"
```

### Script error handling

```bash
# Capture exit code for conditional logic (exit code 3 = not found)
az vm show -g MyRG -n MyVM --output none 2>/dev/null
rc=$?
if [[ $rc -eq 3 ]]; then
  echo "VM not found, creating..."
elif [[ $rc -ne 0 ]]; then
  echo "Unexpected error" >&2; exit 1
fi

# Retry pattern for transient errors
for attempt in 1 2 3; do
  az vm start --ids "$VM_ID" && break
  echo "Attempt $attempt failed, retrying..." >&2
  sleep $((attempt * 5))
done
```

---

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | General error |
| 2 | Parse/argument error |
| 3 | Resource not found (404) — allows distinguishing "missing" from "failed" |

```bash
az vm show -g MyRG -n NonExistentVM --output none 2>/dev/null
rc=$?
if [[ $rc -eq 3 ]]; then
  echo "VM does not exist, creating..."
elif [[ $rc -ne 0 ]]; then
  echo "Unexpected error" >&2; exit 1
fi
```

---

## Quick Reference: Key Flags

```
--query '<jmespath>'    — filter/transform output client-side
--output <format>       — json | jsonc | table | tsv | yaml | none
--only-show-errors      — suppress warnings; errors to stderr
--no-wait               — submit async operation, return immediately
--ids <resource-ids>    — accept one or more resource IDs (space-separated or @-)
--subscription <sub>    — override active subscription for this command
--verbose               — show HTTP request/response details
--debug                 — show all debug output including tokens (avoid in logs)
```
