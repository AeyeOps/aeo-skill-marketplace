---
name: deploy-checklist
version: 0.1.0
description: Pre-deployment validation checklist with environment verification, health checks, and rollback planning
argument-hint: "[environment]"
---

# Pre-Deployment Checklist

You are running a pre-deployment validation checklist. Delegate deployment expertise to the **deployment-agent** agent as needed. Walk through each phase interactively.

## Step 1: Deployment Context

Use AskUserQuestion to gather deployment details:

```
1. Target environment? (use $ARGUMENTS if provided)
   Options: staging / production / other
2. What is being deployed? (service name, version/tag)
3. Deployment strategy?
   Options: Blue-green / Canary / Rolling / Direct
4. Is this a scheduled deployment or hotfix?
5. Who is the deployment owner (on-call)?
```

## Step 2: Pre-Flight Checks

### Code Readiness
Run these checks and report status:

```markdown
## Code Readiness Checklist
- [ ] All CI/CD pipeline checks pass (build, lint, test)
- [ ] Code review approved and merged to deployment branch
- [ ] No open blocking issues tagged for this release
- [ ] Version/tag created and matches deployment artifact
- [ ] Database migrations tested (if applicable)
- [ ] Feature flags configured correctly
```

Use AskUserQuestion:
```
Confirm each code readiness item:
1. CI/CD pipeline status? (All green / Has failures)
2. Code review status? (Approved / Pending)
3. Any blocking issues? (None / List them)
4. Artifact version/tag? (provide the value)
```

### Environment Readiness
```markdown
## Environment Checklist
- [ ] Target environment is accessible
- [ ] Infrastructure resources are sufficient (CPU, memory, disk)
- [ ] Required environment variables and secrets are configured
- [ ] SSL certificates are valid and not expiring soon
- [ ] DNS records are correct
- [ ] Load balancer configuration is verified
- [ ] Network connectivity to dependencies confirmed
```

Delegate to the **deployment-agent** for environment verification:
```
Use the Task tool to spawn the deployment-agent:
- Verify infrastructure readiness for the target environment
- Check resource availability and scaling configuration
- Validate network connectivity to all dependencies
- Confirm secrets and environment variables are set
```

### Dependency Readiness
```markdown
## Dependencies Checklist
- [ ] Database is accessible and healthy
- [ ] Cache layer (Redis/Memcached) is responsive
- [ ] Message queue is operational
- [ ] External APIs are reachable
- [ ] Third-party services are not in maintenance
- [ ] Shared services are compatible with new version
```

## Step 3: Rollback Plan

### Rollback Validation

Use AskUserQuestion:
```
Rollback plan validation:
1. What is the rollback procedure?
   a. Redeploy previous version
   b. Switch traffic back (blue-green)
   c. Scale down canary to 0%
   d. Database rollback required
2. What is the previous known-good version?
3. Estimated rollback time? (seconds / minutes)
4. Is there a database migration that needs reversal?
```

### Rollback Checklist
```markdown
## Rollback Plan
- [ ] Previous version artifact is available and accessible
- [ ] Rollback procedure is documented and tested
- [ ] Database rollback scripts are prepared (if migration exists)
- [ ] Rollback can be executed within [X] minutes
- [ ] Rollback trigger criteria are defined:
  - Error rate exceeds [threshold]%
  - P99 latency exceeds [threshold]ms
  - Health check failures exceed [threshold] consecutive
  - Customer-impacting issue reported
- [ ] Rollback owner identified: [name]
```

### Data Migration Safety
If the deployment includes database changes:
```markdown
## Migration Safety
- [ ] Migration is backwards-compatible (old code works with new schema)
- [ ] Migration has been tested on a copy of production data
- [ ] Rollback migration exists and has been tested
- [ ] Migration estimated runtime: [duration]
- [ ] Migration can run without downtime
- [ ] Data backup taken before migration
```

## Step 4: Monitoring Setup

### Health Check Verification
```markdown
## Health Checks
- [ ] Readiness probe endpoint responds: GET /ready
- [ ] Liveness probe endpoint responds: GET /health
- [ ] Application-specific health checks pass:
  - [ ] Database connectivity
  - [ ] Cache connectivity
  - [ ] External service connectivity
- [ ] Health check thresholds are configured:
  - Readiness: [interval]s interval, [threshold] failures
  - Liveness: [interval]s interval, [threshold] failures
```

### Monitoring Dashboard
```markdown
## Monitoring Checklist
- [ ] Deployment dashboard is open and accessible
- [ ] Key metric alerts are configured:
  - Error rate (threshold: [X]%)
  - Response latency P50/P95/P99
  - CPU and memory utilization
  - Request throughput (requests/sec)
  - Active connections
- [ ] Log aggregation is capturing new version logs
- [ ] Alerting channels are configured (PagerDuty/Slack/email)
- [ ] On-call engineer is aware and available
```

## Step 5: Communication

### Stakeholder Notification
```markdown
## Communication Checklist
- [ ] Engineering team notified of deployment window
- [ ] On-call team is aware and available
- [ ] Customer support notified (if customer-facing changes)
- [ ] Status page updated (if applicable)
- [ ] Deployment channel announcement posted

Announcement template:
  :rocket: Deploying [service] v[version] to [environment]
  Owner: [name]
  Strategy: [blue-green/canary/rolling]
  Expected duration: [estimate]
  Rollback plan: [brief description]
```

## Step 6: Go / No-Go Decision

Present the checklist summary:

```markdown
## Deployment Readiness Summary

| Category          | Status | Issues |
|-------------------|--------|--------|
| Code Readiness    | ✅/❌  | [any]  |
| Environment       | ✅/❌  | [any]  |
| Dependencies      | ✅/❌  | [any]  |
| Rollback Plan     | ✅/❌  | [any]  |
| Monitoring        | ✅/❌  | [any]  |
| Communication     | ✅/❌  | [any]  |

Overall: READY / NOT READY
Blocking issues: [list if any]
```

Use AskUserQuestion for the final call:
```
Deployment Readiness Assessment:
[summary of checklist results]

Decision:
1. GO - Proceed with deployment
2. NO-GO - Defer deployment (list blocking reasons)
3. GO with conditions - Proceed with noted risks accepted
```

## Step 7: Post-Deployment Verification

After deployment, verify:

```markdown
## Post-Deployment Checks
- [ ] New version is running (check version endpoint or logs)
- [ ] Health checks are passing
- [ ] Error rate is within normal bounds
- [ ] Latency is within normal bounds
- [ ] Key user flows are functional (smoke tests)
- [ ] No unexpected errors in logs
- [ ] Monitoring dashboards show healthy metrics
- [ ] Deployment announcement updated with completion status
```

### Smoke Test Checklist
```markdown
## Smoke Tests
- [ ] Homepage/landing page loads
- [ ] Authentication flow works
- [ ] Primary user workflow succeeds
- [ ] API endpoints return expected responses
- [ ] Background jobs are processing
- [ ] Scheduled tasks are running
```

### Deployment Complete Announcement
```markdown
:white_check_mark: Deployment complete
  Service: [service] v[version]
  Environment: [environment]
  Duration: [time]
  Status: Healthy
  Monitoring: [dashboard link]
```
