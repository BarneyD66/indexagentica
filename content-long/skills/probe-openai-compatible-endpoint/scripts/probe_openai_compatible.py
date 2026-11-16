#!/usr/bin/env python3
"""Probe an OpenAI-compatible HTTP endpoint.

Safe by default:
- Only loopback URLs are contacted unless you pass --allow-remote.
- --allow-remote is only for global (public) unicast addresses; RFC1918,
  link-local, metadata and other non-public ranges are refused even then
  (use --allow-private only if you really meant a private URL you typed).
- Every address from a single getaddrinfo() is classified. A mix of
  classes (for example a public address and a private one) is refused.
  IPv4-mapped IPv6 addresses are treated as their IPv4 equivalents.
- The TCP connection is made to a pinned address from that lookup. The
  Host header stays the original name; HTTPS uses SNI and certificate
  verification against that name, not the IP. The hostname is not
  resolved again at connect time.
- API keys come from an environment variable (default OPENAI_API_KEY) and
  are never printed. There is no --api-key flag.
- GET /v1/models is the default request.
- A chat smoke test or a tool-call check is opt-in (--smoke-test / --check-tools)
  and, for any non-loopback URL, also requires --allow-paid (at most one tiny
  chat request and one tools request).
- Redirects are followed manually, with a hop cap. Each hop is resolved,
  classified and pinned again under the same flags. A redirect that leaves
  loopback, that fails classification, or that would turn a POST into a GET
  (301/302/303) is refused.
"""
from __future__ import annotations

import argparse
import http.client
import ipaddress
import json
import os
import socket
import ssl
import sys
import urllib.parse

TIMEOUT = 20
MAX_BODY = 1_000_000
MAX_REDIRECTS = 5
METADATA_ADDRS = {
    ipaddress.ip_address("169.254.169.254"),
    ipaddress.ip_address("fd00:ec2::254"),
}
# IPv4/IPv6 ranges we never treat as "remote public"
NONPUBLIC_NETS = [
    ipaddress.ip_network("0.0.0.0/8"),
    ipaddress.ip_network("10.0.0.0/8"),
    ipaddress.ip_network("100.64.0.0/10"),
    ipaddress.ip_network("127.0.0.0/8"),
    ipaddress.ip_network("169.254.0.0/16"),
    ipaddress.ip_network("172.16.0.0/12"),
    ipaddress.ip_network("192.0.0.0/24"),
    ipaddress.ip_network("192.0.2.0/24"),
    ipaddress.ip_network("192.168.0.0/16"),
    ipaddress.ip_network("198.18.0.0/15"),
    ipaddress.ip_network("198.51.100.0/24"),
    ipaddress.ip_network("203.0.113.0/24"),
    ipaddress.ip_network("224.0.0.0/4"),
    ipaddress.ip_network("240.0.0.0/4"),
    ipaddress.ip_network("255.255.255.255/32"),
    ipaddress.ip_network("::1/128"),
    ipaddress.ip_network("::/128"),
    ipaddress.ip_network("fc00::/7"),
    ipaddress.ip_network("fe80::/10"),
    ipaddress.ip_network("ff00::/8"),
    ipaddress.ip_network("2001:db8::/32"),
]


def die(msg, code=2):
    print(f"error: {msg}", file=sys.stderr)
    raise SystemExit(code)


def canonical_ip(value) -> ipaddress._BaseAddress:
    """Parse an IP and unwrap IPv4-mapped IPv6 (::ffff:x.x.x.x) to IPv4."""
    ip = value if isinstance(value, (ipaddress.IPv4Address, ipaddress.IPv6Address)) else ipaddress.ip_address(value)
    mapped = getattr(ip, "ipv4_mapped", None)
    if mapped is not None:
        return mapped
    return ip


def is_loopback(ip: ipaddress._BaseAddress) -> bool:
    return canonical_ip(ip).is_loopback


def is_metadata(ip: ipaddress._BaseAddress) -> bool:
    return canonical_ip(ip) in METADATA_ADDRS


def is_private_like(ip: ipaddress._BaseAddress) -> bool:
    """RFC1918 / ULA, link-local, and documented metadata addresses."""
    ip = canonical_ip(ip)
    if is_metadata(ip):
        return True
    if ip.is_private or ip.is_link_local:
        return True
    for net in (
        ipaddress.ip_network("10.0.0.0/8"),
        ipaddress.ip_network("100.64.0.0/10"),
        ipaddress.ip_network("169.254.0.0/16"),
        ipaddress.ip_network("172.16.0.0/12"),
        ipaddress.ip_network("192.168.0.0/16"),
        ipaddress.ip_network("fc00::/7"),
        ipaddress.ip_network("fe80::/10"),
    ):
        if ip in net:
            return True
    return False


def is_never_allowed(ip: ipaddress._BaseAddress) -> bool:
    """Multicast, reserved, unspecified, and documentation ranges: no flag allows these."""
    ip = canonical_ip(ip)
    if ip.is_multicast or ip.is_reserved or ip.is_unspecified:
        return True
    for net in (
        ipaddress.ip_network("0.0.0.0/8"),
        ipaddress.ip_network("192.0.0.0/24"),
        ipaddress.ip_network("192.0.2.0/24"),
        ipaddress.ip_network("198.18.0.0/15"),
        ipaddress.ip_network("198.51.100.0/24"),
        ipaddress.ip_network("203.0.113.0/24"),
        ipaddress.ip_network("224.0.0.0/4"),
        ipaddress.ip_network("240.0.0.0/4"),
        ipaddress.ip_network("255.255.255.255/32"),
        ipaddress.ip_network("::/128"),
        ipaddress.ip_network("ff00::/8"),
        ipaddress.ip_network("2001:db8::/32"),
    ):
        if ip in net:
            return True
    return False


def is_nonpublic(ip: ipaddress._BaseAddress) -> bool:
    ip = canonical_ip(ip)
    if is_loopback(ip) or is_private_like(ip) or is_never_allowed(ip):
        return True
    for net in NONPUBLIC_NETS:
        if ip in net:
            return True
    return False


def address_class(ip: ipaddress._BaseAddress) -> str:
    ip = canonical_ip(ip)
    if is_loopback(ip):
        return "loopback"
    if is_never_allowed(ip) and not is_private_like(ip):
        return "blocked"
    if is_private_like(ip):
        return "private"
    if is_nonpublic(ip):
        return "blocked"
    return "public"


def resolve_host(host: str) -> list[ipaddress._BaseAddress]:
    """One getaddrinfo(); IPv4-mapped results are unwrapped. Order preserved."""
    try:
        infos = socket.getaddrinfo(host, None, type=socket.SOCK_STREAM)
    except socket.gaierror as e:
        die(f"could not resolve {host}: {e}", 1)
    addrs = []
    for info in infos:
        addrs.append(canonical_ip(info[4][0]))
    if not addrs:
        die(f"could not resolve {host}", 1)
    out, seen = [], set()
    for a in addrs:
        if a not in seen:
            seen.add(a)
            out.append(a)
    return out


def normalize_base(url: str) -> urllib.parse.ParseResult:
    raw = url.strip()
    if not raw:
        die("empty --url")
    parsed = urllib.parse.urlparse(raw)
    if parsed.scheme not in ("http", "https"):
        die(f"only http and https URLs are allowed (got {parsed.scheme or 'no scheme'})")
    if not parsed.hostname:
        die("URL is missing a host")
    if parsed.username or parsed.password:
        die("do not put credentials in the URL; use an environment variable")
    path = parsed.path or ""
    path = path.rstrip("/")
    return parsed._replace(path=path, fragment="")


def resolve_and_classify(parsed: urllib.parse.ParseResult, allow_remote: bool, allow_private: bool) -> tuple[str, str, list[ipaddress._BaseAddress]]:
    """Resolve once, classify every address, pin the first allowed one.

    Returns (kind, pinned_ip, addresses). Exits if the URL is not allowed.
    """
    host = parsed.hostname
    addrs = resolve_host(host)
    classes = [address_class(a) for a in addrs]
    unique = set(classes)
    listed = ", ".join(map(str, addrs))

    if "blocked" in unique:
        die(
            f"{host} resolved to a reserved, multicast, unspecified or documentation address ({listed}); refusing"
        )
    if len(unique) > 1:
        die(
            f"{host} resolved to a mix of address classes ({listed}); refusing"
        )
    kind_class = next(iter(unique))
    if kind_class == "loopback":
        kind = "loopback"
    elif kind_class == "private":
        if not allow_private:
            die(
                f"{host} resolved to a non-public address ({listed}). "
                "Refusing automatic probes of private, link-local or metadata addresses. "
                "If you typed this URL on purpose, pass --allow-private (and --allow-remote)."
            )
        if not allow_remote:
            die(
                f"{host} is not loopback. Default is loopback-only. "
                "Pass --allow-remote to probe a URL you specified, and --allow-paid "
                "before any chat or tool request that might cost money."
            )
        kind = "remote"
    else:
        if not allow_remote:
            die(
                f"{host} is not loopback. Default is loopback-only. "
                "Pass --allow-remote to probe a URL you specified, and --allow-paid "
                "before any chat or tool request that might cost money."
            )
        kind = "remote"
    pinned = str(addrs[0])
    return kind, pinned, addrs


def join(base: urllib.parse.ParseResult, rel: str) -> str:
    path = base.path.rstrip("/")
    if rel.startswith("/v1/") and path.endswith("/v1"):
        suffix = rel[len("/v1"):]
        new_path = path + suffix
    elif rel.startswith("/"):
        new_path = path + rel
    else:
        new_path = path + "/" + rel
    return urllib.parse.urlunparse(base._replace(path=new_path, query="", fragment=""))


class PinnedHTTPConnection(http.client.HTTPConnection):
    def __init__(self, host, port, timeout, pinned_ip):
        super().__init__(host, port=port, timeout=timeout)
        self._pinned_ip = pinned_ip

    def connect(self):
        self.sock = socket.create_connection((self._pinned_ip, self.port), self.timeout)


class PinnedHTTPSConnection(http.client.HTTPSConnection):
    def __init__(self, host, port, timeout, pinned_ip, context):
        super().__init__(host, port=port, timeout=timeout, context=context)
        self._pinned_ip = pinned_ip

    def connect(self):
        sock = socket.create_connection((self._pinned_ip, self.port), self.timeout)
        context = self._context or ssl.create_default_context()
        # Verify the certificate against the original hostname, not the pinned IP.
        self.sock = context.wrap_socket(sock, server_hostname=self.host)


def _port_for(parsed: urllib.parse.ParseResult) -> int:
    if parsed.port:
        return parsed.port
    return 443 if parsed.scheme == "https" else 80


def _same_origin(a: urllib.parse.ParseResult, b: urllib.parse.ParseResult) -> bool:
    return (
        a.scheme == b.scheme
        and a.hostname == b.hostname
        and _port_for(a) == _port_for(b)
    )


def request(
    method: str,
    url: str,
    *,
    token: str | None,
    body: dict | None,
    origin: urllib.parse.ParseResult,
    origin_kind: str,
    pinned_ip: str,
    allow_remote: bool,
    allow_private: bool,
    allow_paid: bool,
    timeout: int = 20,
):
    """HTTP request with pinned connects and manual redirect handling.

    The caller's already-classified pin is reused for hops that stay on the
    same scheme/host/port, so connect() never triggers a second getaddrinfo
    for that origin. Any other hop is resolved, classified and pinned again.

    Returns (status, headers, obj_or_text).
    """
    current = url
    data = None if body is None else json.dumps(body).encode("utf-8")
    for _hop in range(MAX_REDIRECTS + 1):
        parsed = urllib.parse.urlparse(current)
        if parsed.scheme not in ("http", "https"):
            die(f"refusing redirect to {parsed.scheme}", 1)
        if parsed.username or parsed.password:
            die("do not put credentials in the URL; use an environment variable")
        if _same_origin(parsed, origin):
            kind, hop_pin = origin_kind, pinned_ip
        else:
            kind, hop_pin, _addrs = resolve_and_classify(
                parsed, allow_remote=allow_remote, allow_private=allow_private
            )
        if origin_kind == "loopback" and kind != "loopback":
            die("refusing redirect or request that leaves loopback", 1)
        if kind != "loopback" and method == "POST" and not allow_paid:
            die(
                "chat and tool probes against a non-loopback URL require --allow-paid "
                "(opt-in to a tiny paid request)"
            )
        headers = {
            "Accept": "application/json",
            "User-Agent": "probe-openai-compatible-endpoint/1.0.1 (+https://indexagentica.com/skills/probe-openai-compatible-endpoint/)",
        }
        if data is not None:
            headers["Content-Type"] = "application/json"
        if token:
            headers["Authorization"] = "Bearer " + token
        port = _port_for(parsed)
        host = parsed.hostname
        path = parsed.path or "/"
        if parsed.query:
            path = path + "?" + parsed.query
        try:
            if parsed.scheme == "https":
                conn = PinnedHTTPSConnection(
                    host, port, timeout, hop_pin, ssl.create_default_context()
                )
            else:
                conn = PinnedHTTPConnection(host, port, timeout, hop_pin)
            try:
                conn.request(method, path, body=data, headers=headers)
                resp = conn.getresponse()
                status = resp.status
                resp_headers = {k: v for k, v in resp.getheaders()}
                raw = resp.read(MAX_BODY + 1)
            finally:
                conn.close()
        except OSError as e:
            die(f"request failed: {e}", 1)
        if len(raw) > MAX_BODY:
            die("response too large; stopping", 1)
        if status in (301, 302, 303, 307, 308):
            loc = None
            for k, v in resp_headers.items():
                if k.lower() == "location":
                    loc = v
                    break
            if not loc:
                die(f"HTTP {status} redirect without Location", 1)
            if status in (301, 302, 303) and method == "POST":
                die(f"refusing {status} redirect on {method} (Location present). Probe stopped.", 1)
            current = urllib.parse.urljoin(current, loc)
            continue
        payload = _decode(raw, resp_headers)
        return status, resp_headers, payload
    die("too many redirects", 1)


def _decode(raw: bytes, headers):
    ctype = ""
    for k, v in headers.items():
        if k.lower() == "content-type":
            ctype = (v or "").lower()
            break
    text = raw.decode("utf-8", errors="replace")
    if "json" in ctype or text[:1] in "{[":
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            return text
    return text


def redact(value: str | None) -> str:
    if not value:
        return ""
    return "<redacted>"


def list_models(data) -> list:
    if isinstance(data, dict) and isinstance(data.get("data"), list):
        ids = []
        for item in data["data"]:
            if isinstance(item, dict) and "id" in item:
                ids.append(item["id"])
            else:
                ids.append(item)
        return ids
    return []


def first_content(message: dict) -> str:
    content = message.get("content")
    if isinstance(content, str):
        return content
    return json.dumps(content, ensure_ascii=False) if content is not None else ""


def main(argv=None):
    ap = argparse.ArgumentParser(
        description="Probe an OpenAI-compatible /v1 endpoint. Loopback-only by default; keys from env only."
    )
    ap.add_argument("--url", required=True, help="Base URL, usually ending in /v1 (e.g. http://127.0.0.1:8000/v1)")
    ap.add_argument(
        "--api-key-env",
        default="OPENAI_API_KEY",
        help="Name of the environment variable that holds the API key (default OPENAI_API_KEY). The value is never printed.",
    )
    ap.add_argument("--allow-remote", action="store_true", help="Allow a non-loopback URL you explicitly passed.")
    ap.add_argument(
        "--allow-private",
        action="store_true",
        help="Also allow a private/link-local URL you explicitly passed. Off by default.",
    )
    ap.add_argument(
        "--allow-paid",
        action="store_true",
        help="Opt in to a tiny chat and/or tools request on a non-loopback endpoint (may incur usage).",
    )
    ap.add_argument("--smoke-test", action="store_true", help="POST one short /chat/completions request (max_tokens=8).")
    ap.add_argument(
        "--check-tools",
        action="store_true",
        help="POST one /chat/completions request with a dummy tool to see if tool_calls are returned.",
    )
    ap.add_argument("--model", default="", help="Model id. Default: first id from GET /v1/models.")
    ap.add_argument("--timeout", type=int, default=TIMEOUT, help="Per-request timeout in seconds.")
    args = ap.parse_args(argv)

    timeout = max(1, args.timeout)

    base = normalize_base(args.url)
    kind, pinned_ip, _addrs = resolve_and_classify(
        base, allow_remote=args.allow_remote, allow_private=args.allow_private
    )

    token = os.environ.get(args.api_key_env) or None
    if not token and kind != "loopback":
        print(
            f"note: ${args.api_key_env} is unset. Requests will go without an Authorization header.",
            file=sys.stderr,
        )

    if (args.smoke_test or args.check_tools) and kind != "loopback" and not args.allow_paid:
        die("chat and tool probes against a non-loopback URL require --allow-paid (opt-in to a tiny paid request)")

    report = {
        "url": urllib.parse.urlunparse(base),
        "kind": kind,
        "api_key_env": args.api_key_env,
        "api_key_present": bool(token),
        "models": {"ok": False},
        "smoke_test": None,
        "tool_check": None,
    }

    req_kwargs = dict(
        token=token,
        origin=base,
        origin_kind=kind,
        pinned_ip=pinned_ip,
        allow_remote=args.allow_remote,
        allow_private=args.allow_private,
        allow_paid=args.allow_paid,
        timeout=timeout,
    )

    models_url = join(base, "/v1/models")
    status, _headers, payload = request("GET", models_url, body=None, **req_kwargs)
    ids = list_models(payload) if status == 200 else []
    report["models"] = {
        "ok": status == 200 and isinstance(payload, dict),
        "http_status": status,
        "endpoint": models_url,
        "ids": ids,
        "id_count": len(ids),
        "error": None if status == 200 else _short_err(payload),
    }

    model = args.model or (ids[0] if ids else "probe-model")

    if args.smoke_test:
        chat_url = join(base, "/v1/chat/completions")
        body = {
            "model": model,
            "messages": [{"role": "user", "content": "Reply with the single word pong."}],
            "max_tokens": 8,
            "temperature": 0,
        }
        status, _headers, payload = request("POST", chat_url, body=body, **req_kwargs)
        msg = {}
        if isinstance(payload, dict):
            choices = payload.get("choices") or []
            if choices and isinstance(choices[0], dict):
                msg = choices[0].get("message") or {}
        content = first_content(msg) if msg else ""
        report["smoke_test"] = {
            "ok": status == 200,
            "http_status": status,
            "endpoint": chat_url,
            "model": model,
            "finish_reason": (payload.get("choices") or [{}])[0].get("finish_reason") if isinstance(payload, dict) else None,
            "content_preview": content[:200],
            "error": None if status == 200 else _short_err(payload),
        }

    if args.check_tools:
        chat_url = join(base, "/v1/chat/completions")
        tools = [
            {
                "type": "function",
                "function": {
                    "name": "get_time",
                    "description": "Return the current time in a named timezone.",
                    "parameters": {
                        "type": "object",
                        "properties": {"timezone": {"type": "string"}},
                        "required": ["timezone"],
                    },
                },
            }
        ]
        body = {
            "model": model,
            "messages": [{"role": "user", "content": "Call get_time for timezone UTC."}],
            "tools": tools,
            "tool_choice": "auto",
            "max_tokens": 64,
            "temperature": 0,
        }
        status, _headers, payload = request("POST", chat_url, body=body, **req_kwargs)
        tool_calls = None
        finish = None
        if isinstance(payload, dict):
            choices = payload.get("choices") or []
            if choices and isinstance(choices[0], dict):
                finish = choices[0].get("finish_reason")
                msg = choices[0].get("message") or {}
                tool_calls = msg.get("tool_calls")
        report["tool_check"] = {
            "ok": status == 200,
            "http_status": status,
            "endpoint": chat_url,
            "model": model,
            "finish_reason": finish,
            "returned_tool_calls": bool(tool_calls),
            "tool_call_count": len(tool_calls) if isinstance(tool_calls, list) else 0,
            "tool_names": [
                (tc.get("function") or {}).get("name")
                for tc in (tool_calls or [])
                if isinstance(tc, dict)
            ]
            if isinstance(tool_calls, list)
            else [],
            "error": None if status == 200 else _short_err(payload),
            "notes": "A 200 without tool_calls means the server accepted tools but did not call one (or ignores tools). That is not proof of support.",
        }

    json.dump(report, sys.stdout, indent=2, ensure_ascii=False)
    sys.stdout.write("\n")
    if not report["models"]["ok"]:
        raise SystemExit(1)
    if args.smoke_test and report["smoke_test"] and not report["smoke_test"]["ok"]:
        raise SystemExit(1)
    if args.check_tools and report["tool_check"] and not report["tool_check"]["ok"]:
        raise SystemExit(1)
    return 0


def _short_err(payload) -> str:
    if isinstance(payload, dict):
        err = payload.get("error")
        if isinstance(err, dict) and "message" in err:
            return str(err["message"])[:300]
        return json.dumps(payload, ensure_ascii=False)[:300]
    return str(payload)[:300]


if __name__ == "__main__":
    raise SystemExit(main())
