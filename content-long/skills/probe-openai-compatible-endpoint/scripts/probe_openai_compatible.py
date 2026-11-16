#!/usr/bin/env python3
"""Probe an OpenAI-compatible HTTP endpoint.

Safe by default:
- Only loopback URLs are contacted unless you pass --allow-remote.
- --allow-remote is only for global (public) unicast addresses; RFC1918,
  link-local, metadata and other non-public ranges are refused even then
  (use --allow-private only if you really meant a private URL you typed).
- API keys come from an environment variable (default OPENAI_API_KEY) and
  are never printed. There is no --api-key flag.
- GET /v1/models is the default request.
- A chat smoke test or a tool-call check is opt-in (--smoke-test / --check-tools)
  and, for any non-loopback URL, also requires --allow-paid (at most one tiny
  chat request and one tools request).
- Redirects that change host, or that leave loopback, are refused.
"""
from __future__ import annotations

import argparse
import ipaddress
import json
import os
import socket
import ssl
import sys
import urllib.error
import urllib.parse
import urllib.request

TIMEOUT = 20
MAX_BODY = 1_000_000
MAX_REDIRECTS = 5
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


def is_loopback(ip: ipaddress._BaseAddress) -> bool:
    return ip.is_loopback


def is_nonpublic(ip: ipaddress._BaseAddress) -> bool:
    if ip.is_loopback or ip.is_private or ip.is_link_local or ip.is_multicast or ip.is_reserved or ip.is_unspecified:
        return True
    for net in NONPUBLIC_NETS:
        if ip in net:
            return True
    return False


def resolve_host(host: str) -> list[ipaddress._BaseAddress]:
    infos = socket.getaddrinfo(host, None, type=socket.SOCK_STREAM)
    addrs = []
    for info in infos:
        addrs.append(ipaddress.ip_address(info[4][0]))
    if not addrs:
        die(f"could not resolve {host}", 1)
    # unique, preserve order
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
    # strip trailing slash from path for joining; keep /v1 if present
    path = parsed.path or ""
    path = path.rstrip("/")
    return parsed._replace(path=path, fragment="")


def classify(parsed: urllib.parse.ParseResult, allow_remote: bool, allow_private: bool) -> str:
    """Return 'loopback' or 'remote'. Exits if the URL is not allowed."""
    host = parsed.hostname
    addrs = resolve_host(host)
    kinds = set()
    for a in addrs:
        if is_loopback(a):
            kinds.add("loopback")
        elif is_nonpublic(a):
            kinds.add("private")
        else:
            kinds.add("public")
    if "loopback" in kinds and kinds == {"loopback"}:
        return "loopback"
    if "loopback" in kinds and len(kinds) > 1:
        die(f"{host} resolved to a mix of loopback and non-loopback addresses; refusing")
    if "private" in kinds and not allow_private:
        die(
            f"{host} resolved to a non-public address ({', '.join(map(str, addrs))}). "
            "Refusing automatic probes of private, link-local or metadata addresses. "
            "If you typed this URL on purpose, pass --allow-private (and --allow-remote)."
        )
    if not allow_remote:
        die(
            f"{host} is not loopback. Default is loopback-only. "
            "Pass --allow-remote to probe a URL you specified, and --allow-paid "
            "before any chat or tool request that might cost money."
        )
    return "remote"


def join(base: urllib.parse.ParseResult, rel: str) -> str:
    # rel is like /models or /chat/completions; base path often ends with /v1
    path = base.path.rstrip("/")
    if rel.startswith("/v1/") and path.endswith("/v1"):
        # already has /v1
        suffix = rel[len("/v1"):]
        new_path = path + suffix
    elif rel.startswith("/"):
        new_path = path + rel
    else:
        new_path = path + "/" + rel
    return urllib.parse.urlunparse(base._replace(path=new_path, query="", fragment=""))



class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def request(method: str, url: str, *, token: str | None, body: dict | None, origin: urllib.parse.ParseResult, kind: str, timeout: int = 20):
    """HTTP request that refuses unsafe redirects. Returns (status, headers, obj_or_text)."""
    current = url
    data = None if body is None else json.dumps(body).encode("utf-8")
    for hop in range(MAX_REDIRECTS + 1):
        parsed = urllib.parse.urlparse(current)
        if parsed.scheme not in ("http", "https"):
            die(f"refusing redirect to {parsed.scheme}", 1)
        if parsed.hostname != origin.hostname:
            die(f"refusing redirect off host {origin.hostname} -> {parsed.hostname}", 1)
        # Re-check destination class
        addrs = resolve_host(parsed.hostname)
        if kind == "loopback" and not all(is_loopback(a) for a in addrs):
            die("refusing redirect or request that leaves loopback", 1)
        headers = {
            "Accept": "application/json",
            "User-Agent": "probe-openai-compatible-endpoint/1.0 (+https://indexagentica.com/skills/probe-openai-compatible-endpoint/)",
        }
        if data is not None:
            headers["Content-Type"] = "application/json"
        if token:
            headers["Authorization"] = "Bearer " + token
        req = urllib.request.Request(current, data=data, headers=headers, method=method)
        handlers = [NoRedirect()]
        # Never proxy loopback: a proxy would take the request (and any key) off the machine.
        if kind == "loopback":
            handlers.insert(0, urllib.request.ProxyHandler({}))
        if parsed.scheme == "https":
            handlers.append(urllib.request.HTTPSHandler(context=ssl.create_default_context()))
        opener = urllib.request.build_opener(*handlers)
        try:
            with opener.open(req, timeout=timeout) as resp:
                return _read(resp)
        except urllib.error.HTTPError as e:
            if e.code in (301, 302, 303, 307, 308):
                loc = e.headers.get("Location")
                if not loc:
                    die(f"HTTP {e.code} redirect without Location", 1)
                current = urllib.parse.urljoin(current, loc)
                if e.code in (301, 302, 303) and method == "POST":
                    # Do not silently convert a paid POST into a GET on another URL
                    die(f"refusing {e.code} redirect on {method} (Location present). Probe stopped.", 1)
                continue
            raw = e.read(MAX_BODY + 1)
            payload = _decode(raw, e.headers)
            return e.code, dict(e.headers), payload
        except urllib.error.URLError as e:
            die(f"request failed: {e}", 1)
    die("too many redirects", 1)


def _read(resp):
    raw = resp.read(MAX_BODY + 1)
    if len(raw) > MAX_BODY:
        die("response too large; stopping", 1)
    return resp.status, dict(resp.headers), _decode(raw, resp.headers)


def _decode(raw: bytes, headers):
    ctype = (headers.get("Content-Type") or "").lower()
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
    kind = classify(base, allow_remote=args.allow_remote, allow_private=args.allow_private)

    token = os.environ.get(args.api_key_env) or None
    if not token and kind != "loopback":
        # Many local servers accept a dummy key; remotes usually need a real one.
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

    models_url = join(base, "/v1/models")
    status, _headers, payload = request("GET", models_url, token=token, body=None, origin=base, kind=kind, timeout=timeout)
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
        status, _headers, payload = request("POST", chat_url, token=token, body=body, origin=base, kind=kind, timeout=timeout)
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
        status, _headers, payload = request("POST", chat_url, token=token, body=body, origin=base, kind=kind, timeout=timeout)
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
