# Deployment - Compliance and Regulatory Validation Hooks

Ensure regulatory compliance and security standards during Claude Code operations.

**Hooks are disabled by default.** The configuration below runs secret detection, PII checks, license checks, and command validation before every Bash command, plus audit logging on every Read/Edit. This is opinionated and project-specific — copy the relevant sections into your `hooks.json` selectively.

## Reference Configuration

To enable, copy desired entries into the `hooks` object in `hooks.json`:

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          { "type": "command", "command": "detect-secrets scan --baseline .secrets.baseline", "timeout": 30000 },
          { "type": "command", "command": "grep -r 'TODO:SECURITY' --include='*.py' --include='*.js' && echo 'Security TODOs must be resolved' && exit 1 || true", "timeout": 10000 },
          { "type": "command", "command": "python scripts/check_pii.py", "timeout": 30000 },
          { "type": "command", "command": "python scripts/license_check.py", "timeout": 30000 },
          { "type": "command", "command": "python scripts/validate_command.py '${command}' || (echo 'Command violates security policy' && exit 1)", "timeout": 10000 }
        ]
      },
      {
        "matcher": "WebSearch",
        "hooks": [
          { "type": "command", "command": "echo '$(date -u +%Y-%m-%dT%H:%M:%SZ),WEB_ACCESS,${query},${USER}' >> .claude/external_access.log", "timeout": 5000 }
        ]
      }
    ],
    "PostToolUse": [
      {
        "matcher": "Read",
        "hooks": [
          { "type": "command", "command": "echo '$(date -u +%Y-%m-%dT%H:%M:%SZ),READ,${file_path},${USER}' >> .claude/access.log", "timeout": 5000 }
        ]
      },
      {
        "matcher": "Edit",
        "hooks": [
          { "type": "command", "command": "echo '$(date -u +%Y-%m-%dT%H:%M:%SZ),MODIFY,${file_path},${USER}' >> .claude/access.log", "timeout": 5000 },
          { "type": "command", "command": "python scripts/validate_data_retention.py ${file_path}", "timeout": 10000 }
        ]
      }
    ]
  }
}
```

## Event Mapping Caveats

| Original Event | New Mapping | Notes |
|---------------|-------------|-------|
| `PreCommit` | `PreToolUse` (matcher: `Bash`) | **Caveat:** Fires on ALL Bash tool invocations, not just git commits. Secret detection, security TODO checks, PII checks, and license checks will run before every Bash command. Consider guarding commands with a git-specific check. |
| `PreDeploy` | Removed | No equivalent event in Claude Code hooks spec. |
| `PostToolUse` | `PostToolUse` (kept) | Already compliant structure. |
| `PreToolUse` | `PreToolUse` (kept) | Already compliant structure. Merged with PreCommit commands under Bash matcher. |

## Removed Hooks (No Valid Equivalent)

### PreDeploy
- Comprehensive compliance check via `security-reviewer` agent (GDPR, HIPAA, PCI-DSS, SOC2)
- Audit log entry creation (`python scripts/audit_log.py`)
- Deployment artifact signing (`openssl dgst -sha256`)
- Compliance report generation (`python scripts/compliance_report.py`)

## Compliance Frameworks

### GDPR
- PII detection
- Data retention validation
- Right to erasure implementation
- Consent management
- Data portability

### HIPAA
- PHI encryption
- Access controls
- Audit logging
- Data integrity
- Transmission security

### PCI-DSS
- Credit card data handling
- Encryption standards
- Access restrictions
- Network segmentation
- Security testing

### SOC2
- Security controls
- Availability monitoring
- Processing integrity
- Confidentiality measures
- Privacy controls

## Audit Requirements

| Setting | Value |
|---------|-------|
| Retention Period | 7 years |
| Log Format | ISO 8601 timestamp, action, resource, user, result |
| Encryption | AES-256 for data at rest, TLS 1.3 for data in transit |
| Access Control | Role-based access with principle of least privilege |

## Validation Scripts

### validate_command.py
Command validation against security policy. Blocks dangerous commands such as `rm -rf /`, `chmod 777`, `curl | bash`, and `eval(`.

### validate_data_retention.py
Checks data retention compliance. Flags files exceeding the 7-year retention period.

## Notes
- Customize compliance checks based on your regulatory requirements
- Regularly update validation scripts as regulations change
- Maintain audit logs in tamper-proof storage
- Test compliance hooks in staging before production
