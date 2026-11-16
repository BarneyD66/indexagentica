---
id: "inference-clouds-for-agents"
type: comparison
title: GPU clouds and serverless inference for agents
summary: "Compare GPU rental, serverless GPUs and hosted per-token APIs for agents: OpenAI-compatible base URLs, tools and structured output, BYO models, scale-to-zero and billing, APIs/CLIs, and host-trust notes. No cached dollar figures or invented benchmarks."
description: "A source-checked comparison of Groq, Together AI, Fireworks AI, DeepInfra, Baseten, Replicate, fal, Modal, Runpod, Vast.ai and Lambda Cloud as places an agent builder might run or call a model. Covers serverless per-token APIs versus dedicated or serverless GPUs versus raw GPU rental; official OpenAI-compatible base URLs where they exist; documented tool calling and structured output; bring-your-own-model or container paths; scale-to-zero and billing granularity (with links to live pricing pages, not copied dollar figures); programmatic APIs, CLIs and SDKs; and trust notes, including Vast.ai community hosts versus Secure Cloud and Runpod Community versus Secure Cloud. Distinct from LLM gateways, local model servers and sandbox comparisons. No unbacked latency or throughput numbers."
author: Agentica Author
tags: [inference, gpu, serverless, "openai-compatible", "tool-calling", "structured-output", billing]
entries: [groq, "together-ai", "fireworks-ai", deepinfra, baseten, replicate, "fal-ai", modal, runpod, "vast-ai", "lambda-cloud", vllm, litellm]
related: ["llm-gateways", "local-llm-servers-for-agents", "run-an-agent-on-a-local-model", "fully-local-private-agent", "structured-output-libraries", "code-sandboxes", "self-hosted-agent-sandboxes", "run-untrusted-code-in-a-sandbox", "probe-openai-compatible-endpoint"]
subjects: [groq, "together-ai", "fireworks-ai", deepinfra, baseten, replicate, "fal-ai", modal, runpod, "vast-ai", "lambda-cloud"]
criteria:
  - What you provision
  - "OpenAI-compatible API"
  - Tools and structured output
  - BYO model or container
  - "Scale-to-zero and billing"
  - Programmatic access
  - Trust and isolation
rows:
  groq:
    What you provision: "Hosted GroqCloud inference API (no GPU VMs to rent). Official docs: “Fast LLM inference, OpenAI-compatible.” Service tiers include on_demand (default), performance, flex and auto. The Batch API has its own window and does not take service_tier."
    OpenAI-compatible API: "Yes. Official base URL https://api.groq.com/openai/v1 with a Groq API key (GROQ_API_KEY). Official groq Python and TypeScript libraries exist. Compatibility page lists unsupported OpenAI fields, including logprobs and N other than 1."
    Tools and structured output: "Documented tool use (function calling) with a tools JSON schema and tool_calls. Structured Outputs page: constrain responses to a JSON schema, with strict and best-effort modes. Built-in tools (code execution, browser search) and remote MCP connectors are also documented."
    BYO model or container: "Hosted GroqCloud model catalog. No documented self-serve path to rent a raw GPU or bring an arbitrary inference container as this API. Use the official model list rather than assuming custom weights."
    Scale-to-zero and billing: "Hosted API: no workers for you to scale down. Usage is billed in the Groq console (Billing / spend-limits docs exist). No durable public price table on 16 Nov 2026: groq.com/pricing 308s to the homepage. Do not invent rates; check the console."
    Programmatic access: "HTTPS API plus official OpenAI-compatible client setup and official groq Python/TypeScript SDKs. This is a hosted inference API, not a VM-provisioning cloud, so there is no instance-rental CLI in the pages checked."
    Trust and isolation: "Requests run on GroqCloud with an API key. Built-in code execution and browser tools run on Groq’s side, not in your VPC. No community-host marketplace is documented for this API."
  together-ai:
    What you provision: "Serverless inference (per-token, no provisioning latency, 100+ open models), plus dedicated endpoints and dedicated containers, batch, and fine-tuning APIs. Optional US-only endpoint at us-api.together.ai."
    OpenAI-compatible API: "Yes. Official base_url https://api.together.ai/v1 (US: https://us-api.together.ai/v1). Together documents chat completions with tools and response_format, plus a Responses API and an Anthropic Messages API. Assistants/threads/runs are documented as not supported."
    Tools and structured output: "Documented function/tool calling (simple, parallel, multi-step and multi-turn patterns; support is model-listed). Structured outputs via response_format / JSON mode on supported chat models. Check the serverless and dedicated model lists for current support."
    BYO model or container: "Upload a fine-tuned model to a dedicated endpoint, or serve a custom model behind an OpenAI-compatible URL with dedicated containers (docs: Serve an OpenAI-compatible endpoint). Jig CLI builds and deploys containers."
    Scale-to-zero and billing: "Serverless is per-token with no provisioning step (see the pricing page). Dedicated endpoints have their own billing page. A US geo endpoint is documented to charge a 1.25× multiplier on standard serverless rates for listed token types."
    Programmatic access: "HTTPS API, official OpenAI-compatible client config, together Python client, and the Together CLI for jobs such as evaluations. Dedicated-container deploys use the documented container/Jig path."
    Trust and isolation: "Hosted platform with API-key auth. Dedicated endpoints and containers are the documented path when you need an isolated deployment rather than the shared serverless pool. See Together’s current security/terms for data handling."
  fireworks-ai:
    What you provision: "Serverless inference for open models, plus on-demand dedicated deployments, fine-tuning and a Fireworks API. Text-model docs cover serverless and dedicated via the same chat APIs. Training can be serverless or on dedicated GPUs."
    OpenAI-compatible API: "Yes. Official base_url https://api.fireworks.ai/inference/v1 with a Fireworks API key. Compatibility page covers chat and completions and notes a few field differences (for example max_tokens when the context would be exceeded). Anthropic- and NIM-compatible paths also exist."
    Tools and structured output: "Documented tool calling (OpenAI-compatible tool specs) and structured outputs (JSON schemas or custom grammars). The text-models guide lists both as first-class extensions of the chat API. Responses API is also documented."
    BYO model or container: "Query hosted serverless models, or create on-demand dedicated deployments (deployment-specific model ids). Fine-tune open models (serverless or dedicated training) and serve the result. Firectl manages account resources."
    Scale-to-zero and billing: "Serverless is pay-per-token (live table at fireworks.ai/pricing; also Standard/Priority/Spot styles in Fireworks docs). Dedicated GPUs are billed as deployments, not as a token table. See the pricing page rather than cached figures."
    Programmatic access: "HTTPS API, OpenAI/Anthropic-compatible SDKs, Fireworks Python SDK, and the Firectl CLI (firectl signin, whoami, and resource commands)."
    Trust and isolation: "Hosted inference with API-key auth. Dedicated/on-demand deployments are the documented path for reserved capacity. No community-host marketplace is documented for the inference API."
  deepinfra:
    What you provision: "Usage-based inference API for 100s of open models, plus private/custom LLM deployments on dedicated GPUs (autoscaling) and rentable GPU instances with SSH. Sandboxes are also documented."
    OpenAI-compatible API: "Yes. Official base_url https://api.deepinfra.com/v1/openai (Chat Completions at /chat/completions). A legacy completions API and an OpenAI-compatible Responses API are also documented. Auth: API key or scoped JWT."
    Tools and structured output: "Documented tool calling (OpenAI-compatible tools, tool_choice auto/none among the listed options) and structured outputs via response_format (json_object and JSON schema examples). Feature support still depends on the model."
    BYO model or container: "Custom LLMs: deploy your own LLM on dedicated A100/H100/H200/B200/B300 GPUs with autoscaling and an OpenAI-compatible endpoint. GPU instances (containers API) are for SSH/custom workloads."
    Scale-to-zero and billing: "Public models: per-token or execution-time pricing, pay for use (see deepinfra.com/pricing). Custom deploys are billed per GPU-hour; min_instances can be 0 (scale to zero). Live pricing page is authoritative."
    Programmatic access: "HTTPS API (deploy and OpenAI-compatible inference). Official examples use the OpenAI SDK with the DeepInfra base URL. Dashboard keys and optional key scopes / JWTs are documented."
    Trust and isolation: "Hosted API with key or scoped JWT auth. Private deployments and GPU instances are the documented path when you do not want a shared public-model pool. Sandboxes and instances can run customer workloads."
  baseten:
    What you provision: "Usage-based Model APIs (hosted language and decision models, no deploy step), plus dedicated GPU deployments, training (Loops), and sandboxes for agent code. Pay-as-you-go or reserved capacity (sales)."
    OpenAI-compatible API: "Yes for Model APIs: official OpenAI client base_url https://inference.baseten.co/v1 (Chat Completions and Responses). Anthropic Messages at https://inference.baseten.co (path /v1/messages). Dedicated deployments use https://model-MODEL_ID.api.baseten.co/environments/production/sync/v1."
    Tools and structured output: "Model APIs docs: the listed language models support tool calling (function-calling guide). All listed except Muse Spark Open support structured outputs. Confirm the current model table before relying on a specific model."
    BYO model or container: "Deploy an open-source model, private checkpoint, or custom model on dedicated GPUs with the Baseten CLI / examples. Model APIs cover only the hosted catalog."
    Scale-to-zero and billing: Model APIs are billed per tokens (see www.baseten.co/pricing/). Dedicated Inference is billed per GPU time on the same pricing page. An idle sandbox is documented to go on (see sandbox docs). Use the live pricing page; do not cache dollar figures.
    Programmatic access: "HTTPS Inference and Management APIs, official OpenAI/Anthropic SDK examples, Baseten CLI (documented for dedicated deploys), and further SDKs in the reference. API key required."
    Trust and isolation: "Hosted Model APIs run on Baseten-managed infrastructure. Dedicated deployments and sandboxes are the documented isolation paths. Sandboxes execute agent code on the platform."
  replicate:
    What you provision: "Hosted HTTP API to run and deploy machine-learning models (public catalog and your own). Official Python client, HTTP/OpenAPI API, MCP server and agent skills. Not a raw GPU VM product."
    OpenAI-compatible API: "No general OpenAI-compatible chat/completions base URL was found on 15–16 Nov 2026 (including a 404 on /docs/guides/openai-api). Use the official Replicate HTTP API and the replicate Python client with REPLICATE_API_TOKEN."
    Tools and structured output: "Not documented as an OpenAI tools or response_format surface (no drop-in chat/completions API found). Model-specific input/output schemas are on each model page and in the HTTP API. Do not assume OpenAI tool calling."
    BYO model or container: "Yes: deploy custom models packaged with Cog (official docs). Fine-tunes and private deployments are documented. You are not limited to the public catalog."
    Scale-to-zero and billing: "Pay only for what you use (replicate.com/pricing). Public models: billed for active processing; setup and idle are described as free (cold boots possible). Most private models/deployments also bill setup and idle time. Failed runs are not charged."
    Programmatic access: "Official HTTP API and OpenAPI schema, official Python package (replicate) and REPLICATE_API_TOKEN, plus documented MCP server and agent skills (packages not installed here)."
    Trust and isolation: "Hosted multi-tenant API with token auth. Public models share a hardware pool. Private models and deployments are the documented path for isolated runs. Running a model can spend credit; some models are tryable until billing is required."
  fal-ai:
    What you provision: "Model APIs (1,000+ hosted models, especially image, video, audio and multimodal), Serverless (deploy your own Python apps on fal GPUs; access may need approval), and Compute with dedicated GPUs and SSH. Workflows, a Sandbox and a fal Agent are also documented."
    OpenAI-compatible API: "No general OpenAI-compatible chat/completions base URL was found in official docs on 16 Nov 2026. Call Model APIs with the official fal clients and an API key. Do not treat fal as a drop-in OpenAI chat endpoint."
    Tools and structured output: Not documented as an OpenAI tools/response_format chat API. Model APIs use each model’s own input and output schema. Serverless apps define their own request/response models.
    BYO model or container: "Yes on Serverless: deploy your Python app or migrate a Cog image, Dockerfile, or existing Docker server (official migration guides). Compute offers dedicated GPUs with SSH. Model APIs are the hosted catalog."
    Scale-to-zero and billing: "Model APIs are usage-based (unit depends on the model). Serverless bills runner states per second; runners start on demand and shut down when idle (keep_alive and min-runner settings). See fal.ai/pricing and the Serverless pricing/scale docs."
    Programmatic access: "Official clients, HTTP Model APIs, and the fal CLI (docs: pip install fal). A key-based MCP server is documented. API key required (not created here)."
    Trust and isolation: Hosted Model APIs and managed Serverless runners. Compute SSH and the sandbox can execute customer or agent code. Serverless deploy access is documented as requiring fal’s approval on some accounts.
  modal:
    What you provision: "Serverless AI infrastructure: you write functions/apps that Modal runs for inference, training, batch jobs and sandboxes. Not a hosted model-catalog chat API. Official SDKs (Python, plus Go and JS/TS) and a CLI (modal setup)."
    OpenAI-compatible API: "Not a provider-hosted catalog endpoint. You can deploy your own OpenAI-compatible server; the official example “Run OpenAI-compatible LLM inference with Gemma and vLLM” shows a vLLM server on Modal. The resulting URL is yours, not a single global base URL."
    Tools and structured output: "Whatever the engine you deploy supports (the official vLLM example notes that LLMs expose chat, JSON and tools through an OpenAI-compatible API). Modal itself does not document a hosted tools/JSON catalog. Sandboxes are for running agent-generated code, not for model tool-calls."
    BYO model or container: "Yes: custom container images, open weights or your own models, official CUDA-enabled images. The vLLM example installs vLLM in a Modal image and downloads chosen weights."
    Scale-to-zero and billing: "Official docs: containers scale to zero when there are no inputs (idle), with configurable scaledown/warm-pool tradeoffs. Billing is usage-based; see modal.com/pricing. Cold-start behaviour is documented; do not treat example timings as your measurement."
    Programmatic access: "Official Python SDK and CLI (modal setup / python -m modal setup), plus Go and JavaScript/TypeScript SDKs (documented as beta in the current index). Apps and autoscaling are controlled in code and via the API."
    Trust and isolation: "Modal-hosted serverless containers and documented secure sandboxes for untrusted/agent code (separate from model serving). You still have to lock down what those sandboxes and functions can reach. See Modal’s sandbox networking docs and the sandbox comparisons, not repeated here."
  runpod:
    What you provision: "GPU Pods (Community Cloud and Secure Cloud), Serverless inference workers (including vLLM workers), and Clusters. Pods and custom workers run your containers. Prepaid credits; no account was created here."
    OpenAI-compatible API: "Yes for vLLM Serverless workers: official base_url https://api.runpod.ai/v2/ENDPOINT_ID/openai/v1 with a Runpod API key. Documented routes include /chat/completions. This is an endpoint you create, not a global shared model catalog URL."
    Tools and structured output: "Official OpenAI-compatibility page: function/tool calling depends on the model and vLLM support. Do not assume every endpoint exposes tools or JSON-schema constraints. Structured-output support is not spelled out on that page."
    BYO model or container: "Yes: custom containers on Pods (Docker Hub, GHCR, ECR, templates) and custom Serverless workers/handler images. vLLM workers serve a model you configure. Docker Compose on Pods is documented as unsupported."
    Scale-to-zero and billing: "Prepaid credits; compute and storage billed per second, no documented data-transfer fees. Serverless: scaled-down idle workers are not billed; the idle-timeout wait is billed. Image/model download while scaled down is documented as not billed. See runpod.io/pricing."
    Programmatic access: "REST APIs, official runpod Python SDK, and the rp CLI (login, deploy, manage Pods). Official MCP/docs MCP exist; the hosted MCP at mcp.runpod.io required auth when probed and is not used as a source here."
    Trust and isolation: "Secure Cloud: T3/T4 data centers for production-oriented workloads. Community Cloud: vetted peer-to-peer individual providers, typically cheaper. Pods execute your container. Pick Secure Cloud when you do not want a community host, similar in spirit to Vast’s host-trust split."
  vast-ai:
    What you provision: "GPU rental marketplace (on-demand, interruptible, reserved) plus Vast Serverless (vLLM endpoints and other workers recruited from the same marketplace). Prices are set by supply and demand, not a single Vast list. Official CLI, Python SDK and REST API."
    OpenAI-compatible API: "Yes for Serverless vLLM endpoints, via an official proxy: base_url https://openai.vast.ai/<ENDPOINT_NAME> with a Vast API key. The model field is required by the SDK but ignored; the served model comes from the endpoint’s MODEL_NAME. Raw GPU rentals have no global chat base URL."
    Tools and structured output: "Official proxy docs: tool/function calling is supported on models fine-tuned for it, but behaviour may differ from OpenAI; parallel_tool_calls is not supported. The proxy is text-in, text-out (no audio, images or embeddings endpoints)."
    BYO model or container: "Yes: rent an instance and run your image/template, or create a Serverless vLLM (or custom PyWorker) endpoint. CLI/API/SDK manage instance and endpoint lifecycle. You bring the model name in the endpoint configuration."
    Scale-to-zero and billing: "Prepaid credits. Instances: GPU billed per second while active; storage accrues for the life of the instance, including when stopped. Serverless is also per-second: Ready/Loading bill GPU; Inactive (cold) workers do not, though storage may still accrue. See vast.ai/pricing and Serverless pricing."
    Programmatic access: "Official CLI (pip install vastai or the documented install script — not executed here), Python SDK, and REST API at https://console.vast.ai/api/v0. Default API keys have full account access unless you create a scoped key."
    Trust and isolation: "Security FAQ: clients are isolated in unprivileged Docker containers, but provider security varies (Tier 4 datacenters vs individual hosts). For maximum security use Secure Cloud certified providers only (ISO 27001, Tier 3/4), encrypt data at rest, and do not store credentials on the instance."
  lambda-cloud:
    What you provision: "Public Cloud GPU VMs (On-Demand Cloud), 1-Click Clusters, and filesystems. You run the software stack yourself on Linux GPU instances. Reserved-capacity/Supercluster sales are listed on the pricing page. Not a hosted model API."
    OpenAI-compatible API: "No hosted OpenAI-compatible inference API was found in official Lambda Cloud docs (16 Nov 2026). The Cloud API manages accounts, keys, instances and related resources — it is not a /v1/chat/completions service. Install your own server on an instance if you need that API."
    Tools and structured output: "n/a as a hosted inference feature. Any tool calling or JSON-schema output would come from software you install on the VM (for example a local vLLM or llama.cpp server), not from a Lambda-hosted chat API."
    BYO model or container: "Yes: you control the instance. Run your container or stack (subject to Acceptable Use; docs prohibit cryptocurrency mining). This is closest to a traditional GPU VM."
    Scale-to-zero and billing: "No managed scale-to-zero inference tier is documented. On-Demand Cloud is billed in one-minute increments from health checks until termination, including idle running time (weekly invoices). 1-Click Clusters are billed per GPU-hour under the reservation. See lambda.com/pricing."
    Programmatic access: "Public Cloud API (docs.lambda.com/api/cloud) for instances and keys, plus the console (SSO is documented). API key required for the Cloud API (not created here)."
    Trust and isolation: "Instances run in Lambda’s Public Cloud data centers, not on a community-host marketplace. You are responsible for what you run on the VM and for not exposing unauthenticated inference ports. Refunds, when issued, are documented as service credits, not cash."
verdict: "Hosted OpenAI-compatible chat: Groq, Together AI, Fireworks AI, DeepInfra or Baseten Model APIs; confirm tools and structured output per model. Replicate and fal: native APIs, media, or pack-and-deploy—not a drop-in OpenAI chat URL. Modal: deploy your own server (documented scale-to-zero). Runpod or Vast.ai: GPUs or a vLLM endpoint (Vast: https://openai.vast.ai/<ENDPOINT_NAME>); read Community vs Secure Cloud notes. Lambda Cloud: a GPU VM you set up. Not a gateway, local-server, sandbox, price or benchmark comparison."
sources:
  - title: "Groq docs, OpenAI compatibility"
    url: https://console.groq.com/docs/openai
    accessed: 2026-11-16
  - title: "Groq docs, Tool use overview"
    url: https://console.groq.com/docs/tool-use/overview
    accessed: 2026-11-16
  - title: "Groq docs, Structured outputs"
    url: https://console.groq.com/docs/structured-outputs
    accessed: 2026-11-16
  - title: "Groq docs, Overview"
    url: https://console.groq.com/docs/overview
    accessed: 2026-11-16
  - title: "Together AI docs, OpenAI compatibility"
    url: https://docs.together.ai/docs/inference/openai-compatibility
    accessed: 2026-11-16
  - title: "Together AI docs, Serverless overview"
    url: https://docs.together.ai/docs/serverless/overview
    accessed: 2026-11-16
  - title: "Together AI docs, Function calling"
    url: https://docs.together.ai/docs/inference/function-calling/overview
    accessed: 2026-11-16
  - title: "Together AI docs, Structured outputs"
    url: https://docs.together.ai/docs/inference/chat/structured-outputs
    accessed: 2026-11-16
  - title: "Together AI docs, Dedicated containers OpenAI endpoint"
    url: https://docs.together.ai/docs/dedicated-containers-openai
    accessed: 2026-11-16
  - title: Together AI pricing
    url: https://www.together.ai/pricing
    accessed: 2026-11-16
  - title: "Fireworks docs, OpenAI compatibility"
    url: https://docs.fireworks.ai/tools-sdks/openai-compatibility
    accessed: 2026-11-16
  - title: "Fireworks docs, Querying text models"
    url: https://docs.fireworks.ai/guides/querying-text-models
    accessed: 2026-11-16
  - title: "Fireworks docs, Tool calling"
    url: https://docs.fireworks.ai/guides/function-calling
    accessed: 2026-11-16
  - title: "Fireworks docs, Structured outputs"
    url: https://docs.fireworks.ai/structured-responses/structured-response-formatting
    accessed: 2026-11-16
  - title: "Fireworks docs, Firectl"
    url: https://docs.fireworks.ai/tools-sdks/firectl/firectl
    accessed: 2026-11-16
  - title: Fireworks pricing
    url: https://fireworks.ai/pricing
    accessed: 2026-11-16
  - title: "DeepInfra docs, Chat completions"
    url: https://docs.deepinfra.com/chat/overview
    accessed: 2026-11-16
  - title: "DeepInfra docs, Tool calling"
    url: https://docs.deepinfra.com/chat/tool-calling
    accessed: 2026-11-16
  - title: "DeepInfra docs, Structured outputs"
    url: https://docs.deepinfra.com/chat/structured-outputs
    accessed: 2026-11-16
  - title: "DeepInfra docs, Custom LLMs"
    url: https://docs.deepinfra.com/private-models/custom-llms
    accessed: 2026-11-16
  - title: "DeepInfra docs, GPU instances"
    url: https://docs.deepinfra.com/gpu-instances/overview
    accessed: 2026-11-16
  - title: DeepInfra pricing
    url: https://deepinfra.com/pricing
    accessed: 2026-11-16
  - title: "Baseten docs, Overview"
    url: https://docs.baseten.co/overview
    accessed: 2026-11-16
  - title: "Baseten docs, Model APIs"
    url: https://docs.baseten.co/inference/model-apis/overview
    accessed: 2026-11-16
  - title: "Baseten docs, Quickstart"
    url: https://docs.baseten.co/quickstart
    accessed: 2026-11-16
  - title: "Baseten docs, Calling your model"
    url: https://docs.baseten.co/inference/calling-your-model
    accessed: 2026-11-16
  - title: Baseten pricing
    url: https://www.baseten.co/pricing/
    accessed: 2026-11-16
  - title: Replicate docs
    url: https://replicate.com/docs
    accessed: 2026-11-16
  - title: Replicate HTTP API
    url: https://replicate.com/docs/reference/http
    accessed: 2026-11-16
  - title: Replicate pricing
    url: https://replicate.com/pricing
    accessed: 2026-11-16
  - title: "fal docs, Documentation home"
    url: https://fal.ai/docs/documentation
    accessed: 2026-11-16
  - title: "fal docs, Serverless"
    url: https://fal.ai/docs/documentation/serverless
    accessed: 2026-11-16
  - title: "fal docs, Scaling parameters"
    url: https://fal.ai/docs/documentation/deployment/scale-your-application
    accessed: 2026-11-16
  - title: "fal docs, Serverless pricing"
    url: https://fal.ai/docs/documentation/serverless/pricing
    accessed: 2026-11-16
  - title: fal pricing
    url: https://fal.ai/pricing
    accessed: 2026-11-16
  - title: "Modal docs, Guide"
    url: https://modal.com/docs/guide
    accessed: 2026-11-16
  - title: "Modal docs, Scaling"
    url: https://modal.com/docs/guide/scale
    accessed: 2026-11-16
  - title: "Modal example, OpenAI-compatible vLLM"
    url: https://modal.com/docs/examples/vllm_inference
    accessed: 2026-11-16
  - title: Modal pricing
    url: https://modal.com/pricing
    accessed: 2026-11-16
  - title: "Runpod docs, OpenAI compatibility for vLLM"
    url: https://docs.runpod.io/serverless/vllm/openai-compatibility
    accessed: 2026-11-16
  - title: "Runpod docs, Serverless overview"
    url: https://docs.runpod.io/serverless/overview
    accessed: 2026-11-16
  - title: "Runpod docs, Serverless pricing"
    url: https://docs.runpod.io/serverless/pricing
    accessed: 2026-11-16
  - title: "Runpod docs, Pods overview"
    url: https://docs.runpod.io/pods/overview
    accessed: 2026-11-16
  - title: "Runpod docs, Billing"
    url: https://docs.runpod.io/accounts-billing/billing
    accessed: 2026-11-16
  - title: Runpod pricing
    url: https://www.runpod.io/pricing
    accessed: 2026-11-16
  - title: Vast.ai Security FAQ
    url: https://docs.vast.ai/guides/reference/faq/security.md
    accessed: 2026-11-16
  - title: Vast.ai billing
    url: https://docs.vast.ai/guides/reference/billing
    accessed: 2026-11-16
  - title: Vast.ai CLI hello world
    url: https://docs.vast.ai/cli/hello-world.md
    accessed: 2026-11-16
  - title: Vast.ai API reference introduction
    url: https://docs.vast.ai/api-reference/introduction.md
    accessed: 2026-11-16
  - title: "Vast.ai Serverless OpenAI-compatible interface"
    url: https://docs.vast.ai/guides/serverless/openai-compatible-api
    accessed: 2026-11-16
  - title: Vast.ai Serverless pricing
    url: https://docs.vast.ai/guides/serverless/pricing.md
    accessed: 2026-11-16
  - title: Vast.ai pricing
    url: https://vast.ai/pricing
    accessed: 2026-11-16
  - title: Lambda Cloud docs
    url: https://docs.lambda.com/
    accessed: 2026-11-16
  - title: Lambda Cloud billing
    url: https://docs.lambda.com/public-cloud/billing/
    accessed: 2026-11-16
  - title: Lambda Cloud API
    url: https://docs.lambda.com/api/cloud
    accessed: 2026-11-16
  - title: Lambda Cloud pricing
    url: https://lambda.com/pricing
    accessed: 2026-11-16
last_verified: 2026-11-16
published: 2026-11-16
---

## Who this is for

This page is for an agent builder choosing where a model runs: a hosted per-token API, a dedicated or serverless GPU that you start, or a raw rented GPU. It is not a comparison of LLM *gateways* (OpenRouter, Vercel AI Gateway, Cloudflare AI Gateway, Portkey, LiteLLM as a gateway product) — that is [LLM gateways compared](comparison:llm-gateways). It is not a comparison of Ollama and llama.cpp as *local* servers — that is [Ollama vs llama.cpp for agents](comparison:local-llm-servers-for-agents). How to point an OpenAI SDK at a loopback or self-hosted `/v1` URL is [Run an agent on a local model with an OpenAI-compatible endpoint](guide:run-an-agent-on-a-local-model). Sandboxes for *code* are covered in [Code sandboxes](comparison:code-sandboxes), [Self-hosted sandboxes](comparison:self-hosted-agent-sandboxes) and [Run untrusted code in a sandbox](guide:run-untrusted-code-in-a-sandbox); several vendors here also sell a sandbox, but this table is about inference, not that recipe.

The build renders the comparison table from the front matter. The notes below add only what the cells cannot: how the rows were grouped, which official URLs to open, and which host-trust disclosures to read before you put a key or a weight on someone else’s machine.

## Three ways to buy inference

Roughly, the eleven catalog entries fall into:

1. **Hosted, mostly OpenAI-compatible, per-token (or usage-based) APIs** — [Groq](entry:groq), [Together AI](entry:together-ai), [Fireworks AI](entry:fireworks-ai), [DeepInfra](entry:deepinfra) and [Baseten](entry:baseten) Model APIs. You set `base_url` and an API key. Together, Fireworks, DeepInfra and Baseten also sell dedicated GPUs or private deployments when you outgrow the shared pool.
2. **Native model APIs, or a platform you deploy onto** — [Replicate](entry:replicate) and [fal](entry:fal-ai) are official HTTP APIs (Replicate also has an official Python client, MCP server and agent skills; fal is especially strong on generative media) without a general OpenAI chat `base_url` found in their docs on 16 November 2026. [Modal](entry:modal) is a serverless platform: you bring the code (including an official [vLLM](entry:vllm) OpenAI-compatible example) and Modal scales the containers, including to zero.
3. **GPU rental, with an optional serverless vLLM path** — [Runpod](entry:runpod) (Pods and Serverless), [Vast.ai](entry:vast-ai) (marketplace instances and Serverless, plus an official OpenAI-compatible proxy), and [Lambda Cloud](entry:lambda-cloud) (on-demand VMs and 1-Click Clusters; no hosted OpenAI-compatible inference API was found).

[LiteLLM](entry:litellm) can sit in front of any of the OpenAI-compatible rows as a router; that is a client/gateway choice, compared in the gateways page, not a twelfth cloud.

## Official OpenAI-compatible base URLs

These are copied from official docs checked on 16 November 2026. Replace placeholders, and always send the vendor’s API key, not an OpenAI key.

- Groq: `https://api.groq.com/openai/v1`
- Together AI: `https://api.together.ai/v1` (US-only: `https://us-api.together.ai/v1`)
- Fireworks AI: `https://api.fireworks.ai/inference/v1`
- DeepInfra: `https://api.deepinfra.com/v1/openai`
- Baseten Model APIs: `https://inference.baseten.co/v1` (a dedicated deployment uses `https://model-MODEL_ID.api.baseten.co/environments/production/sync/v1`)
- Runpod vLLM Serverless: `https://api.runpod.ai/v2/ENDPOINT_ID/openai/v1`
- Vast.ai Serverless vLLM proxy: `https://openai.vast.ai/<ENDPOINT_NAME>` (the `model` field is ignored; the endpoint’s `MODEL_NAME` wins)
- Modal, Replicate, fal, Lambda Cloud: no single hosted catalog `base_url` in the official pages cited. Modal’s documented path is to deploy your own server. Replicate and fal document their own HTTP APIs. Lambda’s Cloud API provisions instances.

Tool calling and structured output are **model- and product-specific** even when the vendor has a “yes” in the table. Groq, Together, Fireworks, DeepInfra and Baseten Model APIs document OpenAI-style `tools` and (except where a model is listed as an exception) JSON-schema or JSON-mode output. Vast’s official proxy documents tool calling on models fine-tuned for it, and says `parallel_tool_calls` is not supported. Runpod’s vLLM page says function/tool calling depends on the model and vLLM. Engine-level grammar libraries are compared in [Structured-output libraries](comparison:structured-output-libraries), not here.

To probe an endpoint you already have — list models, optionally smoke-test a chat call, and check tools — use the [probe an OpenAI-compatible endpoint](skill:probe-openai-compatible-endpoint) skill. It is read-only by default and requires an explicit opt-in before it will call a paid remote API.

## Prices, scale-to-zero and what “serverless” means

Dollar figures go stale quickly. This page does **not** copy per-token or per-GPU rates. Open the vendor’s pricing page (linked in Sources) on the day you buy:

- [Groq](https://console.groq.com/docs/overview) — no durable public price table was available on 16 November 2026 (`https://groq.com/pricing` 308s to the homepage). Use the Groq console.
- [Together AI](https://www.together.ai/pricing), [Fireworks AI](https://fireworks.ai/pricing), [DeepInfra](https://deepinfra.com/pricing), [Baseten](https://www.baseten.co/pricing/), [Replicate](https://replicate.com/pricing), [fal](https://fal.ai/pricing), [Modal](https://modal.com/pricing), [Runpod](https://www.runpod.io/pricing), [Vast.ai](https://vast.ai/pricing), [Lambda Cloud](https://lambda.com/pricing).

What *is* stable enough to put in the table is billing *granularity* and scale-to-zero behaviour, as documented: Groq/Together/Fireworks/DeepInfra/Baseten Model APIs charge for API usage rather than a VM you left running; DeepInfra custom deploys can set `min_instances` to 0; fal Serverless and Modal containers are documented to shut down when idle; Runpod Serverless does not bill a worker that has scaled down, but *does* bill the idle-timeout window while a worker waits; Vast Serverless bills GPU for Ready/Loading workers and not for Inactive (cold) workers, while storage can still accrue; Lambda On-Demand Cloud bills by the minute including idle running time, with no managed scale-to-zero inference tier documented.

## Trust notes you should not skip

[Vast.ai](entry:vast-ai)’s official [Security FAQ](https://docs.vast.ai/guides/reference/faq/security.md) is explicit: clients are isolated in unprivileged Docker containers, but **provider security varies**. Tier 4 datacenters are not the same as an individual host. For maximum security the FAQ says to use **Secure Cloud** certified providers only (ISO 27001, Tier 3/4), encrypt sensitive data at rest, and not store credentials in instances. Vast Serverless recruits workers from the same marketplace, so that choice still matters.

[Runpod](entry:runpod) draws a similar line in its Pods overview: **Secure Cloud** in T3/T4 data centers, and **Community Cloud** as a vetted peer-to-peer network of individual providers. Treat Community Cloud as a different trust domain from Secure Cloud.

Lambda Cloud, Groq, Together, Fireworks, DeepInfra, Baseten, Replicate, fal and Modal are conventional hosted platforms rather than community-host marketplaces. That does not make them “private”: you are still sending prompts and, on several of them, *code* (sandboxes, SSH compute, or built-in code-execution tools) to a vendor. Put secrets in the vendor’s secret store or in your own env, not in a disk image you would be sad to see copied.

## What this page does not claim

No latency, throughput or quality numbers were measured. Vendor performance marketing is omitted. Together AI and Fireworks AI catalog entries were last verified for *pricing screenshots* on 9 November 2026; the API and product facts above were re-checked against official docs on 16 November 2026. Modal’s directory entry is thinner and older (last_verified 16 October 2026); the Modal cells rely on the official guide, scaling page and vLLM example checked today. No accounts, API keys or spend were created for this page.
