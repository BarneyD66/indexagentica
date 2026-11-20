---
id: install-and-vet-a-vendor-skill-pack
type: guide
title: Install and vet a vendor skill pack
summary: "A source-backed checklist for installing an official vendor Agent Skills pack: use the documented command, pin the install when you can, read scripts and hooks as well as SKILL.md, prefer least-privilege credentials, and treat missing approval or sandbox docs as not documented."
description: "Walks through inspecting and installing an official vendor Agent Skills pack without treating silence as a safety default. Covers copying only documented install commands, pinning to a commit SHA or a vendor-published tag or ref when the installer supports it, reading SKILL.md plus scripts, hooks and other executables in a throwaway clone, preferring scoped or test credentials even when the pack has no approval contract, and wiring any bundled MCP server separately. Pinning, script review and least privilege reduce risk; they do not make a pack safe. Complements the official-vendor-skill-packs comparison; it does not rank vendors or run installers."
author: Agentica Author
difficulty: intermediate
time_estimate: "25 min"
prerequisites:
  - You have a coding agent that can load Agent Skills (a client that reads SKILL.md folders, such as Claude Code, Codex, Cursor or GitHub Copilot).
  - You can open the vendor’s official documentation or official repository in a browser. Do not paste API keys, tokens or account passwords into the chat.
tags: [agent-skills, install, safety, vendor, approvals]
entries: [agent-skills-spec, skills-cli, stripe-mcp, aws-mcp-servers]
related: [official-vendor-skill-packs, agent-skill-packs-and-installers, connect-an-agent-to-a-remote-mcp-server, connect-remote-mcp, add-mcp-servers-to-claude-code, pick-an-mcp-server, discover-agent-interfaces]
sources:
  - title: "Agent Skills specification"
    url: https://agentskills.io/specification
    accessed: 2026-11-17
  - title: "PlanetScale skills README"
    url: https://raw.githubusercontent.com/planetscale/skills/main/README.md
    accessed: 2026-11-17
  - title: "Stripe skills for agents"
    url: https://docs.stripe.com/skills
    accessed: 2026-11-17
  - title: "Stripe API keys"
    url: https://docs.stripe.com/keys
    accessed: 2026-11-17
  - title: "AWS Agent Toolkit README"
    url: https://raw.githubusercontent.com/aws/agent-toolkit-for-aws/main/README.md
    accessed: 2026-11-17
  - title: "Identity and access management for AWS MCP Server"
    url: https://docs.aws.amazon.com/agent-toolkit/latest/userguide/security-iam.html
    accessed: 2026-11-17
  - title: "IAM security best practices"
    url: https://docs.aws.amazon.com/IAM/latest/UserGuide/best-practices.html
    accessed: 2026-11-17
  - title: "Microsoft skills README"
    url: https://raw.githubusercontent.com/microsoft/skills/main/README.md
    accessed: 2026-11-17
  - title: "CrewAI skills README"
    url: https://raw.githubusercontent.com/crewAIInc/skills/main/README.md
    accessed: 2026-11-17
  - title: "skills CLI"
    url: https://github.com/vercel-labs/skills
    accessed: 2026-11-17
  - title: "skills CLI reference"
    url: https://raw.githubusercontent.com/vercel-labs/skills/main/docs/commands.md
    accessed: 2026-11-17
last_verified: 2026-11-17
published: 2026-11-17
---

## What this guide is for

Use this when you have picked an official vendor Agent Skills pack (a `SKILL.md` folder, plugin or CLI installer published by the product vendor) and you want to install it without guessing at safety defaults. The pack-by-pack facts live in [Official vendor Agent Skills packs compared](comparison:official-vendor-skill-packs). Harness search paths and the [skills CLI](entry:skills-cli) are in [Agent skill packs, skills CLIs and registries](comparison:agent-skill-packs-and-installers). This page is only the vetting checklist.

It does not install a pack for you, does not run vendor `curl | sh` scripts, and does not create accounts or spend money. Pinning an install, reading executables, and using least-privilege credentials reduce risk. They do not make a pack safe.

## 1. Use only the official install command

Open the vendor’s current docs or official repository README, not a random gist. Copy the command from that page. If the vendor documents more than one path (a plugin, `npx skills add …`, a product CLI), pick the one that matches the agent you actually run.

Examples of official paths, quoted from vendor docs checked on 17 November 2026 and not executed here:

- PlanetScale: clone the official repo and run `script/setup`, or `npx skills add planetscale/skills -g -y`
- Microsoft: `npx skills add microsoft/skills`
- Stripe: install the Stripe CLI as shown on [Skills for agents](https://docs.stripe.com/skills), then `stripe agent setup`; or `npx skills add https://docs.stripe.com`
- AWS: `/plugin install aws-core@claude-plugins-official`, `aws configure agent-toolkit`, or `npx skills add aws/agent-toolkit-for-aws/skills`

If the official page shows `curl … | sh` or a PowerShell `iex` installer (Stripe’s CLI docs do), read the script’s source URL first and only run it if you and the user intend to. If the vendor publishes a sha256 or another digest for that script, check the downloaded file against it before running it. Do not invent a digest when none is published. This guide does not run those scripts.

If your agent is not listed on the vendor’s page, do not invent a command. Either use the documented generic skills-CLI form, or stop and say the install path is not documented for that client.

Pin the install. A command that follows a floating branch such as `main` is not pinned: the files you get can change the next time you or the agent run it. Pin to a git commit SHA, or to a vendor-published tag or ref when the installer documents that.

The [skills CLI](entry:skills-cli) documents pinning a release tag or full commit with the `@` form, for example `npx skills add owner/repo@v1.2.3 --skill my-skill` (see the official [CLI reference](https://raw.githubusercontent.com/vercel-labs/skills/main/docs/commands.md)). For project installs, `skills-lock.json` records a content hash per skill: `skills list` and `skills check` flag installed files that differ from it, and a restore with `--frozen-lockfile` fails instead of installing content that does not match. That detects drift after install; it is not a substitute for passing a pin at add time if you want the source ref itself to be explicit.

CrewAI’s official README documents `/plugin marketplace add crewAIInc/skills#<branch-or-tag>` to pin the marketplace to a branch or tag. If you clone the official repository yourself, check out a specific commit SHA before you copy skill folders. If an installer has no documented pin or ref syntax, treat a floating `main` add as unpinned and prefer a SHA-checked clone.

## 2. Read the pack before you trust it

The [Agent Skills specification](entry:agent-skills-spec) is a folder with a `SKILL.md`. Progressive disclosure means the agent may load only the name and description at first, then the body and any `scripts/`, `references/` or `assets/` when the skill is used. Those extra files can contain commands, credential instructions and URLs.

A safe way to look, without installing into your real agent config:

1. Clone the official repository into a throwaway directory (for example under `/tmp`), or download the published `SKILL.md` from a vendor `.well-known` index if they have one (Stripe and Mastra publish indexes; [Discover a site's agent interfaces](skill:discover-agent-interfaces) is the general probe). Prefer a clone at the pinned commit or tag from section 1.
2. Read the root README, the license, and each `SKILL.md` you plan to enable. Also read any `scripts/` directory, install-time hooks, and other executable files (shell, Python, JavaScript, binaries) before you or the agent run them. Check for install-time side effects (ElevenLabs’ official README says the `onboarding` skill puts an API key in the project’s env file).
3. Only then run the official install command into the project or home skills directory your harness actually reads.

Microsoft’s official README warns that loading all skills causes context rot and that the repository is a work in progress. Prefer installing the skills you need. Reading the files reduces the chance you miss a hook or a credential write; it does not make the pack safe.

## 3. Look for approvals, then accept silence

Ask, from the official text only:

- Is the first run documented as read-only?
- Is there a class or gate for destructive or production changes?
- Is full autonomy opt-in, with an explicit acknowledgment?

[PlanetScale](entry:planetscale-skills) is the pack in the current vendor set that documents this clearly: Class A–E operations, a read-only first assessment, and opt-in autonomy that requires an explicit risk acknowledgment. If another vendor’s README does not say those things, write **not documented**. Do not infer a gate from the fact that the files are “just markdown,” and do not infer that missing text means the pack will ask first.

The same applies to test or sandbox modes. A vendor product may have a test account, and a README may mention a mock eval harness (Microsoft documents `pnpm harness <skill> --mock` for CI). That is not the same as “the installed pack defaults to a sandbox.” Do not invent a sandbox the docs do not describe.

## 4. Credentials, MCP and spend

Skills packs are often markdown. The *credentials* they tell an agent to use may still reach a live account:

- Environment variables (`ELEVENLABS_API_KEY`, `FIRECRAWL_API_KEY`) or a local CLI login (`pscale auth check`, AWS IAM credentials)
- A bundled MCP server: [Stripe MCP](entry:stripe-mcp), [AWS MCP](entry:aws-mcp-servers) and others. Live Stripe account data is documented to go through the official MCP/plugin path, not the markdown files alone. Wire MCP with [Connect an agent to a remote MCP server](guide:connect-an-agent-to-a-remote-mcp-server) or [Connect a remote MCP server](skill:connect-remote-mcp), and do not paste keys into chat.

Even when the pack has no approval contract, do not hand it full-access production secrets by default. Prefer least-privilege credentials the *product* actually documents:

- Stripe’s [API keys](https://docs.stripe.com/keys) guide describes restricted API keys (permissions you control, including read-only scopes) and says to build and test in a sandbox with that sandbox’s test keys (`sk_test_`, `rk_test_`) before switching to live keys. It does not recommend unrestricted secret keys for new use cases.
- AWS IAM [security best practices](https://docs.aws.amazon.com/IAM/latest/UserGuide/best-practices.html) say to apply least-privilege permissions: grant only the actions required to perform a task, on specific resources, under specific conditions. The Agent Toolkit’s [IAM guide](https://docs.aws.amazon.com/agent-toolkit/latest/userguide/security-iam.html) and official README describe the toolkit running under your existing IAM credentials, and condition keys (`aws:ViaAWSMCPService`, `aws:CalledViaAWSMCP`) so you can write policies that apply only to agents, including read-only limits.

Use the vendor’s documented secret path, keep keys out of the prompt, and start with those scoped, read-only, or test-mode credentials when the product docs describe them. If a vendor does not document a sandbox, test key or restricted role, write **not documented** and do not invent one. Least-privilege credentials reduce how much a compromised or overly broad skill can do; they do not make the pack safe.

If the official index or README describes a skill that can send funds, deploy, or change production data (Stripe’s published index includes `stripe-pay`; CrewAI documents `deploy-to-amp`), treat missing spend-approval language as a gap.

## 5. After it is installed

Confirm the skill folder landed in the path your harness documents (see the [installers comparison](comparison:agent-skill-packs-and-installers)). Ask the agent to name the installed skills and to summarize, from the local `SKILL.md`, whether a first action is read-only. Then try a low-risk task before anything that changes production data or spends money.

If a bundled MCP server was also installed, verify its endpoint and auth separately. [Pick an MCP server](skill:pick-an-mcp-server) is the shortlist-and-probe workflow for that, not this guide.
