"""Read the local NETGEAR Orbi 970 activity log through its admin UI."""
import argparse
from datetime import date
import getpass
import hashlib
import hmac
from http.client import HTTPSConnection
from http.cookies import SimpleCookie
from ipaddress import ip_address, ip_network
import json
import re
import ssl
import sys
from urllib.parse import urlencode
import warnings


def lan_ip(value):
    address = ip_address(value)
    private_lans = ("10.0.0.0/8", "172.16.0.0/12", "192.168.0.0/16", "fc00::/7")
    if not any(address in ip_network(network) for network in private_lans):
        raise ValueError("supply a private LAN management IP")
    return str(address)


class Router:
    def __init__(self, address, source, fingerprint):
        self.address = address
        self.source = (source, 0) if source else None
        self.pin = fingerprint
        self.cookies = {}
        self.origin = "https://" + (f"[{address}]" if ":" in address else address)

    def connect(self, identify=False):
        context = ssl.create_default_context()
        if self.pin or identify:
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
        conn = HTTPSConnection(self.address, timeout=8, context=context, source_address=self.source)
        conn.connect()
        actual = hashlib.sha256(conn.sock.getpeercert(binary_form=True)).hexdigest()
        if self.pin and not hmac.compare_digest(self.pin, actual):
            conn.close()
            raise ValueError("TLS fingerprint differs from the supplied pin")
        return conn, actual

    def request(self, path, form=None):
        conn, _ = self.connect()
        try:
            headers = {"Referer": self.origin + ("/WebLogin.htm?redirect=start.htm" if form else "/start.htm")}
            if self.cookies:
                headers["Cookie"] = "; ".join(f"{key}={value}" for key, value in self.cookies.items())
            body = None
            if form:
                headers.update({"Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
                                "Origin": self.origin, "X-Requested-With": "XMLHttpRequest"})
                body = urlencode(form).encode("ascii")
            conn.request("POST" if form else "GET", path, body, headers)
            reply = conn.getresponse()
            if reply.status != 200:
                raise ValueError(f"Orbi returned HTTP {reply.status} for {path.split('?')[0]}")
            for name, value in reply.getheaders():
                if name.lower() == "set-cookie":
                    self.cookies.update((k, m.value) for k, m in SimpleCookie(value).items())
            data = reply.read(2_000_001)
            if len(data) > 2_000_000:
                raise ValueError("page exceeds the expected size")
            return data.decode("utf-8", "replace")
        finally:
            conn.close()

    def read_log(self, password_from_stdin):
        page = self.request("/WebLogin.htm?redirect=start.htm")
        if "NETGEAR Orbi Router" not in page or not re.search(r"""\$\s*\.\s*post\(\s*["']ajax/web_login\.cgi["']""", page):
            raise ValueError("this router presents a different login flow; open its local admin UI")
        if password_from_stdin:
            password = sys.stdin.buffer.read().decode("utf-8-sig").removesuffix("\n").removesuffix("\r")
        else:
            with warnings.catch_warnings():
                warnings.simplefilter("error", getpass.GetPassWarning)
                try:
                    password = getpass.getpass("Local Orbi admin password: ")
                except getpass.GetPassWarning as exc:
                    raise ValueError("a private terminal is required; use --password-stdin for a secure pipe") from exc
        if not password or any(ch in password for ch in "\r\n\x00"):
            raise ValueError("supply one nonempty password line")
        result = json.loads(self.request("/ajax/web_login.cgi", {"username": "admin", "sysPasswd": password}))
        del password
        if not isinstance(result, dict) or result.get("auth_ok") not in (True, 1, "1", "true"):
            raise ValueError("Orbi did not confirm authentication; stopped after one submission")
        landing = str(result.get("redirect_to", "")).lstrip("/")
        if landing == "index.htm":
            index = self.request("/index.htm")
            if not re.search(r"\bstart\.htm\b", index):
                raise ValueError("use the router UI to navigate beyond this landing page")
        elif landing != "start.htm":
            raise ValueError("unexpected login landing page; check the local UI for an admin-session prompt")
        menu = self.request("/start.htm")
        if not re.search(r"\bFW_log\.htm\b", menu):
            raise ValueError("local admin menu did not advertise the expected Logs page")
        page = self.request("/FW_log.htm")
        if not re.search(r"""<textarea\b[^>]*(?:name|id)\s*=\s*["']?log_detail\b""", page, re.I):
            raise ValueError("Logs page layout differs; open Advanced > Administration > Logs")
        return page


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("address", type=lan_ip, help="private IP of the Orbi router")
    parser.add_argument("--source", type=lan_ip, help="bind to this local LAN adapter address")
    parser.add_argument("--identify", action="store_true", help="show local source IP and presented certificate SHA-256 without logging in")
    parser.add_argument("--fingerprint", help="SHA-256 of the locally verified router certificate, with optional colons")
    parser.add_argument("--password-stdin", action="store_true", help="read a single UTF-8 password line from stdin")
    parser.add_argument("--date", type=date.fromisoformat, help="summarize activity on this router-local date (YYYY-MM-DD)")
    args = parser.parse_args()
    fingerprint = args.fingerprint.replace(":", "").lower() if args.fingerprint else None
    if fingerprint is not None and not re.fullmatch("[0-9a-f]{64}", fingerprint):
        parser.error("invalid SHA-256 fingerprint")
    router = Router(args.address, args.source, fingerprint)
    if args.identify:
        conn, presented = router.connect(identify=True)
        try:
            print("Local source", conn.sock.getsockname()[0])
            print("Presented certificate SHA-256", presented)
        finally:
            conn.close()
        return
    from summarize_log import parse_entries, summarize
    log = router.read_log(args.password_stdin)
    print(json.dumps(summarize(parse_entries(log), args.date), indent=2, default=str))


if __name__ == "__main__":
    try:
        main()
    except (ValueError, OSError, EOFError) as exc:
        sys.exit(str(exc))
