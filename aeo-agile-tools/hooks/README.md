# Agile Tools - Notification Hooks

Team alerting and notification system hooks for Claude Code operations.

## Blocking Behavior Warning

The original hooks used `"blocking": false` to make notifications advisory-only. Claude Code's hooks spec does not support a `blocking` field — **all hooks block by default** if the command exits non-zero. This means if a webhook endpoint is unreachable, the hook will fail and block the operation.

**For production use, append `|| true` to webhook commands** to prevent failures from blocking operations. For example:
```
curl -X POST ${SLACK_WEBHOOK} ... || true
```

## Event Mapping Caveats

The following events from the original configuration were remapped or removed:

| Original Event | New Mapping | Notes |
|---------------|-------------|-------|
| `PostCommit` | `PostToolUse` (matcher: `Bash`) | **Caveat:** Fires on ALL Bash tool completions, not just git commits. The hook command checks `git log` so it is benign on non-commit invocations, but it will execute more frequently than intended. |
| `PreDeploy` | Removed | No equivalent event in Claude Code hooks spec. |
| `PostDeploy` | Removed | No equivalent event in Claude Code hooks spec. |
| `OnError` | Removed | No equivalent event in Claude Code hooks spec. |
| `Stop` | `Stop` (kept) | Wrapped in correct `matcher`/`hooks` structure. |

## Removed Hooks (No Valid Equivalent)

### PreDeploy Notifications
- Slack notification of deployment start
- Email notification for deployment

### PostDeploy Notifications
- Slack notification of successful deployment
- Status page update (`python scripts/update_status_page.py --status operational`)
- GitHub release creation (`gh release create v${VERSION}`)

### OnError Notifications
- PagerDuty alerting for critical errors
- Slack error notification to #alerts channel

## Integration Configuration

The following integration metadata was stored in the original `notifications.json` and should be configured via environment variables or external config:

### Slack
- **Webhook URL:** Set `SLACK_WEBHOOK` environment variable
- **Channels:** `#deployments`, `#alerts`, `#commits`, `#security`

### PagerDuty
- **Webhook URL:** Set `PAGERDUTY_WEBHOOK` environment variable
- **Routing Key:** Configure separately

### Email
- **SMTP Server:** `smtp.example.com`
- **From Address:** `claude-code@example.com`
- **Team List:** `team@example.com`

### Discord
- **Webhook URL:** `https://discord.com/api/webhooks/YOUR/WEBHOOK`

### Microsoft Teams
- **Webhook URL:** `https://outlook.office.com/webhook/YOUR/WEBHOOK`

## Message Templates

- **Deployment:** `Deployment Alert - Project: ${PROJECT_NAME}, Version: ${VERSION}, Environment: ${ENVIRONMENT}, Deployed by: ${USER}, Status: ${STATUS}`
- **Error:** `Error Alert - Error: ${error}, File: ${file}, Line: ${line}, Action Required: ${action}`
- **Commit:** `New Commit - Author: ${author}, Message: ${message}, Files Changed: ${files}, Branch: ${branch}`

## Required Environment Variables

| Variable | Description |
|----------|-------------|
| `SLACK_WEBHOOK` | Slack incoming webhook URL |
| `PAGERDUTY_WEBHOOK` | PagerDuty events API endpoint |
| `ANALYTICS_WEBHOOK` | Custom analytics endpoint |
| `PROJECT_NAME` | Your project name |
| `VERSION` | Current version being deployed |
| `ENVIRONMENT` | Deployment environment (staging/production) |
