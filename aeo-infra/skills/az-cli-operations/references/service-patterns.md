# Azure CLI Service Patterns

Common service-specific CLI patterns distilled from operational practice.

## Contents

- [Virtual Machines (`az vm`)](#virtual-machines-az-vm)
- [Storage Accounts (`az storage`)](#storage-accounts-az-storage)
- [Virtual Networks (`az network`)](#virtual-networks-az-network)
- [Key Vault (`az keyvault`)](#key-vault-az-keyvault)
- [App Service (`az webapp`)](#app-service-az-webapp)
- [AKS (`az aks`)](#aks-az-aks)
- [RBAC (`az role`)](#rbac-az-role)

---

## Virtual Machines (`az vm`)

```bash
# Create Linux VM — Trusted Launch, system-assigned identity
az vm create \
  --resource-group rg-myapp-prod \
  --name vm-myapp-01 \
  --image Canonical:ubuntu-24_04-lts:server:latest \
  --size Standard_D2s_v5 \
  --security-type TrustedLaunch \
  --enable-secure-boot true --enable-vtpm true \
  --admin-username azureuser \
  --generate-ssh-keys \
  --public-ip-sku Standard \
  --os-disk-delete-option delete \
  --data-disk-delete-option delete \
  --nic-delete-option delete \
  --no-wait

# Spot VM (fault-tolerant workloads only)
az vm create \
  --resource-group rg-batch \
  --name vm-batch-01 \
  --image Ubuntu2204 \
  --size Standard_D4s_v5 \
  --priority Spot \
  --eviction-policy Deallocate \
  --max-price 0.05 \
  --admin-username azureuser \
  --generate-ssh-keys

# Discover images and sizes
az vm image list --output table                      # popular aliases
az vm image list --publisher Canonical --offer ubuntu-24_04-lts --sku server --all --output table
az vm list-sizes --location eastus --output table

# Stop + deallocate (stop billing for compute)
az vm deallocate --resource-group rg-myapp-prod --name vm-myapp-01

# List all VMs with power state
az vm list --show-details \
  --query "[].{Name:name,RG:resourceGroup,State:powerState,Size:hardwareProfile.vmSize}" \
  --output table

# Delete VM (orphans disks, NICs, public IPs, NSGs unless --*-delete-option was set at creation!)
az vm delete --resource-group rg-myapp-prod --name vm-myapp-01 --yes
# Then clean up orphaned resources manually

# Force-delete a stuck/deprovisioning VM
az vm delete --resource-group rg-myapp-prod --name vm-myapp-01 --force-deletion yes
```

**Gotchas:**
- `az vm delete` does NOT delete attached disks, NICs, public IPs, or NSGs unless `--os-disk-delete-option delete` (etc.) was set at VM creation. Clean up orphans manually or delete the resource group.
- `az vm stop` keeps the VM allocated — you still pay for compute. Always use `az vm deallocate`.
- `--image` short aliases (e.g., `Ubuntu2204`) resolve to Gen1 by default. Use full URNs for Gen2/Trusted Launch.
- Trusted Launch requires a Gen2 image; not compatible with ultra disks or ephemeral OS disks in some configs.
- Spot VMs with `--eviction-policy Delete` lose data on eviction — use `Deallocate` to preserve disks.
- `az vm deallocate` stops compute billing; managed disk storage charges continue.

---

## Storage Accounts (`az storage`)

```bash
# General-purpose v2, LRS — minimum viable
az storage account create \
  --resource-group rg-myapp-prod \
  --name stmyapp001 \
  --location eastus \
  --sku Standard_LRS \
  --kind StorageV2 \
  --min-tls-version TLS1_2 \
  --allow-blob-public-access false \
  --https-only true

# Create container (always use --auth-mode login)
az storage container create \
  --name mycontainer \
  --account-name stmyapp001 \
  --auth-mode login

# Upload blob
az storage blob upload \
  --container-name mycontainer \
  --file ./localfile.txt --name remotefile.txt \
  --account-name stmyapp001 \
  --auth-mode login

# Upload directory recursively
az storage blob upload-batch \
  --source ./local-dir \
  --destination mycontainer \
  --account-name stmyapp001 \
  --auth-mode login

# Generate SAS token (user delegation — no account key)
EXPIRY=$(date -u -d "+1 hour" '+%Y-%m-%dT%H:%MZ')
az storage blob generate-sas \
  --container-name mycontainer --name remotefile.txt \
  --permissions r --expiry "$EXPIRY" \
  --account-name stmyapp001 \
  --auth-mode login --as-user --output tsv

# Sync directory via AzCopy wrapper
az extension add --name storage-preview
az storage azcopy blob sync \
  --container mycontainer \
  --account-name stmyapp001 \
  --source "./local-dir"
```

**Gotchas:**
- Default auth is key-based unless you pass `--auth-mode login`. Key auth bypasses Entra RBAC — always use `--auth-mode login`.
- `--allow-blob-public-access false` disables anonymous access at the account level. Set this on all accounts.
- SKU redundancy conversions have restrictions: LRS to GZRS requires two hops with a 72-hour wait between.
- Enabling hierarchical namespace (Data Lake Gen2) cannot be undone.
- Lifecycle management policies auto-tier cold blobs to Cool/Cold/Archive — can cut costs significantly.

---

## Virtual Networks (`az network`)

```bash
# Create VNet
az network vnet create \
  --resource-group rg-myapp-prod \
  --name vnet-myapp-prod \
  --location eastus \
  --address-prefixes 10.0.0.0/16

# Add subnets
az network vnet subnet create \
  --resource-group rg-myapp-prod \
  --vnet-name vnet-myapp-prod \
  --name snet-app --address-prefixes 10.0.1.0/24

# Create NSG and rules
az network nsg create --resource-group rg-myapp-prod --name nsg-app

az network nsg rule create \
  --resource-group rg-myapp-prod --nsg-name nsg-app \
  --name allow-https-inbound --priority 100 \
  --direction Inbound --access Allow --protocol Tcp \
  --source-address-prefixes Internet \
  --destination-port-ranges 443

# Associate NSG with subnet
az network vnet subnet update \
  --resource-group rg-myapp-prod \
  --vnet-name vnet-myapp-prod --name snet-app \
  --network-security-group nsg-app

# Standard public IP (zone-redundant)
az network public-ip create \
  --resource-group rg-myapp-prod --name pip-lb-frontend \
  --sku Standard --allocation-method Static --zone 1 2 3

# Standard Load Balancer (Basic LB retired 2025-09-30)
az network lb create \
  --resource-group rg-myapp-prod --name lb-myapp \
  --sku Standard --frontend-ip-name fe-config \
  --public-ip-address pip-lb-frontend \
  --backend-pool-name be-pool
```

**Gotchas:**
- Basic LB and default outbound access both retired 2025-09-30. All new deployments must use Standard LB.
- Standard LB has no default inbound rules — NSGs must explicitly allow traffic or everything is dropped.
- Health probe source IP `168.63.129.16` must not be blocked by NSGs.
- Standard public IPs without `--zone` are non-zonal. Specify `--zone 1 2 3` for zone-redundant.
- Standard public IPs cost ~$0.005/hr even when not attached — delete idle IPs.

---

## Key Vault (`az keyvault`)

```bash
# Production vault — RBAC model, purge protection
az keyvault create \
  --resource-group rg-myapp-prod \
  --name kv-myapp-prod --location eastus \
  --enable-rbac-authorization true \
  --enable-purge-protection true \
  --retention-days 90 --sku standard

# Assign Key Vault Secrets Officer role
KV_ID=$(az keyvault show -g rg-myapp-prod -n kv-myapp-prod --query id -o tsv)
az role assignment create \
  --role "Key Vault Secrets Officer" \
  --assignee-object-id "$(az ad signed-in-user show --query id -o tsv)" \
  --assignee-principal-type User --scope "$KV_ID"

# Set a secret
az keyvault secret set --vault-name kv-myapp-prod \
  --name MyDbPassword --value "S3cr3tP@ssword!"

# Read a secret value
az keyvault secret show --vault-name kv-myapp-prod \
  --name MyDbPassword --query value --output tsv

# Create RSA key
az keyvault key create --vault-name kv-myapp-prod \
  --name MyRsaKey --kty RSA --size 4096

# Import certificate (PFX)
az keyvault certificate import --vault-name kv-myapp-prod \
  --name MyCert --file ./cert.pfx --password "pfxpassword"

# Grant app's managed identity read access
az role assignment create \
  --role "Key Vault Secrets User" \
  --assignee-object-id "$MI_OBJECT_ID" \
  --assignee-principal-type ServicePrincipal --scope "$KV_ID"
```

**Key Vault RBAC Roles:** Administrator (full control), Secrets Officer (CRUD secrets), Secrets User (read values), Certificates Officer, Crypto Officer, Crypto User, Reader (metadata only).

**Gotchas:**
- `--enable-purge-protection true` is irreversible. Don't enable on dev/test vaults unless required for compliance.
- Soft-delete is always on for new vaults and cannot be disabled. Vault names are held for the retention period in soft-deleted state.
- RBAC model is preferred over legacy access policies — access policies don't support PIM or object-level scoping.
- Standard tier: ~$0.03/10,000 operations. Premium required for HSM-protected keys (~$1/month per key).

---

## App Service (`az webapp`)

```bash
# Create plan and webapp (Linux, Python 3.12)
az appservice plan create \
  --resource-group rg-myapp-prod --name plan-myapp-prod \
  --location eastus --sku P1V3 --is-linux

az webapp create \
  --resource-group rg-myapp-prod --plan plan-myapp-prod \
  --name myapp-webapp-001 --runtime "PYTHON:3.12" \
  --assign-identity [system]

# ZIP deploy (preferred)
az webapp deploy \
  --resource-group rg-myapp-prod --name myapp-webapp-001 \
  --src-path ./app.zip --type zip

# App settings (become env vars in the app)
az webapp config appsettings set \
  --resource-group rg-myapp-prod --name myapp-webapp-001 \
  --settings DB_HOST="myserver.postgres.database.azure.com" APP_ENV="production"

# Key Vault reference syntax in app settings
az webapp config appsettings set \
  --resource-group rg-myapp-prod --name myapp-webapp-001 \
  --settings DB_PASSWORD="@Microsoft.KeyVault(SecretUri=https://kv-myapp-prod.vault.azure.net/secrets/MyDbPassword/)"

# Deployment slots — create, deploy, swap
az webapp deployment slot create \
  --resource-group rg-myapp-prod --name myapp-webapp-001 \
  --slot staging --configuration-source myapp-webapp-001

az webapp deployment slot swap \
  --resource-group rg-myapp-prod --name myapp-webapp-001 \
  --slot staging --target-slot production
```

**Gotchas:**
- Deployment slots require Standard tier or above.
- Slot swap warms up staging before swapping — health check failures cancel the swap.
- App settings marked "deployment slot setting" stay with the slot and are NOT swapped.
- Key Vault references require webapp's managed identity to have `Key Vault Secrets User` role. Missing RBAC causes silent failures.
- `az webapp deploy` (Kudu v2) replaces the older `az webapp deployment source config-zip`.
- P1V3/P2V3 offers better perf-per-dollar than P1V2/P2V2. Always-on requires Basic tier or above.

---

## AKS (`az aks`)

```bash
# Production cluster — managed identity, workload identity, OIDC
az aks create \
  --resource-group rg-myapp-prod --name aks-myapp-prod \
  --location eastus --node-count 3 --node-vm-size Standard_D4s_v5 \
  --enable-managed-identity --enable-oidc-issuer --enable-workload-identity \
  --network-plugin azure --network-policy azure \
  --enable-cluster-autoscaler --min-count 3 --max-count 10 \
  --zones 1 2 3 --generate-ssh-keys

# Get kubeconfig
az aks get-credentials -g rg-myapp-prod -n aks-myapp-prod --overwrite-existing

# Add spot node pool for batch workloads
az aks nodepool add \
  --resource-group rg-myapp-prod --cluster-name aks-myapp-prod \
  --name spotpool --node-count 2 --node-vm-size Standard_D4s_v5 \
  --priority Spot --eviction-policy Delete --spot-max-price -1 \
  --enable-cluster-autoscaler --min-count 0 --max-count 10

# Upgrade — control plane first, then node pools
az aks get-upgrades -g rg-myapp-prod -n aks-myapp-prod --output table
az aks upgrade -g rg-myapp-prod -n aks-myapp-prod \
  --kubernetes-version 1.31.0 --control-plane-only --yes

# Workload identity setup
MI_CLIENT_ID=$(az identity show -g rg-myapp-prod -n mi-myapp --query clientId -o tsv)
OIDC_ISSUER=$(az aks show -g rg-myapp-prod -n aks-myapp-prod --query oidcIssuerProfile.issuerUrl -o tsv)
az identity federated-credential create \
  --resource-group rg-myapp-prod --identity-name mi-myapp --name fc-myapp \
  --issuer "$OIDC_ISSUER" \
  --subject "system:serviceaccount:myapp-ns:myapp-sa" \
  --audience "api://AzureADTokenExchange"
```

**Gotchas:**
- Cannot upgrade and scale a node pool simultaneously — operations are mutually exclusive.
- Always upgrade control plane before node pools; node pools cannot be more than one minor version ahead.
- Azure Linux 2.0 node images removed March 31, 2026 — migrate to Azure Linux 3.0 or Ubuntu.
- `--enable-cluster-autoscaler` on `az aks create` applies to the default system node pool only; user pools need it separately.
- System node pools cannot be deleted; at least one system pool with one node is required.
- Pod Disruption Budgets block node drain during upgrades — validate PDBs before production upgrades.
- Workload identity replaces AAD Pod Identity (deprecated).

---

## RBAC (`az role`)

```bash
# List role assignments at subscription scope
az role assignment list --all --output table \
  --query "[].{Principal:principalName,Role:roleDefinitionName,Scope:scope}"

# Assign role by UPN
az role assignment create \
  --assignee "user@example.com" --role "Reader" \
  --scope "/subscriptions/<sub-id>/resourceGroups/rg-myapp-prod"

# Assign to service principal / managed identity (use object ID)
az role assignment create \
  --assignee-object-id "<object-id>" \
  --assignee-principal-type ServicePrincipal \
  --role "Storage Blob Data Contributor" \
  --scope "/subscriptions/<sub-id>/resourceGroups/rg-myapp-prod/providers/Microsoft.Storage/storageAccounts/stmyapp001"

# Delete assignment (ALWAYS specify --assignee and --role)
az role assignment delete \
  --assignee "user@example.com" --role "Reader" \
  --resource-group rg-myapp-prod

# Create custom role from JSON
az role definition create --role-definition @custom-role.json

# List custom roles
az role definition list --custom-role-only true --output table
```

**Gotchas:**
- Always use `--assignee-object-id` with `--assignee-principal-type` for service principals/managed identities. `--assignee` with display name or app ID can resolve ambiguously.
- Role assignment propagation takes up to 5 minutes — don't test access immediately after assigning.
- **DANGER**: `az role assignment delete` without `--assignee` may match and delete more assignments than intended at the given scope.
- Custom roles: limit of 5,000 per Entra tenant. `AssignableScopes` must include the target scope.
- Deny assignments can only be created by Azure Blueprints or Managed Applications — not via `az role`.
- RBAC has no direct cost. PIM (just-in-time activation) requires Entra ID P2 (~$9/user/month).
