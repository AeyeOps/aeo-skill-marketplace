# Security - Security Gates Hooks

Security validation hooks for Claude Code operations. Provides file content scanning and command validation.

## Configuration

| Setting | Value |
|---------|-------|
| Severity threshold | medium |
| Block on failure | true |
| Audit all operations | true |
| Require approval for sensitive | true |

## Setup Instructions

1. Copy `security_check.py` and `command_security_check.sh` to your project `hooks/` directory
2. Make scripts executable: `chmod +x hooks/security_check.py hooks/command_security_check.sh`
3. Add the hooks configuration to your `.claude/settings.json`
4. Test the security hooks with safe and dangerous operations
5. Customize security rules by editing the script files

## Testing

### File Security
```bash
echo 'API_KEY="sk-1234567890"' > test.py
claude 'edit test.py to add a function'  # Should block secrets
```

### Command Security
```bash
claude 'run chmod 777 *'    # Should block dangerous permissions
claude 'run sudo apt update' # Should block sudo usage
claude 'run ls -la'          # Should work normally
```

## Customization

### security_check.py
- **sensitive_file_patterns:** Edit to add custom file patterns
- **secret_patterns:** Modify to detect specific secret formats
- **excluded_paths:** Add paths to exclude from secret scanning
- **permission_checks:** Customize file permission validation rules

### command_security_check.sh
- **dangerous_commands:** Edit `dangerous_patterns` array to block additional commands
- **confirmation_required:** Modify `confirmation_patterns` for operations requiring warning
- **allowed_sudo_exceptions:** Add specific sudo operations if needed (not recommended)
- **custom_validation:** Add domain-specific command validation rules

## Monitoring

| Setting | Value |
|---------|-------|
| Audit log location | `.claude/security-audit.log` |
| Log format | `TIMESTAMP EVENT_TYPE TOOL/COMMAND RESULT` |
| Log rotation | Automatically truncated to last 1000 entries |

## Integration Examples

- **CI/CD pipeline:** Use these hooks to block commits with secrets
- **Team enforcement:** Deploy via `.claude/settings.json` for team-wide security
- **Compliance reporting:** Parse audit logs for compliance documentation
- **Incident response:** Monitor audit logs for security violations
