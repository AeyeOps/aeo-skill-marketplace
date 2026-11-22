# Local admin access and validation

These instructions cover the RBE971 interface serving the NETGEAR Orbi Router login page. Other firmware may present a different interface. Use its visible admin navigation if the form or menu differs.

From the skill directory, identify which local adapter reaches the intended gateway and which TLS certificate the gateway presents. Substitute the private addresses for your setup.

```text
python scripts/read_logs.py <gateway-ip> --source <local-ip> --identify
```

You can use normal certificate validation when the router presents a certificate trusted for its IP. For a locally issued certificate, verify the SHA-256 fingerprint against a trusted view of the intended router, then pass it as `--fingerprint`. The identification command reports the fingerprint presented on that connection. A changed pin warrants rechecking the device and certificate.

```text
python scripts/read_logs.py <gateway-ip> --source <local-ip> --fingerprint <sha256> --date YYYY-MM-DD
```

The interactive prompt hides the password. When the user specifically supplies a password in the Windows clipboard, this PowerShell invocation passes it directly to the helper on stdin. Use a PowerShell console or subprocess whose output goes only into the pipe. Do not echo the clipboard, put the password in a command argument, dump the HTML, or store a session in the skill.

```powershell
$OutputEncoding = [System.Text.UTF8Encoding]::new($false)
Get-Clipboard -Raw | python scripts/read_logs.py <gateway-ip> --fingerprint <sha256> --password-stdin --date YYYY-MM-DD
```

The verified login page registers an AJAX form handler. It submits the local `admin` username and password to `/ajax/web_login.cgi`. The ordinary HTML form action differs. Check the JSON `auth_ok` result and keep session cookies in memory for the subsequent same-origin GETs. The helper recognizes the index/start landing pages and follows the Logs link exposed by the menu. If login fails or the UI asks to displace another administrator, stop. Use the router-facing LAN for this workflow.

To validate access, require the authenticated Logs page and its log text area. A successful TCP connection, public login page, or HTTP 200 alone proves less. Compare any reported log time range with the incident window. A router restart can be relevant to log retention; use the entries actually present to establish coverage. Viewing logs or signing in can itself generate an admin-login entry.
