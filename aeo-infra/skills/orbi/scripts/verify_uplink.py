"""Check HTTPS reachability through one Windows or Linux IPv4 interface."""

import argparse
import http.client
import ipaddress
import re
import socket
import ssl
import struct
import sys


def interface_index(value):
    index = int(value)
    if not 1 <= index <= 0xFFFFFFFF:
        raise argparse.ArgumentTypeError("interface index must be between 1 and 4294967295")
    return index


def dns_hostname(value):
    name = value.removesuffix(".")
    label = r"[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?"
    if len(name) > 253 or not all(re.fullmatch(label, part) for part in name.split(".")):
        raise argparse.ArgumentTypeError("expected an ASCII DNS hostname")
    if name.rsplit(".", 1)[-1].isdigit():
        raise argparse.ArgumentTypeError("expected a DNS hostname with a nonnumeric final label")
    return name


def probe(index, source, address, hostname):
    context = ssl.create_default_context()
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(10)
        if sys.platform == "win32":
            # Winsock IP_UNICAST_IF takes a DWORD in network byte order.
            sock.setsockopt(socket.IPPROTO_IP, 31, struct.pack("!I", index))
        elif sys.platform.startswith("linux"):
            name = socket.if_indextoname(index)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_BINDTODEVICE, name.encode() + b"\0")
        else:
            raise OSError("interface binding is supported on Windows and Linux")
        sock.bind((str(source), 0))
        sock.connect((str(address), 443))
        with context.wrap_socket(sock, server_hostname=hostname) as tls:
            request = f"HEAD / HTTP/1.1\r\nHost: {hostname}\r\nConnection: close\r\n\r\n"
            tls.sendall(request.encode("ascii"))
            with http.client.HTTPResponse(tls, method="HEAD") as response:
                response.begin()
                return response.status


def main():
    parser = argparse.ArgumentParser(description=__doc__, epilog=(
        "Exit 0 for HTTP 2xx/3xx, 1 for a failed check, or 2 for invalid arguments. "
        "Redirects are reported without following them."
    ))
    parser.add_argument("--interface-index", required=True, type=interface_index)
    parser.add_argument("--source", required=True, type=ipaddress.IPv4Address,
                        help="local IPv4 address assigned to that interface")
    parser.add_argument("--address", type=ipaddress.IPv4Address, default="1.1.1.1",
                        help="destination IPv4 address (default: %(default)s)")
    parser.add_argument("--hostname", type=dns_hostname, default="one.one.one.one",
                        help="TLS server name and HTTP Host (default: %(default)s)")
    args = parser.parse_args()
    if args.source.is_unspecified:
        parser.error("--source must be an assigned address, not 0.0.0.0")

    path = f"interface {args.interface_index}, {args.source} -> {args.address}:443 ({args.hostname})"
    try:
        status = probe(args.interface_index, args.source, args.address, args.hostname)
    except (OSError, http.client.HTTPException) as error:
        print(f"{path}: {error}", file=sys.stderr)
        return 1
    print(f"{path}: HTTP {status}")
    return 0 if 200 <= status < 400 else 1


if __name__ == "__main__":
    sys.exit(main())
