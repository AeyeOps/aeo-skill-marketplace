---
name: secure-coding
description: |
  Secure coding practices covering input validation, secrets management, and authentication patterns.
  Activate when: validating user input, managing secrets, implementing authentication,
  handling authorization, encoding output, applying secure defaults, reviewing code security.
---

# Secure Coding Practices

## Input Validation

### Validation Strategy

```markdown
Validate at system boundaries:
1. All user input (forms, query params, headers, file uploads)
2. External API responses (don't trust third-party data)
3. Configuration files loaded at runtime
4. Data read from databases (defense in depth)

Validation approach:
- Allowlist over denylist (define what IS valid, not what isn't)
- Validate type, length, range, format, and business rules
- Reject invalid input — don't try to "fix" it
- Validate on the server side (client-side is for UX, not security)
```

### Common Validations

```python
# Email validation
import re
EMAIL_PATTERN = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")

def validate_email(email: str) -> str:
    email = email.strip().lower()
    if len(email) > 254:
        raise ValueError("Email too long")
    if not EMAIL_PATTERN.match(email):
        raise ValueError("Invalid email format")
    return email

# Numeric range validation
def validate_quantity(qty: int) -> int:
    if not isinstance(qty, int):
        raise TypeError("Quantity must be an integer")
    if qty < 1 or qty > 10000:
        raise ValueError("Quantity must be between 1 and 10000")
    return qty

# String sanitization
def validate_username(username: str) -> str:
    username = username.strip()
    if len(username) < 3 or len(username) > 30:
        raise ValueError("Username must be 3-30 characters")
    if not re.match(r"^[a-zA-Z0-9_-]+$", username):
        raise ValueError("Username may only contain letters, numbers, hyphens, underscores")
    return username
```

### File Upload Validation

```python
ALLOWED_EXTENSIONS = {".pdf", ".png", ".jpg", ".jpeg", ".docx"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB

def validate_upload(file) -> None:
    # Check file size
    if file.size > MAX_FILE_SIZE:
        raise ValueError("File too large (max 10MB)")

    # Check extension (use allowlist)
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise ValueError(f"File type not allowed: {ext}")

    # Check MIME type (don't trust Content-Type header alone)
    import magic
    mime = magic.from_buffer(file.read(2048), mime=True)
    file.seek(0)
    ALLOWED_MIMES = {"application/pdf", "image/png", "image/jpeg"}
    if mime not in ALLOWED_MIMES:
        raise ValueError(f"File content type not allowed: {mime}")

    # Generate safe filename (never use user-provided filename for storage)
    import uuid
    safe_name = f"{uuid.uuid4()}{ext}"
    return safe_name
```

## Output Encoding

### Prevent XSS (Cross-Site Scripting)

```markdown
Rule: Encode output based on the context where it appears.

HTML context:    Encode < > & " '   → &lt; &gt; &amp; &quot; &#x27;
Attribute:       Encode all non-alphanumeric characters
JavaScript:      Encode all non-alphanumeric characters as \xHH
URL:             Use percent-encoding for parameter values
CSS:             Encode all non-alphanumeric characters as \HHHHHH
```

```python
# VULNERABLE: Raw user input in HTML
html = f"<p>Welcome, {username}!</p>"

# FIXED: Use template engine with auto-escaping (Jinja2)
# Jinja2 auto-escapes by default:
# {{ username }}  →  renders as &lt;script&gt; not <script>

# FIXED: Manual escaping when needed
from markupsafe import escape
html = f"<p>Welcome, {escape(username)}!</p>"

# For JavaScript context:
import json
safe_js = json.dumps(user_data)  # JSON encoding is safe for JS context
script = f"<script>var data = {safe_js};</script>"
```

### Content Security Policy (CSP)

```markdown
Set CSP header to prevent inline scripts and unauthorized sources:

# Strict CSP (recommended)
Content-Security-Policy: default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; object-src 'none'; base-uri 'self'; form-action 'self'

What each directive does:
  default-src 'self'   — Only load resources from same origin
  script-src 'self'    — Only run scripts from same origin (blocks inline)
  object-src 'none'    — Block Flash, Java, other plugins
  base-uri 'self'      — Prevent base tag hijacking
  form-action 'self'   — Forms can only submit to same origin
```

## Secrets Management

### Never Hard-Code Secrets

```python
# VULNERABLE: Secrets in source code
API_KEY = "sk-1234567890abcdef"
DB_PASSWORD = "super_secret_password"

# FIXED: Load from environment
API_KEY = os.environ["API_KEY"]
DB_PASSWORD = os.environ["DB_PASSWORD"]

# FIXED: Use a secrets manager
from aws_secrets import get_secret
API_KEY = get_secret("my-app/api-key")
```

### Secret Storage Hierarchy

```markdown
Best to worst:
1. Secrets manager (AWS Secrets Manager, HashiCorp Vault, Azure Key Vault)
   - Automatic rotation, access control, audit logging
2. Environment variables (set by deployment system)
   - Not in code, but visible via /proc/environ, ps
3. Encrypted config files (decrypted at deploy time)
   - Key management becomes the problem
4. .env files (gitignored, never committed)
   - OK for local development only

NEVER:
- Commit secrets to git (even if you delete them later — they're in history)
- Log secrets (mask in log output)
- Pass secrets via URL parameters (logged by proxies)
- Store secrets in client-side code (JavaScript, mobile apps)
```

### Handling Secret Exposure

```markdown
If a secret is committed to git:
1. Rotate the secret IMMEDIATELY (generate new key/password)
2. Revoke the old secret in the service provider
3. Remove from git history: git filter-branch or BFG Repo-Cleaner
4. Force-push to all branches (after coordination with team)
5. Audit access logs for unauthorized use during exposure window
6. Add the secret pattern to .gitignore and pre-commit hooks
```

## Authentication Patterns

### Password Handling

```python
import bcrypt

def hash_password(password: str) -> str:
    """Hash a password for storage. Never store plaintext."""
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt(rounds=12)).decode("utf-8")

def verify_password(password: str, hashed: str) -> bool:
    """Verify a password against its hash. Use constant-time comparison."""
    return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))
```

```markdown
Password policy:
- Minimum 8 characters (NIST recommends no maximum under 64)
- Check against breach databases (Have I Been Pwned API)
- Do NOT require special characters or forced rotation (per NIST 800-63B)
- Allow paste into password fields (password managers)
- Provide strength meter for user feedback
```

### Token-Based Authentication (JWT)

```python
import jwt
from datetime import datetime, timedelta, timezone

SECRET_KEY = os.environ["JWT_SECRET"]
ALGORITHM = "HS256"

def create_token(user_id: int) -> str:
    payload = {
        "sub": str(user_id),
        "iat": datetime.now(timezone.utc),
        "exp": datetime.now(timezone.utc) + timedelta(hours=1),
        "jti": secrets.token_urlsafe(16),  # Unique token ID for revocation
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def verify_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise AuthError("Token expired")
    except jwt.InvalidTokenError:
        raise AuthError("Invalid token")
```

```markdown
JWT best practices:
- [ ] Use short expiration (15 min for access tokens)
- [ ] Use refresh tokens (longer-lived) stored securely
- [ ] Include jti (JWT ID) for revocation capability
- [ ] Validate algorithm on decode (prevent "none" algorithm attack)
- [ ] Store tokens in httpOnly, secure cookies (not localStorage)
- [ ] Use asymmetric keys (RS256) in distributed systems
```

### Session Management

```markdown
Secure session configuration:
- [ ] Generate session ID with secrets.token_urlsafe(32)
- [ ] Set cookie flags: HttpOnly, Secure, SameSite=Lax
- [ ] Regenerate session ID after login (prevent session fixation)
- [ ] Invalidate session on logout (server-side deletion)
- [ ] Set absolute timeout (e.g., 8 hours) and idle timeout (e.g., 30 min)
- [ ] Store session data server-side (not in the cookie itself)
```

## Authorization Patterns

### Role-Based Access Control (RBAC)

```python
from functools import wraps

PERMISSIONS = {
    "admin": {"read", "write", "delete", "manage_users"},
    "editor": {"read", "write"},
    "viewer": {"read"},
}

def require_permission(permission: str):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, current_user, **kwargs):
            user_permissions = PERMISSIONS.get(current_user.role, set())
            if permission not in user_permissions:
                raise PermissionError(f"Missing permission: {permission}")
            return func(*args, current_user=current_user, **kwargs)
        return wrapper
    return decorator

@require_permission("delete")
def delete_record(record_id: int, current_user):
    # Only admins reach here
    db.delete(record_id)
```

### Resource-Level Authorization

```python
def get_document(doc_id: int, current_user: User) -> Document:
    doc = db.query(Document).get(doc_id)
    if doc is None:
        raise NotFoundError("Document not found")  # Don't reveal existence to unauthorized
    if doc.owner_id != current_user.id and not current_user.is_admin:
        raise NotFoundError("Document not found")  # Same error — don't leak access info
    return doc
```

## Cryptography Basics

### When to Use What

```markdown
Hashing (one-way, not reversible):
  Passwords    → bcrypt, scrypt, Argon2 (with salt, high cost factor)
  Integrity    → SHA-256, SHA-3 (verify data hasn't been tampered with)
  NEVER use    → MD5, SHA-1 (broken for security purposes)

Symmetric encryption (same key for encrypt and decrypt):
  Data at rest → AES-256-GCM (authenticated encryption)
  Use case     → Encrypting files, database fields, backups
  Key mgmt     → Store keys in secrets manager, rotate regularly

Asymmetric encryption (public/private key pair):
  Data in transit → TLS (HTTPS)
  Signatures      → RSA, Ed25519 (verify sender identity)
  Use case        → Key exchange, digital signatures, JWT (RS256)
```

### Secure Random Numbers

```python
import secrets

# Generate random token
token = secrets.token_urlsafe(32)     # URL-safe base64 string
token = secrets.token_hex(32)          # Hex string

# Generate random integer
otp = secrets.randbelow(1000000)       # 0 to 999999

# NEVER use for security:
import random
random.randint(0, 999999)  # Predictable! Not cryptographically secure
```

## Secure Defaults

```markdown
Default-deny:
- Access denied unless explicitly granted
- Features disabled unless explicitly enabled
- Ports closed unless explicitly opened

Principle of least privilege:
- Services run with minimum required permissions
- Database users have minimum required grants
- API keys scoped to minimum required capabilities
- File permissions set to minimum needed (644 files, 755 dirs)

Fail securely:
- On error, deny access (don't fall through to allow)
- On exception, return generic error to user, log details internally
- On timeout, treat as failure (don't assume success)
```
