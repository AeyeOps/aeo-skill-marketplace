---
name: owasp-top-10
description: |
  OWASP Top 10 vulnerabilities with detection patterns, code examples, and prevention checklists.
  Activate when: reviewing code for security, checking for OWASP vulnerabilities, performing security
  audits, fixing injection flaws, preventing XSS, securing authentication, checking access control.
---

# OWASP Top 10 Vulnerabilities

## A01: Broken Access Control

```markdown
Description: Users can act outside their intended permissions — accessing other users'
data, modifying records they shouldn't, or escalating privileges.

Detection patterns:
- URL parameter tampering: /api/users/123 → /api/users/456
- Missing authorization checks on API endpoints
- Direct object references without ownership verification
- Metadata manipulation (JWT role claim, hidden form fields)
- CORS misconfiguration allowing unauthorized origins
```

```python
# VULNERABLE: No authorization check — any user can view any profile
@app.get("/api/users/{user_id}")
def get_user(user_id: int):
    return db.query(User).get(user_id)

# FIXED: Verify the requesting user owns the resource
@app.get("/api/users/{user_id}")
def get_user(user_id: int, current_user: User = Depends(get_current_user)):
    if current_user.id != user_id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Forbidden")
    return db.query(User).get(user_id)
```

```markdown
Prevention checklist:
- [ ] Deny by default — require explicit grants, not explicit denials
- [ ] Enforce ownership checks on every data access
- [ ] Use server-side session for authorization (don't trust client)
- [ ] Disable directory listing on web servers
- [ ] Rate-limit API access to detect enumeration attempts
- [ ] Log access control failures and alert on patterns
```

## A02: Cryptographic Failures

```markdown
Description: Sensitive data exposed due to weak or missing encryption, including
data in transit, at rest, or during processing.

Detection patterns:
- HTTP instead of HTTPS for sensitive data
- Passwords stored in plaintext or weak hash (MD5, SHA1)
- Hard-coded encryption keys or secrets in source code
- Weak or deprecated TLS versions (TLS 1.0, 1.1)
- Sensitive data in URL parameters (logged by proxies)
```

```python
# VULNERABLE: Weak password hashing
import hashlib
hashed = hashlib.md5(password.encode()).hexdigest()

# FIXED: Use bcrypt with appropriate cost factor
import bcrypt
hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt(rounds=12))
```

```markdown
Prevention checklist:
- [ ] Classify data by sensitivity; apply controls accordingly
- [ ] Use TLS 1.2+ for all data in transit; enforce HSTS
- [ ] Hash passwords with bcrypt, scrypt, or Argon2 (never MD5/SHA1)
- [ ] Use authenticated encryption (AES-GCM, ChaCha20-Poly1305)
- [ ] Manage keys in a secrets vault (not in source code)
- [ ] Disable caching for responses containing sensitive data
```

## A03: Injection

```markdown
Description: User-supplied data is sent to an interpreter as part of a command
or query — allowing attackers to execute arbitrary commands.

Detection patterns:
- String concatenation in SQL queries
- User input passed directly to shell commands
- Template strings with user input (SSTI)
- LDAP, XPath, or NoSQL queries built from user input
- Dynamic code execution (eval, exec) with user input
```

```python
# VULNERABLE: SQL injection via string formatting
query = f"SELECT * FROM users WHERE email = '{email}'"
cursor.execute(query)

# FIXED: Parameterized query
cursor.execute("SELECT * FROM users WHERE email = %s", (email,))

# FIXED: ORM usage (SQLAlchemy)
user = session.query(User).filter(User.email == email).first()
```

```python
# VULNERABLE: Command injection
import os
os.system(f"convert {user_filename} output.png")

# FIXED: Use subprocess with argument list (no shell)
import subprocess
subprocess.run(["convert", user_filename, "output.png"], check=True)
```

```markdown
Prevention checklist:
- [ ] Use parameterized queries or ORM for all database access
- [ ] Use subprocess with argument lists instead of os.system/shell=True
- [ ] Validate and sanitize all user input on the server side
- [ ] Apply least-privilege database permissions
- [ ] Never use eval() or exec() with user-controlled input
- [ ] Use allowlists for expected input values where possible
```

## A04: Insecure Design

```markdown
Description: Fundamental design flaws that cannot be fixed by implementation
alone — missing threat modeling, insecure business logic, or absent controls.

Detection patterns:
- No rate limiting on authentication or sensitive operations
- Password reset via security questions (easily guessed)
- Business logic that trusts client-side calculations
- No account lockout after failed login attempts
- Missing audit trail for sensitive operations

Prevention checklist:
- [ ] Threat model during design phase
- [ ] Define security requirements alongside functional requirements
- [ ] Use secure design patterns (least privilege, defense in depth)
- [ ] Validate business logic on the server, never the client
- [ ] Implement rate limiting on sensitive endpoints
- [ ] Design with abuse cases in mind, not just use cases
```

## A05: Security Misconfiguration

```markdown
Description: Insecure defaults, incomplete configurations, verbose error messages,
or unnecessary features enabled in production.

Detection patterns:
- Default credentials still active (admin/admin)
- Debug mode enabled in production
- Verbose error messages exposing stack traces to users
- Unnecessary HTTP methods enabled (TRACE, DELETE)
- Missing security headers (CSP, X-Frame-Options, etc.)
- Cloud storage buckets publicly accessible
```

```python
# VULNERABLE: Debug mode in production
app = Flask(__name__)
app.run(debug=True)  # Exposes interactive debugger to attackers

# FIXED: Environment-based configuration
app = Flask(__name__)
app.config["DEBUG"] = os.environ.get("FLASK_DEBUG", "false").lower() == "true"
```

```markdown
Prevention checklist:
- [ ] Remove default credentials before deployment
- [ ] Disable debug mode, verbose errors, and stack traces in production
- [ ] Set security headers: CSP, HSTS, X-Content-Type-Options, X-Frame-Options
- [ ] Remove unnecessary features, endpoints, and sample code
- [ ] Automate configuration hardening with infrastructure-as-code
- [ ] Regularly scan for misconfigurations (cloud posture management)
```

## A06: Vulnerable and Outdated Components

```markdown
Description: Using components (libraries, frameworks, OS) with known vulnerabilities
or that are no longer maintained.

Detection patterns:
- Dependencies with known CVEs (check advisories)
- Libraries that haven't been updated in years
- Components past end-of-life (Python 2, Node 12, etc.)
- No automated dependency scanning in CI pipeline

Prevention checklist:
- [ ] Maintain an inventory of all components and versions
- [ ] Remove unused dependencies
- [ ] Monitor for CVEs: pip-audit, npm audit, Dependabot, Snyk
- [ ] Subscribe to security advisories for critical dependencies
- [ ] Update dependencies regularly (automated PRs via Dependabot/Renovate)
- [ ] Use lock files to ensure reproducible builds
```

## A07: Identification and Authentication Failures

```markdown
Description: Weaknesses in authentication that allow attackers to compromise
passwords, keys, or session tokens.

Detection patterns:
- Weak password policy (no minimum length, no complexity)
- Credential stuffing possible (no rate limiting on login)
- Session tokens in URL parameters
- Session not invalidated on logout or password change
- Missing multi-factor authentication for sensitive operations
```

```python
# VULNERABLE: Predictable session tokens
import random
session_id = str(random.randint(1, 999999))

# FIXED: Cryptographically random session tokens
import secrets
session_id = secrets.token_urlsafe(32)
```

```markdown
Prevention checklist:
- [ ] Enforce strong passwords (minimum 8 chars, check against breach lists)
- [ ] Implement MFA for login and sensitive operations
- [ ] Rate-limit and temporarily lock after repeated failed logins
- [ ] Use cryptographically random session tokens
- [ ] Invalidate sessions on logout, password change, and timeout
- [ ] Never expose session tokens in URLs or logs
```

## A08: Software and Data Integrity Failures

```markdown
Description: Code and infrastructure that doesn't verify integrity — insecure
CI/CD pipelines, auto-updates without verification, or deserialization of untrusted data.

Detection patterns:
- Deserializing untrusted data (pickle, Java serialization, YAML load)
- CI/CD pipeline without integrity checks on artifacts
- Dependencies pulled without checksum verification
- Auto-update mechanism without signature verification
```

```python
# VULNERABLE: Deserializing untrusted data
import pickle
data = pickle.loads(user_input)  # Arbitrary code execution!

# FIXED: Use safe serialization formats
import json
data = json.loads(user_input)  # Only parses data, no code execution
```

```markdown
Prevention checklist:
- [ ] Never deserialize untrusted data with pickle, eval, or yaml.load
- [ ] Use json, yaml.safe_load, or schema-validated parsers
- [ ] Verify integrity of dependencies (checksums, lock files)
- [ ] Sign and verify CI/CD artifacts
- [ ] Implement code review for CI/CD pipeline changes
```

## A09: Security Logging and Monitoring Failures

```markdown
Description: Insufficient logging, missing monitoring, or lack of incident response
capability — attacks go undetected.

Detection patterns:
- No logging of authentication events (login, logout, failures)
- Logs don't include enough context (who, what, when, where)
- No alerting on suspicious patterns (brute force, enumeration)
- Logs stored only locally (lost if server compromised)
- No incident response plan

Prevention checklist:
- [ ] Log all authentication events (success and failure)
- [ ] Log all access control failures
- [ ] Log all input validation failures (potential attack probes)
- [ ] Include context: timestamp, user ID, IP, action, result
- [ ] Ship logs to centralized, tamper-resistant storage
- [ ] Set up alerts for suspicious patterns
- [ ] Never log sensitive data (passwords, tokens, PII)
- [ ] Test that logging works (include in incident response drills)
```

## A10: Server-Side Request Forgery (SSRF)

```markdown
Description: Application fetches a remote resource using a user-supplied URL
without validation — allowing attackers to reach internal services.

Detection patterns:
- User can provide a URL that the server fetches
- No allowlist for permitted domains or IP ranges
- Internal metadata endpoints accessible (169.254.169.254)
- URL redirects not followed safely
```

```python
# VULNERABLE: Fetch any URL the user provides
import requests
response = requests.get(user_provided_url)

# FIXED: Validate URL against allowlist
from urllib.parse import urlparse

ALLOWED_HOSTS = {"api.example.com", "cdn.example.com"}

def safe_fetch(url: str):
    parsed = urlparse(url)
    if parsed.hostname not in ALLOWED_HOSTS:
        raise ValueError(f"Host not allowed: {parsed.hostname}")
    if parsed.scheme not in ("http", "https"):
        raise ValueError(f"Scheme not allowed: {parsed.scheme}")
    return requests.get(url, allow_redirects=False, timeout=10)
```

```markdown
Prevention checklist:
- [ ] Validate and sanitize all user-supplied URLs
- [ ] Use allowlists for permitted domains and protocols
- [ ] Block requests to private/internal IP ranges (10.x, 172.16.x, 192.168.x, 169.254.x)
- [ ] Disable HTTP redirects or re-validate after redirect
- [ ] Use network-level segmentation (services can't reach metadata endpoints)
- [ ] Monitor outbound requests for anomalies
```
