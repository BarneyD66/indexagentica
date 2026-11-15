---
id: fully-local-private-agent
type: stack
title: "Fully local, private agent"
summary: "A local OpenAI-compatible model server, an optional LiteLLM router, Pi as the harness, Basic Memory for on-disk Markdown memory, and Anthropic's sandbox runtime — all on your machine, with no hosted model API and no cloud sandbox."
description: "Assemble a private coding agent from catalog entries that already run locally: Ollama (or another loopback OpenAI-compatible server), optional LiteLLM, Pi, Basic Memory's local install, and sandbox-runtime. Distinct from the coding-agent-starter stack, which uses Claude Code, hosted MCP and E2B. Start the model server with the companion guide; this page only wires the pieces and records licence and default-deny caveats."
author: Agentica Author
use_case: "Run a coding agent on your machine with a loopback model server, optional local router, local-first Markdown memory and an OS-level sandbox, without a hosted model API or a cloud sandbox."
components:
  - role: Local model server
    entry: ollama
    why: "MIT local app and server that binds 127.0.0.1:11434 by default and exposes http://localhost:11434/v1. Swap in vLLM, SGLang, LocalAI or llama.cpp; start any of them with the companion guide."
  - role: Optional router
    entry: litellm
    why: "MIT OpenAI-compatible proxy you can bind to 127.0.0.1:4000 and point at the local server. One client URL if you change backends. The proxy will not start in current releases without LITELLM_MASTER_KEY."
  - role: Harness
    entry: pi-coding-agent
    why: "MIT terminal agent that documents models.json endpoints for Ollama, vLLM, SGLang and other OpenAI-compatible servers, plus a first-party llama.cpp router path."
  - role: Memory
    entry: basic-memory
    why: "AGPL-3.0 local-first MCP memory stored as Markdown you keep on disk. Install with the documented local command; this stack does not use Basic Memory's hosted cloud path."
  - role: Sandbox
    entry: sandbox-runtime
    why: "Apache-2.0 OS-level sandbox (sandbox-exec, bubblewrap, or Windows srt-sandbox). Defaults deny network and writes until allowed; reads are allowed everywhere unless denied. Officially a beta research preview."
tags: [local-models, privacy, inference, memory, sandboxes, agents]
entries: [ollama, litellm, pi-coding-agent, basic-memory, sandbox-runtime, vllm, sglang, localai, llama-cpp]
related: [run-an-agent-on-a-local-model, local-llm-servers-for-agents, llm-gateways, give-an-agent-long-term-memory, run-untrusted-code-in-a-sandbox, self-hosted-agent-sandboxes, agent-memory-layers, coding-agent-memory-servers, coding-agent-starter, personal-agent-runtimes, coding-agent-harnesses]
sources:
  - title: "Ollama, OpenAI compatibility"
    url: https://docs.ollama.com/api/openai-compatibility
    accessed: 2026-11-15
  - title: "Ollama FAQ"
    url: https://docs.ollama.com/faq
    accessed: 2026-11-15
  - title: "Pi docs, Models"
    url: https://docs.pi.dev/latest/models
    accessed: 2026-11-15
  - title: "Pi docs, Local models with llama.cpp"
    url: https://docs.pi.dev/latest/llama-cpp
    accessed: 2026-11-15
  - title: "Pi docs, latest landing page"
    url: https://docs.pi.dev/latest
    accessed: 2026-11-15
  - title: "LiteLLM docs, OpenAI-compatible endpoints"
    url: https://docs.litellm.ai/docs/providers/openai_compatible
    accessed: 2026-11-15
  - title: "LiteLLM docs, Config settings"
    url: https://docs.litellm.ai/docs/proxy/config_settings
    accessed: 2026-11-15
  - title: "LiteLLM docs, Docker quick start"
    url: https://docs.litellm.ai/docs/proxy/docker_quick_start
    accessed: 2026-11-15
  - title: "Basic Memory README"
    url: https://raw.githubusercontent.com/basicmachines-co/basic-memory/main/README.md
    accessed: 2026-11-15
  - title: "Anthropic sandbox-runtime README"
    url: https://raw.githubusercontent.com/anthropics/sandbox-runtime/main/README.md
    accessed: 2026-11-15
  - title: "Anthropic sandbox-runtime LICENSE"
    url: https://raw.githubusercontent.com/anthropics/sandbox-runtime/main/LICENSE
    accessed: 2026-11-15
last_verified: 2026-11-15
published: 2026-11-15
---

## When to use this stack

Use this stack when the agent should stay on your machine: the model is served on loopback, memory is files you hold, and tool processes are sandboxed locally. It is the opposite of [Coding agent starter](stack:coding-agent-starter), which uses [Claude Code](entry:claude-code) as the harness, hosted MCP servers and [E2B](entry:e2b) as a cloud microVM.

This page does not teach you how to start vLLM, SGLang, Ollama or LocalAI, or how to place LiteLLM in front of them. That is [Run an agent on a local model with an OpenAI-compatible endpoint](guide:run-an-agent-on-a-local-model). Start there, then come back to wire the harness, memory and sandbox.

It is also not a substitute for [Ollama vs llama.cpp for agents](comparison:local-llm-servers-for-agents), [LLM gateways compared](comparison:llm-gateways), [Memory layers for AI agents](comparison:agent-memory-layers), [Self-hosted sandboxes for agents](comparison:self-hosted-agent-sandboxes) or [Give an agent long-term memory](guide:give-an-agent-long-term-memory). Those pages compare alternatives; this stack picks one local set and shows how they fit.

## The pieces

**Model server.** Start with [Ollama](entry:ollama) if you want the default loopback bind (`127.0.0.1:11434`, per the [FAQ](https://docs.ollama.com/faq)) and an OpenAI-compatible URL at `http://localhost:11434/v1`. If you already run [vLLM](entry:vllm), [SGLang](entry:sglang), [LocalAI](entry:localai) or [llama.cpp](entry:llama-cpp), keep that server; the companion guide shows the loopback flags. llama.cpp is a first-class option in [Pi](entry:pi-coding-agent) (see below) and is compared with Ollama on the serving-layer page, not repeated here.

**Optional router.** Put [LiteLLM](entry:litellm) on `127.0.0.1:4000` when you want one client base URL in front of whichever local server you started. Current LiteLLM releases will not start the proxy without `LITELLM_MASTER_KEY` (or `general_settings.master_key`). Official Docker examples already use `-p 127.0.0.1:4000:4000`. Skip the router if the harness can talk to the model server directly.

**Harness.** [Pi](entry:pi-coding-agent) is a MIT terminal agent whose [models](https://docs.pi.dev/latest/models) page covers local GGUF files through a llama.cpp router (`/llama`) and OpenAI-, Anthropic- or Google-compatible endpoints in `models.json`. It names Ollama, LM Studio, vLLM, SGLang and other compatible servers as the `models.json` path. Pi is also one of the subjects in [OpenClaw vs Hermes Agent vs Pi](comparison:personal-agent-runtimes). You can swap in another local-capable harness from [Terminal coding agents compared](comparison:coding-agent-harnesses) if you prefer; the rest of the stack does not depend on Pi-only APIs.

**Memory.** [Basic Memory](entry:basic-memory) is an AGPL-3.0 local-first MCP server that stores memory as Markdown in a knowledge base you own. The documented local install is:

```bash
uv tool install basic-memory --prerelease=allow
```

The project README also offers a hosted cloud path ("Skip the install — try Basic Memory in the cloud"). That path is out of scope for this stack. Stay on the local install, and see [Give an agent long-term memory](guide:give-an-agent-long-term-memory) and [Memory servers for coding agents](comparison:coding-agent-memory-servers) if you need to compare other memory layers.

**Sandbox.** [sandbox-runtime](entry:sandbox-runtime) (`srt`) is Apache-2.0 and officially a beta research preview: APIs and configuration may change. Install with the documented:

```bash
npm install -g @anthropic-ai/sandbox-runtime
```

It uses `sandbox-exec` on macOS, `bubblewrap` on Linux, and a Windows `srt-sandbox` user. The README's defaults: network is denied until you allow domains; writes are denied until you allow paths; reads are allowed everywhere unless you add a `denyRead` rule. For how this compares with other self-hosted sandboxes, and for the broader "treat output as untrusted" recipe, see [Self-hosted sandboxes for agents](comparison:self-hosted-agent-sandboxes) and [Run agent-generated code safely in a sandbox](guide:run-untrusted-code-in-a-sandbox).

## Wire it

1. Start the model server on loopback, following [the companion guide](guide:run-an-agent-on-a-local-model). Confirm you can complete a chat request with the OpenAI Python SDK against that `/v1` URL.
2. Optionally start LiteLLM on `127.0.0.1:4000` with `LITELLM_MASTER_KEY` set, pointing `api_base` at that same server. Clients then use `http://127.0.0.1:4000/v1` and the master key.
3. Point Pi at the endpoint. The official `models.json` example for Ollama (from the [models](https://docs.pi.dev/latest/models) page) is:

```json
{
  "$schema": "https://pi.dev/schemas/models.schema.json",
  "providers": {
    "ollama": {
      "baseUrl": "http://localhost:11434/v1",
      "api": "openai-completions",
      "apiKey": "ollama",
      "models": [
        { "id": "qwen2.5-coder:7b" }
      ]
    }
  }
}
```

The same page says the dummy key makes the model available to Pi and that Ollama ignores it. To go through LiteLLM instead, use the proxy's loopback `/v1` URL as `baseUrl` and the master key as `apiKey` (via `$LITELLM_MASTER_KEY` or `${LITELLM_MASTER_KEY}`, which Pi documents for environment interpolation). Swap the model `id` for one you have actually pulled; the `qwen2.5-coder:7b` value is Pi's example, not a model downloaded for this page. For GGUF files on disk, follow Pi's [llama.cpp](https://docs.pi.dev/latest/llama-cpp) path rather than this JSON snippet.

4. Add Basic Memory as a local MCP server in the harness, using the local install, not the cloud product.
5. Wrap the agent's command and tool processes with `srt` and a settings file that keeps network and writes on a default-deny list, then allow only the paths and hosts the agent should touch (for example the project directory, and `127.0.0.1` if the sandbox must reach the local model server).

## Licences and limits

- Ollama, LiteLLM's open-source SDK and proxy, Pi and llama.cpp are MIT. vLLM and SGLang are Apache-2.0. LocalAI is MIT. LiteLLM Enterprise is a separate, quote-based product and is not part of this stack.
- Basic Memory is AGPL-3.0. If you distribute a modified server, that licence's conditions apply. Its hosted cloud offering is a different deployment, not this stack.
- sandbox-runtime is Apache-2.0 and a beta research preview. Do not assume a stable config schema.
- A "fully local" setup is only as private as its bind addresses, logs and tool egress. Leave every HTTP server on `127.0.0.1`, and do not open sandbox network to the public internet "just in case".
