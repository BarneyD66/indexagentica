---
id: agent-evals-and-observability
type: stack
title: "A recommended stack for agent evals and observability"
summary: "Instrument an agent with OpenTelemetry GenAI conventions and OpenInference, inspect traces and run experiments in Langfuse, and gate quality in CI with Langfuse's experiment action plus Promptfoo config-file evals."
description: "A recommended default for agent observability and evaluation: follow the OpenTelemetry GenAI semantic conventions, instrument with OpenInference (traces are standard OTLP and work with any OpenTelemetry backend), send them to Langfuse for datasets, judges and experiments, and add CI gates with langfuse/experiment-action and Promptfoo. Alternatives such as OpenLLMetry, Phoenix, Opik and Inspect stay in the notes. For the evaluation loop and a platform comparison, see the companion guide and comparison."
author: Agentica Author
use_case: "Trace an agent with portable OpenTelemetry instrumentation, review live and offline quality in a self-hostable platform, and fail CI when dataset experiments or file-based evals regress."
components:
  - role: Trace conventions
    entry: otel-genai-semconv
    why: "The OpenTelemetry GenAI semantic conventions (status: Development) define spans, metrics and events for inference, embeddings, tool execution, retrieval and agent operations, plus MCP and Agent2Agent. Adopt them so traces stay portable as backends change."
  - role: Instrumentation
    entry: openinference
    why: "Apache-2.0 conventions and instrumentation libraries, built on OpenTelemetry, for tracing LLM calls, agents, tools, retrieval and embeddings. Official docs say traces work with Arize Phoenix, Arize AX and any OpenTelemetry backend; span processors convert OpenLIT and OpenLLMetry traces into OpenInference form."
  - role: Observability and evals platform
    entry: langfuse
    why: "Open-source LLM observability you can use as Langfuse Cloud or self-host with Docker, Kubernetes or VMs (some add-on features require a license key). It receives OTLP at /api/public/otel, maps GenAI and OpenInference attributes, and adds datasets, LLM-as-a-judge, human annotation and experiments for online and offline evals."
  - role: Experiment CI gate
    entry: langfuse-experiment-action
    why: "MIT GitHub Action that loads your experiment script, runs it against a Langfuse dataset, comments the result on the pull request, and can fail the job when the script raises RegressionError. Official docs say to pin the action to a release; set langfuse_base_url for a self-hosted instance."
  - role: Config-file evals and red team
    entry: promptfoo
    why: "Open-source CLI and library for evaluating and red-teaming LLM apps with declarative test cases in a config file, automatic scoring, and local execution of evals (red-team generation may use hosted services). Use it alongside Langfuse when you want file-based evals that run on your machine or in CI."
  - role: Promptfoo CI action
    entry: promptfoo-action
    why: "MIT GitHub Action that runs Promptfoo when monitored files change. On pull requests it evaluates the current checkout, can post a comment with pass/fail counts, and can fail the job when the suite pass percentage is below the optional fail-on-threshold input."
tags: [evals, observability, tracing, opentelemetry, ci, llm-as-judge, red-teaming]
entries: [otel-genai-semconv, openinference, langfuse, langfuse-experiment-action, promptfoo, promptfoo-action, openllmetry, openlit, langfuse-mcp, langfuse-skills, inspect-ai, inspect-evals, arize-phoenix, opik, laminar, braintrust, tau2-bench]
related: [evaluate-an-ai-agent, agent-observability-platforms, llm-red-teaming-tools, research-agent, agent-benchmarks, newer-agent-eval-sets, test-an-agent-for-prompt-injection]
sources:
  - title: "OpenTelemetry GenAI Semantic Conventions, repository README"
    url: https://raw.githubusercontent.com/open-telemetry/semantic-conventions-genai/main/README.md
    accessed: 2026-11-22
  - title: "OpenTelemetry, Semantic conventions for generative AI systems"
    url: https://raw.githubusercontent.com/open-telemetry/semantic-conventions-genai/main/docs/gen-ai/README.md
    accessed: 2026-11-22
  - title: "OpenTelemetry, Semantic conventions for GenAI agent spans"
    url: https://raw.githubusercontent.com/open-telemetry/semantic-conventions-genai/main/docs/gen-ai/gen-ai-agent-spans.md
    accessed: 2026-11-22
  - title: "OpenTelemetry GenAI Semantic Conventions repository"
    url: https://github.com/open-telemetry/semantic-conventions-genai
    accessed: 2026-11-22
  - title: "OpenInference README"
    url: https://raw.githubusercontent.com/Arize-ai/openinference/main/README.md
    accessed: 2026-11-22
  - title: "OpenInference, official site (Markdown)"
    url: https://openinf.dev/index.html.md
    accessed: 2026-11-22
  - title: "OpenInference specification"
    url: https://openinf.dev/spec/index.html.md
    accessed: 2026-11-22
  - title: "Langfuse docs, Get started with tracing"
    url: https://langfuse.com/docs/observability/get-started
    accessed: 2026-11-22
  - title: "Langfuse docs, OpenTelemetry (OTEL) for LLM observability"
    url: https://langfuse.com/integrations/native/opentelemetry
    accessed: 2026-11-22
  - title: "Langfuse docs, Evaluation overview"
    url: https://langfuse.com/docs/evaluation/overview
    accessed: 2026-11-22
  - title: "Langfuse docs, Datasets"
    url: https://langfuse.com/docs/evaluation/experiments/datasets
    accessed: 2026-11-22
  - title: "Langfuse docs, Experiments in CI/CD"
    url: https://langfuse.com/docs/evaluation/experiments/experiments-ci-cd
    accessed: 2026-11-22
  - title: "Langfuse docs, MCP server"
    url: https://langfuse.com/docs/api-and-data-platform/features/mcp-server
    accessed: 2026-11-22
  - title: "Langfuse docs, Self-host Langfuse"
    url: https://langfuse.com/self-hosting
    accessed: 2026-11-22
  - title: "Langfuse LICENSE"
    url: https://raw.githubusercontent.com/langfuse/langfuse/main/LICENSE
    accessed: 2026-11-22
  - title: "langfuse/experiment-action README"
    url: https://raw.githubusercontent.com/langfuse/experiment-action/main/README.md
    accessed: 2026-11-22
  - title: "langfuse/experiment-action releases"
    url: https://github.com/langfuse/experiment-action/releases
    accessed: 2026-11-22
  - title: "Promptfoo docs, Intro"
    url: https://www.promptfoo.dev/docs/intro/
    accessed: 2026-11-22
  - title: "Promptfoo docs, Getting started"
    url: https://www.promptfoo.dev/docs/getting-started/
    accessed: 2026-11-22
  - title: "Promptfoo docs, Testing prompts with GitHub Actions"
    url: https://www.promptfoo.dev/docs/integrations/github-action/
    accessed: 2026-11-22
  - title: "promptfoo/promptfoo-action README"
    url: https://raw.githubusercontent.com/promptfoo/promptfoo-action/main/README.md
    accessed: 2026-11-22
  - title: "OpenLLMetry README"
    url: https://raw.githubusercontent.com/traceloop/openllmetry/main/README.md
    accessed: 2026-11-22
  - title: "Inspect AI README"
    url: https://raw.githubusercontent.com/UKGovernmentBEIS/inspect_ai/main/README.md
    accessed: 2026-11-22
  - title: "Inspect documentation"
    url: https://inspect.aisi.org.uk/
    accessed: 2026-11-22
last_verified: 2026-11-22
published: 2026-11-22
---

## Why this stack

The catalog already has a [hands-on evaluation loop](guide:evaluate-an-ai-agent) and a [comparison of observability platforms](comparison:agent-observability-platforms). This stack is the opinionated default those pages leave open: one portable instrumentation path, one self-hostable platform for traces and experiments, and two CI gates — one for Langfuse dataset experiments, one for file-based Promptfoo evals.

It is also distinct from the [research agent stack](stack:research-agent), which includes Langfuse as a single tracing component. Here observability and evaluation are the whole design.

## How the pieces fit

1. Instrument the agent so every model call, tool use, retrieval step and agent turn becomes an OpenTelemetry span, following the [GenAI semantic conventions](entry:otel-genai-semconv) and, in practice, [OpenInference](entry:openinference) libraries.
2. Export those spans over OTLP to [Langfuse](entry:langfuse). Review live traces, promote interesting examples into a dataset, attach LLM-as-a-judge, code or human scores, and run offline experiments before you ship.
3. In GitHub Actions, run the same Langfuse experiments with [langfuse/experiment-action](entry:langfuse-experiment-action) and fail the job when a score violates your threshold.
4. Keep a second, declarative eval suite in [Promptfoo](entry:promptfoo) (`promptfooconfig.yaml`) for local runs and for [promptfoo-action](entry:promptfoo-action) on pull requests. Use Promptfoo's red-teaming when you also need automated vulnerability scans; compare red-team tools in [Open-source red-teaming tools for LLM apps and agents](comparison:llm-red-teaming-tools).

You can swap the platform later because the traces are standard OTLP. You can also swap the CI gate if you only want one of the two eval styles.

## Instrument with OpenTelemetry

The [OpenTelemetry GenAI semantic conventions](https://raw.githubusercontent.com/open-telemetry/semantic-conventions-genai/main/docs/gen-ai/README.md) now live in their own repository, [open-telemetry/semantic-conventions-genai](https://github.com/open-telemetry/semantic-conventions-genai). As of this writing the documents are marked **Development**. They cover client inference and embeddings, tool execution, retrieval, remote agent invocations, model and agent spans, plus technology-specific notes (OpenAI, Anthropic, AWS Bedrock, Azure AI Inference) and conventions for MCP and the Agent2Agent protocol.

[OpenInference](entry:openinference) builds on OpenTelemetry with a span-kind taxonomy and attribute schema for LLM calls, agents, tools, retrievers and embeddings. Instrumentation packages exist for Python, JavaScript, Java and Go. The project's official site is [openinf.dev](https://openinf.dev/); the README states that traces are natively supported by Arize Phoenix and Arize AX, and that they work with any OpenTelemetry-compatible backend because they are standard OTLP traces.

If you already emit [OpenLLMetry](entry:openllmetry) or [OpenLIT](entry:openlit) spans, OpenInference documents span processors that convert those traces into OpenInference form. OpenLLMetry itself is a set of Apache-2.0 OpenTelemetry instrumentations maintained by Traceloop; it is a reasonable alternative or complement when you already standardized on that stack.

## Inspect and evaluate in Langfuse

[Langfuse](entry:langfuse) is open source. Official docs say you can use [Langfuse Cloud](https://langfuse.com/docs/observability/get-started) or [self-host](https://langfuse.com/self-hosting) it with Docker, Kubernetes or VMs, and that the instrumentation code is the same for both. Self-hosting runs the same infrastructure as Langfuse Cloud; some add-on features require a license key. The open-source portions of the repository are available under the MIT Expat license; content under documented `ee/` paths uses a separate license.

Langfuse receives traces on the `/api/public/otel` OTLP endpoint (HTTP/JSON or HTTP/protobuf; official docs say gRPC is not supported yet). For a self-hosted instance the same path applies; docs give `http://localhost:3000/api/public/otel` as the local example and note that the OpenTelemetry endpoint was introduced in Langfuse v3.22.0. Authentication is HTTP Basic. When you send spans directly via OpenTelemetry, Langfuse v4 docs also ask for an `x-langfuse-ingestion-version: 4` header so new data appears in real time on the v4 data model; without it, directly ingested OpenTelemetry data can be delayed by up to 10 minutes.

A minimal exporter configuration, using the official EU Cloud endpoint, looks like this (put the base64-encoded public and secret key pair in `AUTH_STRING`, and see the [OpenTelemetry page](https://langfuse.com/integrations/native/opentelemetry) for US, Japan, HIPAA and self-hosted URLs):

```bash
export OTEL_EXPORTER_OTLP_ENDPOINT="https://cloud.langfuse.com/api/public/otel"
export OTEL_EXPORTER_OTLP_HEADERS="Authorization=Basic ${AUTH_STRING},x-langfuse-ingestion-version=4"
```

Langfuse maps incoming GenAI, OpenInference and related attributes onto its data model. Official docs warn that if you want to filter or aggregate by identifiers such as `userId`, `sessionId`, metadata, version, release or tags, you should propagate those trace-level attributes to every span in the trace, not only the root.

For Python or JavaScript/TypeScript, Langfuse also documents its own SDK as the preferred way to set Langfuse-specific attributes, media and export. This stack still recommends OTLP plus OpenInference so a second backend (for example [Arize Phoenix](entry:arize-phoenix) or [Opik](entry:opik)) can receive the same traces. The [platform comparison](comparison:agent-observability-platforms) covers Langfuse, LangSmith, Phoenix, Braintrust, Opik and Laminar, including license and self-host notes.

Once traces are flowing, Langfuse evaluation runs both **online** (scoring live production traces) and **offline** (running your application against a pre-defined dataset). A [dataset](https://langfuse.com/docs/evaluation/experiments/datasets) is a collection of inputs and expected outputs; official docs highlight creating test cases from real production traces. You can combine LLM-as-a-judge, human annotation queues and custom scores via API or SDK, then compare experiments.

## Gate changes in CI

Langfuse's [experiments in CI/CD](https://langfuse.com/docs/evaluation/experiments/experiments-ci-cd) workflow is: create a dataset, write an experiment with the Python or JS/TS SDK, add evaluators, raise `RegressionError` when a score violates your threshold, and run the script with [langfuse/experiment-action](https://github.com/langfuse/experiment-action). Official docs say this works with Langfuse Cloud and self-hosted Langfuse.

The action loads the experiment script, runs it against a Langfuse dataset, comments the result on the pull request, and optionally fails the job when a regression is detected. `should_fail_on_regression` defaults to true. Pin the action to a release from the [experiment-action releases](https://github.com/langfuse/experiment-action/releases) (the official workflow example also recommends pinning to a release SHA). Store the Langfuse public and secret keys as GitHub secrets; set `langfuse_base_url` when you are not using the default `https://cloud.langfuse.com`.

Treat the CI gate as a release policy, not a scoreboard. Langfuse docs distinguish "every required case must pass" from "no approved passing case may regress," and they say missing cases, duplicate IDs, task failures, and missing or invalid evaluator results must fail the gate rather than count as passes.

## Config-file evals and red teaming

[Promptfoo](entry:promptfoo) is an open-source CLI and library for evaluating and red-teaming LLM apps. You describe prompts, providers and test cases in a config file (the getting-started example uses `promptfooconfig.yaml`), run `promptfoo eval`, and inspect results in a web viewer. Official intro notes that evals run on your machine and call the configured providers, while red-team generation may use hosted services.

[promptfoo-action](entry:promptfoo-action) runs that config in GitHub Actions when monitored files change. The action's README states that on pull requests it evaluates the current checkout (it does not run separate base and head evaluations), can post a comment with pass/fail counts, and accepts an optional `fail-on-threshold` (required suite pass percentage from 0 to 100). Official docs still show `promptfoo/promptfoo-action@v1`; pin a release or commit as you would any GitHub Action, and pass provider credentials through GitHub secrets — never commit them.

Use Promptfoo when you want evals as files in the repo, a local red-team loop, or a CI check that does not depend on a Langfuse dataset. Use Langfuse experiments when the cases should come from production traces and the scores should live next to those traces. Most teams will want both.

## Alternatives and going further

- **Other platforms.** If you prefer not to standardize on Langfuse, the same OpenInference or OpenLLMetry traces can go to any OTLP backend. Start with the [observability platform comparison](comparison:agent-observability-platforms) for [Opik](entry:opik), [Laminar](entry:laminar), [Arize Phoenix](entry:arize-phoenix) and [Braintrust](entry:braintrust).
- **Inspect.** [Inspect](entry:inspect-ai) is a framework for large language model evaluations from the UK AI Security Institute, with a companion library of evaluations in [Inspect Evals](entry:inspect-evals). Use it when you want a research-style eval harness rather than a production tracing platform.
- **Langfuse MCP and skills.** [Langfuse MCP](entry:langfuse-mcp) lets an assistant read and write Langfuse data over MCP. Official docs state that **both read and write tools are available by default**; if you only want read-only tools, configure your MCP client with an allowlist. If you can install CLI tools, Langfuse currently recommends the [Langfuse Agent Skill](entry:langfuse-skills) over the MCP server for that environment.
- **Published benchmarks.** Catalog entries such as [τ-bench 2.0](entry:tau2-bench), and the comparisons of [agent benchmarks](comparison:agent-benchmarks) and [newer agent eval sets](comparison:newer-agent-eval-sets), are useful for shared leaderboards. They are not a substitute for your own traces, datasets and CI gates.
- **Security tests.** Pair this stack with [Test an agent for prompt injection](guide:test-an-agent-for-prompt-injection) and the [red-teaming comparison](comparison:llm-red-teaming-tools) when the failure mode is an attack rather than a quality regression.

For a worked loop with official SDK snippets across more than one platform, follow [Evaluate an AI agent](guide:evaluate-an-ai-agent). Re-check those commands against current vendor docs: that guide was last verified on 2026-10-14, and the pages cited here were checked again on 2026-11-22.

## Caveats

- The OpenTelemetry GenAI conventions are still in Development. Langfuse maps a range of community attribute names because the conventions are evolving; do not assume every attribute is interpreted the same way in every backend.
- Langfuse's OTLP intake is HTTP only (JSON or protobuf), not gRPC. Confirm the `/api/public/otel` path and the v4 ingestion header on the version you actually run.
- Self-hosted Langfuse needs PostgreSQL, Redis/Valkey, ClickHouse and blob storage, as documented on the self-hosting page. Some add-on features need a license key. This article does not quote prices.
- Promptfoo evals are local, but official docs warn that red-team generation may call hosted services. Review Promptfoo's data-handling notes before you scan production prompts.
- GitHub Actions that call model providers will spend API budget. Keep keys in secrets, pin action versions, and start the gate on a small required dataset.
