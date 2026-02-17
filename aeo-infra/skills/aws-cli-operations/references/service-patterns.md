# AWS CLI Service Patterns

Common service-specific CLI patterns distilled from operational practice.

## VPC Provisioning

```bash
# Create VPC
VPC_ID=$(aws ec2 create-vpc \
  --cidr-block 10.0.0.0/16 \
  --tag-specifications 'ResourceType=vpc,Tags=[{Key=Name,Value=my-vpc}]' \
  --query 'Vpc.VpcId' --output text)

# Enable DNS hostnames (required for RDS, EFS, many services)
aws ec2 modify-vpc-attribute --vpc-id $VPC_ID --enable-dns-hostnames

# Public subnet
PUB_SUBNET=$(aws ec2 create-subnet \
  --vpc-id $VPC_ID --cidr-block 10.0.1.0/24 \
  --availability-zone us-east-1a \
  --tag-specifications 'ResourceType=subnet,Tags=[{Key=Name,Value=public-1a}]' \
  --query 'Subnet.SubnetId' --output text)

# Private subnet
PRIV_SUBNET=$(aws ec2 create-subnet \
  --vpc-id $VPC_ID --cidr-block 10.0.10.0/24 \
  --availability-zone us-east-1a \
  --tag-specifications 'ResourceType=subnet,Tags=[{Key=Name,Value=private-1a}]' \
  --query 'Subnet.SubnetId' --output text)

# Internet Gateway
IGW_ID=$(aws ec2 create-internet-gateway \
  --tag-specifications 'ResourceType=internet-gateway,Tags=[{Key=Name,Value=my-igw}]' \
  --query 'InternetGateway.InternetGatewayId' --output text)
aws ec2 attach-internet-gateway --internet-gateway-id $IGW_ID --vpc-id $VPC_ID

# Route table for public subnet
PUB_RT=$(aws ec2 create-route-table --vpc-id $VPC_ID \
  --query 'RouteTable.RouteTableId' --output text)
aws ec2 create-route --route-table-id $PUB_RT \
  --destination-cidr-block 0.0.0.0/0 --gateway-id $IGW_ID
aws ec2 associate-route-table --route-table-id $PUB_RT --subnet-id $PUB_SUBNET

# Gateway endpoint for S3 (free — saves NAT costs)
aws ec2 create-vpc-endpoint \
  --vpc-id $VPC_ID \
  --service-name com.amazonaws.us-east-1.s3 \
  --route-table-ids $PUB_RT \
  --vpc-endpoint-type Gateway
```

**Gotchas:**
- VPC CIDR cannot be changed after creation (but secondary CIDRs can be added)
- Always create subnets in at least 2 AZs for HA
- NAT Gateway: ~$32/month + data processing — use VPC endpoints for S3/DynamoDB to reduce traffic
- NAT Gateway must be in a PUBLIC subnet

---

## Lambda Deployment

```bash
# Create function (arm64 is ~20% cheaper)
aws lambda create-function \
  --function-name my-function \
  --runtime python3.12 \
  --handler app.handler \
  --role arn:aws:iam::123456789012:role/LambdaRole \
  --zip-file fileb://function.zip \
  --memory-size 512 --timeout 30 \
  --architectures arm64 \
  --tags Environment=production

# Update code and publish version
aws lambda update-function-code \
  --function-name my-function \
  --zip-file fileb://function.zip \
  --publish

# Invoke (v2 requires --cli-binary-format for raw JSON payload)
aws lambda invoke \
  --function-name my-function \
  --payload '{"key":"value"}' \
  --cli-binary-format raw-in-base64-out \
  response.json

# Add permission for API Gateway / EventBridge / S3
aws lambda add-permission \
  --function-name my-function \
  --statement-id trigger-invoke \
  --action lambda:InvokeFunction \
  --principal apigateway.amazonaws.com \
  --source-arn "arn:aws:execute-api:us-east-1:123456789012:api-id/*"
```

**Gotchas:**
- `--timeout` default is 3s — almost always too short. Max is 900s (15 min).
- `--memory-size` also scales CPU. 1769 MB = 1 vCPU.
- `--publish` creates immutable version. Without it, only updates `$LATEST`.
- Max zip: 50 MB (250 MB unzipped). Use container images for larger (up to 10 GB).
- Forgetting `add-permission` is the #1 cause of "Lambda not triggered" issues.

---

## DynamoDB Operations

```bash
# Create table with GSI (on-demand billing)
aws dynamodb create-table \
  --table-name Orders \
  --key-schema AttributeName=PK,KeyType=HASH AttributeName=SK,KeyType=RANGE \
  --attribute-definitions \
    AttributeName=PK,AttributeType=S \
    AttributeName=SK,AttributeType=S \
  --billing-mode PAY_PER_REQUEST \
  --tags Key=Environment,Value=production

# Wait for table
aws dynamodb wait table-exists --table-name Orders

# Insert-only put (prevents overwrites)
aws dynamodb put-item \
  --table-name Orders \
  --item '{"PK":{"S":"ORDER#123"},"SK":{"S":"META"},"amount":{"N":"99.99"}}' \
  --condition-expression "attribute_not_exists(PK)"

# Query (partition key + sort key condition)
aws dynamodb query \
  --table-name Orders \
  --key-condition-expression "PK = :pk AND begins_with(SK, :prefix)" \
  --expression-attribute-values '{":pk":{"S":"ORDER#123"},":prefix":{"S":"ITEM#"}}'

# Enable Point-in-Time Recovery (essential before destructive ops)
aws dynamodb update-continuous-backups \
  --table-name Orders \
  --point-in-time-recovery-specification PointInTimeRecoveryEnabled=true
```

**Gotchas:**
- Only define `--attribute-definitions` for key attributes and GSI keys
- `status` is a reserved word — use `#s` alias via `--expression-attribute-names`
- `batch-write-item`: max 25 items, no condition expressions. Check `UnprocessedItems`.
- All values use DynamoDB JSON: `{"S":"string"}`, `{"N":"123"}`, `{"BOOL":true}`

---

## RDS Management

```bash
# Create instance (Secrets Manager-managed password)
aws rds create-db-instance \
  --db-instance-identifier prod-postgres \
  --db-instance-class db.r6g.xlarge \
  --engine postgres --engine-version 16.4 \
  --master-username admin \
  --manage-master-user-password \
  --allocated-storage 100 --storage-type gp3 \
  --multi-az --storage-encrypted \
  --backup-retention-period 14 \
  --deletion-protection \
  --copy-tags-to-snapshot \
  --tags Key=Environment,Value=production

# Always snapshot before changes
aws rds create-db-snapshot \
  --db-instance-identifier prod-postgres \
  --db-snapshot-identifier prod-postgres-pre-change-$(date +%Y%m%d)

# Delete with final snapshot (NEVER skip in production)
aws rds delete-db-instance \
  --db-instance-identifier dev-postgres \
  --final-db-snapshot-identifier dev-postgres-final-$(date +%Y%m%d)
```

**Gotchas:**
- `--manage-master-user-password` stores password in Secrets Manager (preferred over `--master-user-password`)
- `--storage-encrypted` cannot be changed after creation
- Instance class changes cause ~5-10 min downtime (failover in multi-AZ)
- Restored instances get NEW endpoints — update connection strings

---

## CloudWatch Observability

```bash
# Custom metric
aws cloudwatch put-metric-data \
  --namespace "MyApp" \
  --metric-data '[{
    "MetricName":"RequestLatency",
    "Value":42.5,
    "Unit":"Milliseconds",
    "Dimensions":[{"Name":"Environment","Value":"production"}]
  }]'

# Create alarm
aws cloudwatch put-metric-alarm \
  --alarm-name high-cpu \
  --metric-name CPUUtilization \
  --namespace AWS/EC2 \
  --statistic Average --period 300 --threshold 80 \
  --comparison-operator GreaterThanThreshold \
  --evaluation-periods 2 \
  --alarm-actions arn:aws:sns:us-east-1:123456789012:alerts \
  --dimensions Name=InstanceId,Value=i-0abc123

# Tail CloudWatch Logs
aws logs tail /aws/lambda/my-function --follow --since 1h
aws logs tail /aws/lambda/my-function --filter-pattern "ERROR" --follow

# Metric query (anomaly detection)
aws cloudwatch get-metric-data \
  --metric-data-queries '[{
    "Id":"cpu","MetricStat":{
      "Metric":{"Namespace":"AWS/EC2","MetricName":"CPUUtilization",
        "Dimensions":[{"Name":"InstanceId","Value":"i-0abc123"}]},
      "Period":300,"Stat":"Average"}}]' \
  --start-time $(date -d '1 hour ago' -u +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S)
```

**Gotchas:**
- `put-metric-data` accepts up to 1000 metrics per call with `--metric-data` array
- Custom metrics cost $0.30/metric/month (first 10 free)
- `aws logs tail` defaults to past 10 minutes; use `--since` for wider range

---

## SSM Parameter Store

```bash
# Store configuration (standard tier, free)
aws ssm put-parameter \
  --name "/myapp/production/db-host" \
  --value "db-prod.rds.amazonaws.com" \
  --type String \
  --tags Key=Environment,Value=production

# Store secret (encrypted with KMS)
aws ssm put-parameter \
  --name "/myapp/production/api-key" \
  --value "sk-secret-key" \
  --type SecureString \
  --key-id alias/myapp-key

# Get parameter (with decryption)
aws ssm get-parameter \
  --name "/myapp/production/api-key" \
  --with-decryption \
  --query 'Parameter.Value' --output text

# Get all params by path (hierarchical fetch)
aws ssm get-parameters-by-path \
  --path "/myapp/production/" \
  --recursive --with-decryption

# Update (overwrite required for existing params)
aws ssm put-parameter \
  --name "/myapp/production/db-host" \
  --value "new-db-host.rds.amazonaws.com" \
  --type String --overwrite
```

**Gotchas:**
- Standard tier: free, 10,000 params max, 4 KB max value, 40 TPS throughput
- Advanced tier: $0.05/param/month, 100,000 params, 8 KB values, higher throughput
- `SecureString` uses KMS — caller needs `kms:Decrypt` permission
- Without `--overwrite`, `put-parameter` fails on existing params
- Version history kept automatically; reference specific version with `:VERSION`

---

## Security Groups

```bash
# Create security group
SG_ID=$(aws ec2 create-security-group \
  --group-name web-server-sg \
  --description "Web server access" \
  --vpc-id $VPC_ID \
  --tag-specifications 'ResourceType=security-group,Tags=[{Key=Name,Value=web-sg}]' \
  --query 'GroupId' --output text)

# Allow SSH from specific IP
aws ec2 authorize-security-group-ingress \
  --group-id $SG_ID \
  --protocol tcp --port 22 \
  --cidr 203.0.113.0/32

# Allow HTTPS from anywhere
aws ec2 authorize-security-group-ingress \
  --group-id $SG_ID \
  --protocol tcp --port 443 \
  --cidr 0.0.0.0/0

# Audit: find open-to-world rules
aws ec2 describe-security-groups \
  --query 'SecurityGroups[?IpPermissions[?IpRanges[?CidrIp==`0.0.0.0/0`]]].{ID:GroupId,Name:GroupName}' \
  --output table
```

**Gotchas:**
- Default SG allows all outbound, no inbound — must explicitly add ingress rules
- SGs are stateful — return traffic is auto-allowed
- Changes take effect immediately, no restart needed
- Document rules before modifying; `revoke-security-group-ingress` can cause outages
