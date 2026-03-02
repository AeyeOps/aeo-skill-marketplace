# Dangerous Azure CLI Commands Reference

Commands that destroy data, incur costs, or disrupt production. Always confirm subscription with `az account show` before executing.

## Contents

- [Tier 1: Irreversible Data Loss](#tier-1-irreversible-data-loss)
- [Tier 2: Service Disruption](#tier-2-service-disruption)
- [Tier 3: Cost Explosion](#tier-3-cost-explosion)
- [Pre-Execution Safety Checklist](#pre-execution-safety-checklist)
- [The --yes and --no-wait Danger](#the---yes-and---no-wait-danger)
- [Account-Level Guardrails](#account-level-guardrails)

## Tier 1: Irreversible Data Loss

These commands **permanently delete data** with no recovery path:

| Command | Risk | Safer Alternative |
|---------|------|-------------------|
| `az group delete --yes` | Deletes resource group and ALL resources (VMs, DBs, storage, vaults) | List first: `az resource list -g myRG --output table`; apply `CanNotDelete` lock |
| `az keyvault purge` | Permanently destroys soft-deleted vault — encryption keys lost forever | Enable purge protection: `az keyvault update --enable-purge-protection true` |
| `az storage account delete --yes` | Deletes entire account; bypasses blob soft delete | Apply `CanNotDelete` lock; enable blob + container soft delete first |
| `az cosmosdb delete --yes` | Deletes account and all databases — no built-in soft delete | Enable continuous backup before creation; apply resource lock |
| `az sql db delete --yes` | Deletes database; recoverable only within 7–35 day backup retention | Check retention: `az sql db show`; restore with `az sql db restore` |
| `az role assignment delete` (no `--assignee`) | Without `--assignee`, may match and delete more assignments than intended at the given scope | Always specify `--assignee` and `--role` explicitly |

## Tier 2: Service Disruption

These commands cause **immediate outages** or **access loss**:

| Command | Risk | Mitigation |
|---------|------|------------|
| `az vm deallocate` | Immediate service outage; dynamic public IP released | Check running workloads first; use `az vm stop` to keep IP allocated |
| `az vm delete --yes` | Orphans disks, NICs, public IPs, NSGs | Set `--os-disk-delete-option delete` at VM creation; or delete resource group |
| `az aks delete --yes --no-wait` | Destroys cluster, all workloads, PVs with Delete reclaim policy | Scale to 0 or `az aks stop` instead; apply resource lock |
| `az webapp stop` / `az webapp delete` | App offline immediately; delete removes config, history, slots | Back up settings: `az webapp config appsettings list --output json > backup.json` |
| `az network nsg rule delete` | Opens/closes traffic paths; no soft delete | Set rule to `--access Deny` instead of deleting |
| `az network vnet delete` | Destroys all subnet config, peering, route tables | Export config: `az network vnet show --output json > backup.json`; apply lock |

## Tier 3: Cost Explosion

These commands can **unexpectedly spike costs**:

| Command | Risk | Mitigation |
|---------|------|------------|
| `az vm resize --size Standard_M96s_v3` | ~$6.50/hr; GPU VMs up to $30+/hr | Check sizes: `az vm list-vm-resize-options`; set budget alert |
| `az aks nodepool add --node-count 20` | 20 nodes billing immediately; no autoscaler means idle cost | Use `--enable-cluster-autoscaler --min-count 1`; use spot VMs |
| `az storage account create --sku Premium_LRS` | Premium is ~10x standard per-GB cost | Check SKU before: `az storage account show --query sku` |
| `az cognitiveservices account create --sku S0` | No spending cap by default on OpenAI/AI services | Create budget alert: `az consumption budget create` |

## Pre-Execution Safety Checklist

Before any destructive command:

```bash
# 1. Verify subscription
az account show --output table

# 2. List what will be affected
az resource list --resource-group myRG --output table

# 3. What-if for ARM/Bicep deployments
az deployment group what-if \
  --resource-group myRG \
  --template-file main.bicep

# 4. Apply resource lock on production
az lock create \
  --name prod-lock \
  --lock-type CanNotDelete \
  --resource-group myProductionRG
```

## The --yes and --no-wait Danger

- `--yes` bypasses confirmation prompt — never use interactively
- `--no-wait` returns immediately; errors from background operation are lost
- **Combined `--yes --no-wait`**: highest-risk flag pattern — fires destructive operation, returns instantly, swallows errors
- **Rule**: Never combine on Tier 1/2 commands in production

## Account-Level Guardrails

### Resource Locks

```bash
# CanNotDelete — blocks delete, allows modify
az lock create --name protect-rg --lock-type CanNotDelete --resource-group myRG

# ReadOnly — blocks all modifications including delete
az lock create --name freeze-rg --lock-type ReadOnly --resource-group myRG

# List locks
az lock list --resource-group myRG --output table

# Remove (requires explicit intent)
az lock delete --name protect-rg --resource-group myRG
```

**Note**: Locks operate on the control plane only. A `CanNotDelete` lock on a storage account prevents account deletion but does NOT prevent deleting blobs inside it.

### Soft Delete Enablement

| Resource | Default | How to Enable |
|----------|---------|---------------|
| Key Vault soft delete | Yes (default; cannot be disabled) | Enforced on all vaults |
| Key Vault purge protection | **No** | `az keyvault update --enable-purge-protection true` (irreversible) |
| Storage blob soft delete | **No** | `az storage account blob-service-properties update --enable-delete-retention true` |
| Storage container soft delete | **No** | `az storage account blob-service-properties update --enable-container-delete-retention true` |
| Cosmos DB continuous backup | **No** | `az cosmosdb create --backup-policy-type Continuous` (at creation only) |
| SQL Database backup | Yes (7 days) | Configurable 1–35 days via backup retention policy |

### Cost Management

```bash
# Create monthly budget with alert
az consumption budget create \
  --budget-name monthly-limit \
  --amount 2000 \
  --time-grain Monthly \
  --category Cost

# Check current spending
az consumption usage list \
  --billing-period-name $(date +%Y%m) \
  --output table
```
