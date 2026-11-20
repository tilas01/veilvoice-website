#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Serve site/ on this computer, with the same headers as the real server.

    python3 hosting/local/serve.py            # http://localhost:8000
    python3 hosting/local/serve.py --port 9000
    python3 hosting/local/serve.py --check    # start, fetch every page, stop

This is for reading the site offline and for looking at a change before it is
published. It listens on 127.0.0.1 only, so nothing outside this computer can
reach it, and that is also why it uses plain HTTP: the traffic never leaves
the machine, so there is nothing for TLS to protect.

The security headers are read from hosting/nginx/veilvoice-headers.conf, the
file the real server uses, so the two cannot drift apart and a page that
breaks under the real Content-Security-Policy breaks here first. The two
headers that only make sense over HTTPS are left out: Strict-Transport-Security
and the CSP's upgrade-insecure-requests.

Nothing is logged unless you ask with --verbose, matching the real server,
which keeps no access log. Standard library only.
"""

import argparse
import contextlib
import functools
import http.server
import re
import socket
import sys
import threading
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SITE = ROOT / "site"
HEADERS_FILE = ROOT / "hosting" / "nginx" / "veilvoice-headers.conf"

HTTPS_ONLY = {"strict-transport-security"}
ADD_HEADER = re.compile(r'^\s*add_header\s+(\S+)\s+"([^"]*)"\s+always;\s*$')


def security_headers():
    """The real server's headers, as (name, value) pairs, minus the HTTPS-only ones."""
    found = []
    for line in HEADERS_FILE.read_text(encoding="utf-8").splitlines():
        match = ADD_HEADER.match(line)
        if not match:
            continue
        name, value = match.groups()
        if name.lower() in HTTPS_ONLY:
            continue
        if name.lower() == "content-security-policy":
            value = "; ".join(
                part.strip() for part in value.split(";")
                if part.strip() and part.strip() != "upgrade-insecure-requests"
            )
        found.append((name, value))
    if not found:
        raise SystemExit(f"no headers found in {HEADERS_FILE}")
    return found


class Handler(http.server.SimpleHTTPRequestHandler):
    """Static files with fixed content types and the real server's headers.

    The content types are pinned because `mimetypes` answers from the
    machine's own tables, which differ between systems.
    """

    extensions_map = {
        **http.server.SimpleHTTPRequestHandler.extensions_map,
        ".html": "text/html; charset=utf-8",
        ".css": "text/css; charset=utf-8",
        ".js": "text/javascript; charset=utf-8",
        ".json": "application/json; charset=utf-8",
        ".svg": "image/svg+xml",
        ".png": "image/png",
        ".gif": "image/gif",
        ".webp": "image/webp",
        ".ico": "image/x-icon",
        ".woff2": "font/woff2",
        ".xml": "application/xml; charset=utf-8",
        ".txt": "text/plain; charset=utf-8",
        ".asc": "text/plain; charset=utf-8",
    }

    def __init__(self, *args, headers, verbose, **kwargs):
        self._headers = headers
        self._verbose = verbose
        super().__init__(*args, **kwargs)

    def end_headers(self):
        for name, value in self._headers:
            self.send_header(name, value)
        # Always the file as it is now, never a copy from an earlier run.
        self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def list_directory(self, path):
        # The real server never lists a folder, so neither does this one.
        self.send_error(404)
        return None

    def log_message(self, fmt, *args):
        if self._verbose:
            sys.stderr.write("  %s\n" % (fmt % args))


def make_server(port, verbose=False):
    if not (SITE / "index.html").exists():
        raise SystemExit(f"no site found at {SITE}; run tools/import-site.py first")
    handler = functools.partial(
        Handler, directory=str(SITE), headers=security_headers(), verbose=verbose
    )
    try:
        return http.server.ThreadingHTTPServer(("127.0.0.1", port), handler)
    except OSError as exc:
        raise SystemExit(f"could not use port {port}: {exc}") from exc


def pages():
    return sorted("/" + p.relative_to(SITE).as_posix() for p in SITE.rglob("*.html"))


def check(port):
    """Fetch every page once and report any that do not load."""
    server = make_server(port)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    base = f"http://127.0.0.1:{server.server_address[1]}"
    broken = []
    try:
        for page in pages():
            try:
                with urllib.request.urlopen(base + page, timeout=5) as response:
                    # Read the whole body: closing early leaves the server
                    # writing into a closed connection.
                    response.read()
                    if response.status != 200:
                        broken.append(f"{page}: HTTP {response.status}")
                    elif "Content-Security-Policy" not in response.headers:
                        broken.append(f"{page}: no Content-Security-Policy header")
            except Exception as exc:  # noqa: BLE001 - report every page, then fail once
                broken.append(f"{page}: {exc}")
    finally:
        server.shutdown()
        thread.join(timeout=2)
    for line in broken:
        print(f"  {line}")
    if broken:
        print(f"\n{len(broken)} page(s) did not load")
        return 1
    print(f"served {len(pages())} pages, each with the security headers")
    return 0


def free_port():
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--port", type=int, default=8000, help="default 8000")
    parser.add_argument("--check", action="store_true", help="fetch every page once, then stop")
    parser.add_argument("--verbose", action="store_true", help="print each request")
    args = parser.parse_args()
    if args.check:
        return check(free_port())
    server = make_server(args.port, args.verbose)
    print(f"VeilVoice website at http://localhost:{server.server_address[1]}  (Ctrl-C stops it)")
    with contextlib.suppress(KeyboardInterrupt):
        server.serve_forever()
    server.server_close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
