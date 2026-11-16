---
name: probe-openai-compatible-endpoint
description: "Probe any OpenAI-compatible HTTP endpoint (a local server such as Ollama, llama.cpp, vLLM or LiteLLM, or a hosted inference API). Discovers the base URL, lists models via GET /v1/models, optionally runs a tiny chat smoke test and a tool-call check, and reports what the server accepted. Use when pointing an agent or an OpenAI SDK at a new base_url, when a local or cloud /v1 URL might be wrong, or when you need to know whether an endpoint lists models and accepts tools. Safe by default: loopback-only, keys from environment variables only (never printed), and paid remote chat or tool requests are opt-in."
license: MIT
compatibility: "Needs Python 3.9 or later (standard library only). By default the script contacts only a loopback URL you pass. Remote or private URLs need explicit flags. An API key, if required, is read from an environment variable and never printed."
metadata:
  title: Probe an OpenAI-compatible endpoint
  summary: A read-only-by-default Python probe that lists models on an OpenAI-compatible /v1 endpoint, with opt-in chat and tool-call checks, loopback default, and keys from env only.
  author: Agentica Author
  version: "1.0.1"
  last_verified: 2026-11-16
  published: 2026-11-16
  tags: openai-compatible, inference, local-llm, tool-calling, probe
  entries: litellm, vllm, ollama, llama-cpp, localai
  related: run-an-agent-on-a-local-model, local-llm-servers-for-agents, llm-gateways, fully-local-private-agent, inference-clouds-for-agents
  sources: https://raw.githubusercontent.com/openai/openai-openapi/master/openapi.yaml https://developers.openai.com/api/docs/guides/function-calling https://github.com/openai/openai-python https://indexagentica.com/guides/run-an-agent-on-a-local-model/ https://indexagentica.com/compare/local-llm-servers-for-agents/
---

# Probe an OpenAI-compatible endpoint

Many local servers and inference clouds expose an HTTP API that looks like OpenAI's: a base URL ending in `/v1`, `GET /v1/models`, and `POST /v1/chat/completions`. This skill is how you check that a URL you already have actually speaks that dialect before you point an agent or an OpenAI SDK at it.

How to run a local server and wire an SDK is covered in https://indexagentica.com/guides/run-an-agent-on-a-local-model/. Ollama vs llama.cpp is https://indexagentica.com/compare/local-llm-servers-for-agents/. LLM *gateways* (OpenRouter, LiteLLM as a product, and similar) are https://indexagentica.com/compare/llm-gateways/. This skill does not compare vendors and does not start a server for you.

## Safety first

Do these in order. The bundled script enforces them; follow the same rules if you probe with `curl`.

1. **Default is loopback only.** Pass a `http://127.0.0.1:...` or `http://localhost:...` base URL. The script refuses any other host unless you add `--allow-remote`.
2. **Every address from one DNS lookup is classified.** The script calls `getaddrinfo` once for the URL you passed (and once more only for a redirect hop that leaves that scheme, host or port). IPv4-mapped IPv6 addresses such as `::ffff:10.0.0.1` are treated as their IPv4 equivalents. If *any* address is loopback, private, link-local, metadata (`169.254.169.254`, `fd00:ec2::254`), multicast, reserved or unspecified, the URL is refused unless the matching flag allows that class (loopback is the default; `--allow-private`, with `--allow-remote`, is for RFC1918, link-local and metadata). A mix of classes (for example one public address and one private address) is refused. `--allow-remote` alone is only for global unicast addresses.
3. **The TCP connection is pinned to an already-checked address.** The script connects to the first address from that lookup and does not resolve the hostname again at connect time. The HTTP `Host` header stays the original name; for HTTPS, SNI and certificate verification also use that name, not the IP. This closes a DNS-rebinding race between the check and the connect. It does not make every request safe: you still have to pass a URL you mean, and flags you mean, and a later redirect hop is looked up and classified from scratch.
4. **Keys come from the environment**, never from the command line and never from the URL. Default is `$OPENAI_API_KEY`. Use `--api-key-env NAME` to read a different variable (for example `GROQ_API_KEY`). The value is never printed in the report or in logs.
5. **`GET /v1/models` is the only default request.** It is read-only.
6. **Chat and tool probes are opt-in** (`--smoke-test`, `--check-tools`). Against a non-loopback URL they also require `--allow-paid`, because they can incur usage. The script sends at most one short chat request and one short tools request (`max_tokens` 8 and 64). The same `--allow-paid` rule is applied again if a redirect hop is no longer loopback.
7. **Redirects are followed manually, with a hop cap.** Each hop that changes scheme, host or port is resolved, classified and pinned again under the same flags. A redirect that leaves loopback, that fails classification (including a redirect to `169.254.169.254` or another private or metadata address), or that would turn a POST into a GET (`301`/`302`/`303`) is refused.
8. **Do not paste a key into chat.** If a probe fails with 401, ask the user to set the env var in their shell; do not have them send the secret to you.

The script does not crawl, does not create accounts, and does not purchase GPU time. It only connects to an address that already passed classification for the URL you passed, or for a redirect hop that was also classified.

## Probe

The script is standard-library Python 3 (`scripts/probe_openai_compatible.py`). From the unpacked skill folder:

```bash
# List models on a local server (default, no key required if the server doesn't need one)
python3 scripts/probe_openai_compatible.py --url http://127.0.0.1:8000/v1

# Optional loopback smoke test and tool-call check (still no --allow-paid needed)
python3 scripts/probe_openai_compatible.py --url http://127.0.0.1:8000/v1 --smoke-test --check-tools

# Hosted API: list models only. Replace the URL with the vendor's official base URL.
# Requires --allow-remote. Does not send a chat request.
OPENAI_API_KEY=... python3 scripts/probe_openai_compatible.py \
  --url https://api.example.com/v1 --allow-remote --api-key-env OPENAI_API_KEY

# Hosted API plus one tiny chat request and one tools request (may incur usage)
OPENAI_API_KEY=... python3 scripts/probe_openai_compatible.py \
  --url https://api.example.com/v1 --allow-remote --allow-paid \
  --smoke-test --check-tools --model MODEL_ID --api-key-env OPENAI_API_KEY
```

`--url` should be the OpenAI-compatible **base URL**, usually ending in `/v1` (or a vendor prefix plus `/v1`). The script joins `/models` and `/chat/completions` onto that base; if the base already ends with `/v1`, it does not double the prefix.

`--model` is optional. If you omit it, the first `id` from `GET /v1/models` is used for the optional chat and tools requests. If the list is empty, the fallback id is `probe-model` and the host may reject it.

The report is JSON on stdout. It includes the resolved base URL, whether an API key env var was set (not the value), the model ids, and, if you opted in, a short preview of the chat reply and whether `tool_calls` came back. A `200` on the tools request **without** `tool_calls` means the server accepted the payload, not that it supports tools. That is not proof of support.

A non-zero exit status means the models list failed, or an opted-in chat/tools request returned a non-200. The JSON is still printed so you can read the error (the error body is truncated and never includes your key).

## What the script is checking

These shapes are the common OpenAI-compatible subset, as documented in OpenAI's official OpenAPI document (https://raw.githubusercontent.com/openai/openai-openapi/master/openapi.yaml) and the function-calling guide (https://developers.openai.com/api/docs/guides/function-calling):

- `GET {base}/models` → a JSON object with a `data` array of `{ "id": "..." }`
- `POST {base}/chat/completions` with `model`, `messages`, and (for the tools check) `tools` plus `tool_choice`

The smoke test and tools check send `max_tokens` (8 and 64) because that field is what most local servers and OpenAI-compatible clouds accept today. Some hosts have switched newer models to `max_completion_tokens`; if a host rejects `max_tokens`, the report will show the error rather than invent a fallback.

Official vendor `base_url` values differ (plain `/v1`, `/openai/v1`, `/inference/v1`, an endpoint id in the path, and so on). Use the vendor's docs, not a guessed URL. Compatibility is **model-specific** even when the vendor documents tools or structured output in general.

## After a successful probe

1. Set the same `base_url` and env-var key in the client or SDK you actually run. The OpenAI Python library takes `base_url` and `api_key` (https://github.com/openai/openai-python).
2. Pin the model id you just saw, rather than relying on "first in the list."
3. If you need a local, private setup rather than a cloud API, see https://indexagentica.com/guides/run-an-agent-on-a-local-model/ and https://indexagentica.com/stacks/fully-local-private-agent/.

## What this skill does not do

- It does not start Ollama, vLLM, llama.cpp, LiteLLM or a cloud deployment.
- It does not compare inference clouds or gateways, and it does not rank quality or latency.
- It does not execute tool calls it receives; it only reports whether the model asked for one.
- It does not send prompts to any host except the `--url` you passed, and only after the flags above.

## What was tested (2026-11-16)

The script (v1.0.1) was run on this box against a local mock OpenAI-compatible server bound to `127.0.0.1` (not a vendor). The mock implemented `GET /v1/models`, a chat completion that replies `pong`, and a tools response that returns a `get_time` tool call. Extra cases used a second mock that issued a redirect, plus a test harness that monkeypatched `socket.getaddrinfo`.

- Default `--url http://127.0.0.1:<port>/v1` listed the mock model and exited 0.
- `--smoke-test --check-tools` on loopback returned `pong` and a `get_time` tool call, without `--allow-paid`.
- `http://1.1.1.1/v1` without `--allow-remote` was refused (no request was sent).
- `--smoke-test` against `http://1.1.1.1/v1` with `--allow-remote` but without `--allow-paid` was refused (no request was sent).
- A `http://192.168.0.1:9/v1` URL was refused even with `--allow-remote` (it needs `--allow-private` as well). No packet needed to be sent for the refusal.
- A fake key in `$OPENAI_API_KEY` did not appear in stdout or stderr.
- Credentials in the URL were refused.
- A hostname whose `getaddrinfo` result included both a public address and a private address was refused.
- A rebind simulation where the first `getaddrinfo` result was a public address and a later lookup would have returned a private address connected only to the pinned first address; `getaddrinfo` was not called again at connect time.
- A loopback mock that redirected to `http://169.254.169.254/` was refused (and a redirect to a private host was refused the same way).
- The IPv4-mapped address `::ffff:10.0.0.1` was refused.

The mocks were stopped afterwards. No real API keys were used and no paid remote requests were sent.
