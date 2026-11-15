---
id: run-an-agent-on-a-local-model
type: guide
title: "Run an agent on a local model with an OpenAI-compatible endpoint"
summary: "Start Ollama, vLLM, SGLang or LocalAI bound to 127.0.0.1, point the OpenAI Python SDK at the server's /v1 base URL, enable tool calling, and optionally route the same endpoint through a LiteLLM proxy config."
description: "A practical how-to for running an agent against a local OpenAI-compatible server. It covers documented bind flags for Ollama, vLLM, SGLang and LocalAI, official OpenAI SDK base_url examples, tool-calling flags, and a LiteLLM config that talks to those servers. It is not a product comparison of Ollama and llama.cpp, and not a feature matrix of hosted LLM gateways. LiteLLM 1.109.1 was installed on this box and checked with --validate_config plus a loopback mock; vLLM, SGLang, Ollama and LocalAI were not installed or started."
author: Agentica Author
difficulty: intermediate
time_estimate: 45 min
prerequisites:
  - "Python 3.10 or newer (for the LiteLLM proxy extra; this box ran 1.109.1 on Python 3.13)"
  - "A local OpenAI-compatible server already installed, or a documented install to follow (Ollama, vLLM, SGLang or LocalAI). This guide does not install vLLM or SGLang, which typically need a GPU."
  - "No cloud account or paid API key is required for the loopback path"
tags: [inference, local-models, openai-compatible, tool-calling, litellm, agents]
entries: [ollama, vllm, sglang, localai, litellm, llama-cpp, pi-coding-agent]
related: [fully-local-private-agent, local-llm-servers-for-agents, llm-gateways, personal-agent-runtimes, coding-agent-harnesses]
sources:
  - title: "Ollama, OpenAI compatibility"
    url: https://docs.ollama.com/api/openai-compatibility
    accessed: 2026-11-15
  - title: "Ollama FAQ"
    url: https://docs.ollama.com/faq
    accessed: 2026-11-15
  - title: "Ollama, Tool calling"
    url: https://docs.ollama.com/capabilities/tool-calling
    accessed: 2026-11-15
  - title: "vLLM stable docs, Online serving"
    url: https://docs.vllm.ai/en/stable/serving/online_serving/
    accessed: 2026-11-15
  - title: "vLLM stable docs, Tool calling"
    url: https://docs.vllm.ai/en/stable/features/tool_calling/
    accessed: 2026-11-15
  - title: "vLLM stable docs, vllm serve"
    url: https://docs.vllm.ai/en/stable/cli/serve/
    accessed: 2026-11-15
  - title: "vLLM stable docs, Security"
    url: https://docs.vllm.ai/en/stable/usage/security/
    accessed: 2026-11-15
  - title: "vLLM PyPI project"
    url: https://pypi.org/project/vllm/
    accessed: 2026-11-15
  - title: "vLLM latest GitHub release"
    url: https://api.github.com/repos/vllm-project/vllm/releases/latest
    accessed: 2026-11-15
  - title: "SGLang docs, Quickstart"
    url: https://docs.sglang.io/docs/get-started/quickstart
    accessed: 2026-11-15
  - title: "SGLang docs, Examples"
    url: https://docs.sglang.io/docs/get-started/examples
    accessed: 2026-11-15
  - title: "SGLang docs, Server arguments"
    url: https://docs.sglang.io/docs/advanced_features/server_arguments
    accessed: 2026-11-15
  - title: "SGLang docs, OpenAI-compatible APIs"
    url: https://docs.sglang.io/docs/basic_usage/openai_api
    accessed: 2026-11-15
  - title: "SGLang PyPI project"
    url: https://pypi.org/project/sglang/
    accessed: 2026-11-15
  - title: "SGLang latest GitHub release"
    url: https://api.github.com/repos/sgl-project/sglang/releases/latest
    accessed: 2026-11-15
  - title: "LocalAI docs, Quickstart"
    url: https://localai.io/docs/start/quickstart/
    accessed: 2026-11-15
  - title: "LocalAI docs, CLI reference"
    url: https://localai.io/docs/reference/cli-reference/
    accessed: 2026-11-15
  - title: "LocalAI docs, OpenAI functions"
    url: https://localai.io/docs/api/openai-functions/
    accessed: 2026-11-15
  - title: "LocalAI latest GitHub release"
    url: https://api.github.com/repos/mudler/LocalAI/releases/latest
    accessed: 2026-11-15
  - title: "LiteLLM docs, OpenAI-compatible endpoints"
    url: https://docs.litellm.ai/docs/providers/openai_compatible
    accessed: 2026-11-15
  - title: "LiteLLM docs, CLI quick start"
    url: https://docs.litellm.ai/docs/proxy/quick_start
    accessed: 2026-11-15
  - title: "LiteLLM docs, Docker quick start"
    url: https://docs.litellm.ai/docs/proxy/docker_quick_start
    accessed: 2026-11-15
  - title: "LiteLLM docs, Config settings"
    url: https://docs.litellm.ai/docs/proxy/config_settings
    accessed: 2026-11-15
  - title: "LiteLLM docs, Security best practices"
    url: https://docs.litellm.ai/docs/proxy/security_best_practices
    accessed: 2026-11-15
  - title: "LiteLLM docs, Master key rotations"
    url: https://docs.litellm.ai/docs/proxy/master_key_rotations
    accessed: 2026-11-15
  - title: "LiteLLM docs, Ollama provider"
    url: https://docs.litellm.ai/docs/providers/ollama
    accessed: 2026-11-15
  - title: "LiteLLM docs, vLLM provider"
    url: https://docs.litellm.ai/docs/providers/vllm
    accessed: 2026-11-15
  - title: "LiteLLM PyPI project"
    url: https://pypi.org/project/litellm/
    accessed: 2026-11-15
  - title: "LiteLLM latest GitHub release"
    url: https://api.github.com/repos/BerriAI/litellm/releases/latest
    accessed: 2026-11-15
  - title: "Pi docs, Models"
    url: https://docs.pi.dev/latest/models
    accessed: 2026-11-15
last_verified: 2026-11-15
published: 2026-11-15
---

## What this guide is (and is not)

This is a how-to: start a local model server so it listens only on loopback, point an [OpenAI Python SDK](https://github.com/openai/openai-python) client at that server's OpenAI-compatible `/v1` URL, send a tool-calling request, and optionally put [LiteLLM](entry:litellm) in front as a local router.

It is not a feature-by-feature bake-off of local servers. For Ollama versus llama.cpp — tools, grammars, default ports and licences — see [Ollama vs llama.cpp for agents](comparison:local-llm-servers-for-agents). [llama.cpp](entry:llama-cpp) is not a fifth subject here; use that comparison if that is the server you want. It is also not a comparison of hosted LLM gateways. LiteLLM appears here only as a local proxy you run yourself. For OpenRouter, Vercel AI Gateway, Cloudflare AI Gateway, Portkey and LiteLLM as a *gateway product*, see [LLM gateways compared](comparison:llm-gateways).

To assemble a whole on-machine agent (this serving path plus local memory and a local sandbox), see [Fully local, private agent](stack:fully-local-private-agent).

Versions checked on 15 November 2026: [Ollama](entry:ollama) GitHub v0.40.16 (from the catalog entry and the 14 November comparison; not re-pulled as a server here); [vLLM](entry:vllm) PyPI **0.33.0**, while GitHub `/releases/latest` currently points at **v0.33.0rc3** with `prerelease` set to false (a `v0.33.0` tag also exists); [SGLang](entry:sglang) PyPI and GitHub **v0.5.23**; [LocalAI](entry:localai) GitHub **v4.12.1** (do not `pip install` the unrelated PyPI package named `localai`); [LiteLLM](entry:litellm) PyPI and GitHub **v1.109.1**, in sync. LiteLLM's SDK and open-source proxy are MIT; the repository's `enterprise/` tree is a separate licence and is not used here.

## Bind the server to loopback first

These servers speak HTTP. If the process listens on all interfaces, anything that can reach that port can usually call the model. This guide always sets an explicit loopback bind. Official examples do not always do that:

- [Ollama's FAQ](https://docs.ollama.com/faq) states that the server binds `127.0.0.1:11434` by default. Change it with `OLLAMA_HOST` (their examples use `0.0.0.0:11434` when the goal is to expose the server).
- [vLLM's `vllm serve` CLI](https://docs.vllm.ai/en/stable/cli/serve/) documents `--port` with default `8000`. `--host` is documented only as "Host name", with no default on that page, so pass `--host 127.0.0.1` explicitly. Official client examples use `http://localhost:8000/v1`.
- [SGLang server arguments](https://docs.sglang.io/docs/advanced_features/server_arguments) document `--host` default `127.0.0.1` and `--port` default `30000`. The [quickstart](https://docs.sglang.io/docs/get-started/quickstart) overrides this with `--host 0.0.0.0 --port 30000`. The [examples](https://docs.sglang.io/docs/get-started/examples) page shows both a Docker publish of `127.0.0.1:30000:30000` (the process inside the container still uses `--host 0.0.0.0`) and a native command with `--host 127.0.0.1 --port 30000`.
- [LocalAI's quickstart](https://localai.io/docs/start/quickstart/) states: "By default, LocalAI listens on port 8080 on all interfaces, and authentication is off." The [CLI reference](https://localai.io/docs/reference/cli-reference/) documents `--address` / `$LOCALAI_ADDRESS` with default `:8080`. Pass `--address 127.0.0.1:8080`. Official Docker examples use `-p 8080:8080`, which publishes the port on all host interfaces; use `-p 127.0.0.1:8080:8080` instead.

Do not run vendor `install.sh` scripts from this guide. Follow each project's documented install for your OS, then start the server with the flags below.

## Start an OpenAI-compatible server

Pick one. You only need a single `/v1` endpoint for the rest of the guide.

### Ollama

Once the Ollama app or daemon is installed, it already listens on loopback. The [OpenAI compatibility](https://docs.ollama.com/api/openai-compatibility) page gives the local base URL as `http://localhost:11434/v1`.

A generic OpenAI client looks like this (the dummy key is required by the SDK; Ollama does not treat it as a secret on the default local server):

```python
from openai import OpenAI

client = OpenAI(base_url="http://127.0.0.1:11434/v1", api_key="ollama")
```

Use a model name you have already pulled. This guide does not download a model.

### vLLM

Cite the [stable](https://docs.vllm.ai/en/stable/serving/online_serving/) docs, not `/en/latest/` (that tree is a developer preview). A loopback server, combining the official `vllm serve` form with the documented `--host` / `--port` flags:

```bash
vllm serve MODEL \
    --host 127.0.0.1 \
    --port 8000
```

Replace `MODEL` with a Hugging Face model id your install can load. The official tool-calling quickstart uses `meta-llama/Llama-3.1-8B-Instruct` and was not run here.

The [security](https://docs.vllm.ai/en/stable/usage/security/) page states that `--api-key` (or `VLLM_API_KEY`) authenticates only endpoints under the `/v1`, `/v2`, `/inference` and `/cohere` prefixes. Do not treat `--api-key` as protection for the whole process; bind to loopback first.

Official client (from the [tool-calling](https://docs.vllm.ai/en/stable/features/tool_calling/) page):

```python
from openai import OpenAI

client = OpenAI(base_url="http://localhost:8000/v1", api_key="dummy")
```

### SGLang

From the official [examples](https://docs.sglang.io/docs/get-started/examples) native path, which already uses loopback:

```bash
sglang serve MODEL_PATH --host 127.0.0.1 --port 30000
```

If you copy the [quickstart](https://docs.sglang.io/docs/get-started/quickstart) command, it passes `--host 0.0.0.0 --port 30000`. Change `--host` to `127.0.0.1` unless you intend to publish the port. Official Docker examples map `-p 30000:30000` or `-p 127.0.0.1:30000:30000` and still pass `--host 0.0.0.0` *inside* the container; the host-side `-p` is what decides whether the port is reachable off-machine.

Official client (same examples page):

```python
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:30000/v1",
    api_key="EMPTY",
)
```

The server is ready when it logs `The server is fired up and ready to roll!`.

### LocalAI

The documented command is `local-ai run`. Bind loopback with the official `--address` flag:

```bash
local-ai run --address 127.0.0.1:8080
```

The official quickstart also shows `local-ai run qwen3-4b`, which downloads that model on first run, and `docker run -p 8080:8080 --name local-ai -ti localai/localai:latest`. Prefer a host publish of `127.0.0.1:8080:8080` if you use Docker. The [OpenAI functions](https://localai.io/docs/api/openai-functions/) page uses `http://localhost:8080/v1/` as `base_url`.

Official client (from that page; `api_key="test"` is their example):

```python
from openai import OpenAI

client = OpenAI(
    api_key="test",
    base_url="http://localhost:8080/v1/"
)
```

## Point the OpenAI SDK at `base_url`

The pattern is the same for every server above: construct `OpenAI(base_url=..., api_key=...)` and call `chat.completions.create`. Use the host and port you actually bound. `localhost` and `127.0.0.1` are equivalent on a typical machine; this guide prefers `127.0.0.1` in commands we write, and leaves official snippets unchanged when quoting them.

A minimal completion, with the Ollama URL as the example:

```python
from openai import OpenAI

client = OpenAI(base_url="http://127.0.0.1:11434/v1", api_key="ollama")
response = client.chat.completions.create(
    model="MODEL",
    messages=[{"role": "user", "content": "Reply with the word pong."}],
)
print(response.choices[0].message.content)
```

Replace `MODEL` with a name the server already has. This snippet was not sent to a real local model on this box.

## Enable tool calling

Tool calling is a server *and* a model feature. The request shape is the OpenAI `tools` array. The server often needs an extra flag so it can parse the model's tool calls back into that schema.

**vLLM.** The [tool-calling](https://docs.vllm.ai/en/stable/features/tool_calling/) page marks `--enable-auto-tool-choice` as mandatory for auto tool choice, and `--tool-call-parser` as the parser to use (required with that flag). Their Llama 3.1 8B quickstart is:

```bash
vllm serve meta-llama/Llama-3.1-8B-Instruct \
    --enable-auto-tool-choice \
    --tool-call-parser llama3_json \
    --chat-template examples/tool_chat_template_llama3.1_json.jinja
```

Add `--host 127.0.0.1 --port 8000` as above. That page documents `tool_choice` values `auto`, `required` (as of `vllm>=0.8.3`) and `none`, plus named function calling. Their official Python example builds a `get_weather` tool, passes `tools=tools, tool_choice="auto"`, and reads `response.choices[0].message.tool_calls`.

**SGLang.** Official [examples](https://docs.sglang.io/docs/get-started/examples) pass `--tool-call-parser qwen3_coder` on the Qwen3.8-27B-FP8 serve command. That same page notes that its small local Qwen3-0.6B example does *not* configure tool calling, and points at the tool-calling guide for other models. The OpenAI client is still `base_url="http://localhost:30000/v1"` with `api_key="EMPTY"`.

**Ollama.** The [OpenAI compatibility](https://docs.ollama.com/api/openai-compatibility) page documents `tools` as supported on `/v1/chat/completions` and `tool_choice` as not supported on that route. Use the native tools API or omit `tool_choice` on `/v1`. See the [tool-calling](https://docs.ollama.com/capabilities/tool-calling) docs and the [Ollama vs llama.cpp](comparison:local-llm-servers-for-agents) comparison for the native versus OpenAI surface; this guide does not repeat that matrix.

**LocalAI.** The [OpenAI functions](https://localai.io/docs/api/openai-functions/) page shows the same `tools` / `tool_choice="auto"` shape against `http://localhost:8080/v1/`. Use a model you have installed that actually supports tools (their quickstart names `qwen3-4b` as a small CPU model that does).

An official-style request, abbreviated from the vLLM quickstart (not executed here):

```python
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get the current weather in a given location",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {"type": "string"},
                    "unit": {"type": "string", "enum": ["celsius", "fahrenheit"]},
                },
                "required": ["location", "unit"],
            },
        },
    },
]

response = client.chat.completions.create(
    model="MODEL",
    messages=[{"role": "user", "content": "What is the weather in San Francisco?"}],
    tools=tools,
    tool_choice="auto",  # omit on Ollama /v1/chat/completions
)
```

Then execute the returned `tool_calls` in your process and send the tool result back on a message with `role="tool"`, following the provider's example.

## Route through LiteLLM

Use [LiteLLM](entry:litellm) when you want one local OpenAI-compatible URL in front of whichever server you started, or when a client already speaks "OpenAI" and you would rather change a config file than the client. This is a router on `127.0.0.1`, not the hosted-gateway comparison.

Install the proxy extra (PyPI **1.109.1** on 15 November 2026, matching GitHub `v1.109.1`):

```bash
pip install 'litellm[proxy]'
```

The [OpenAI-compatible endpoints](https://docs.litellm.ai/docs/providers/openai_compatible) page says to prefix the model with `openai/`, set `api_base` to your server, and pass an `api_key` (the OpenAI provider path requires one; a dummy value is enough when the backend ignores it). If you see a `Not Found` error, that page says to give `api_base` a `/v1` postfix. A config that points at a loopback Ollama server:

```yaml
model_list:
  - model_name: local-model
    litellm_params:
      model: openai/MODEL
      api_base: http://127.0.0.1:11434/v1
      api_key: dummy
```

Change `api_base` (and the model id after `openai/`) for vLLM (`http://127.0.0.1:8000/v1`), SGLang (`http://127.0.0.1:30000/v1`) or LocalAI (`http://127.0.0.1:8080/v1`). LiteLLM also documents provider prefixes such as `ollama/` with `api_base: http://localhost:11434` and `hosted_vllm/`; those are alternatives, not a second required router.

Check the file without starting a server (LiteLLM 1.109.1 CLI: "Load and validate the config file ... then exit"):

```bash
litellm --config /path/to/config.yaml --validate_config
```

Start the proxy on loopback. The 1.109.1 CLI documents `--host` and `--port`. Official [CLI](https://docs.litellm.ai/docs/proxy/quick_start) logs say `Proxy running on http://0.0.0.0:4000` when you do not pass `--host`; pass it:

```bash
export LITELLM_MASTER_KEY="sk-$(openssl rand -hex 32)"
litellm --config /path/to/config.yaml --host 127.0.0.1 --port 4000
```

Keep that value out of the config file and out of source control. The [config settings](https://docs.litellm.ai/docs/proxy/config_settings) page states that the proxy will not start when the master key is unset, empty, or has a known unsafe value, and that `general_settings.master_key` falls back to `LITELLM_MASTER_KEY`. 1.109.1 on this box refused to boot without it, with the same message. The older wording on the [configs](https://docs.litellm.ai/docs/proxy/configs) page that still calls `master_key` optional lags that behaviour. There is a documented local-only escape hatch, `LITELLM_DANGEROUSLY_PERMIT_WEAK_OR_UNSET_MASTER_KEY`, which this guide does not recommend.

The official [Docker quick start](https://docs.litellm.ai/docs/proxy/docker_quick_start) already publishes loopback and expects a master key:

```bash
docker run \
  -v "$PWD/litellm_config.yaml:/app/config.yaml:ro" \
  -e LITELLM_MASTER_KEY \
  -p 127.0.0.1:4000:4000 \
  docker.litellm.ai/berriai/litellm:latest \
  --config /app/config.yaml
```

Call the proxy with the OpenAI SDK. Official snippets often use `http://0.0.0.0:4000`; use loopback and the master key:

```python
import os
from openai import OpenAI

client = OpenAI(
    base_url="http://127.0.0.1:4000/v1",
    api_key=os.environ["LITELLM_MASTER_KEY"],
)
response = client.chat.completions.create(
    model="local-model",
    messages=[{"role": "user", "content": "Reply with the word pong."}],
)
print(response.choices[0].message.content)
```

Do not use LiteLLM's `--test` flag as a "local" check. The official CLI help describes it as making a test request, and the docs route that path at a Hugging Face inference example (`gpt-3.5-turbo` / `bigcode/starcoder`). That leaves the machine. Use `--validate_config`, or a client request against a server you started on `127.0.0.1`.

See the official [security best practices](https://docs.litellm.ai/docs/proxy/security_best_practices) for storing the master key and provider credentials outside `config.yaml`.

## What was verified on this box

On 15 November 2026 this box installed `litellm[proxy]==1.109.1` (Python 3.13). `litellm --config ... --validate_config` exited 0 on a config whose `api_base` was `http://127.0.0.1:18080/v1`. Starting the proxy with `--host 127.0.0.1 --port 14000` and no `LITELLM_MASTER_KEY` failed with `UnsafeMasterKeyError`. With a locally generated `LITELLM_MASTER_KEY`, the same proxy listened only on `127.0.0.1:14000`. A loopback mock OpenAI server on `127.0.0.1:18080` answered `POST /v1/chat/completions`; both `curl` to `/chat/completions` and the OpenAI SDK (`base_url="http://127.0.0.1:14000/v1"`) returned the mock body `mock-ok`. Both processes were stopped afterwards. No vLLM, SGLang, Ollama or LocalAI server was installed or started, and no model weights were downloaded.

## Next step

Wire this endpoint into a local harness, memory store and sandbox with [Fully local, private agent](stack:fully-local-private-agent). [Pi](entry:pi-coding-agent) documents a `models.json` provider with `"baseUrl": "http://localhost:11434/v1"` and `"api": "openai-completions"` for Ollama, and the same compatible-endpoint path for vLLM, SGLang and other OpenAI-style servers.
