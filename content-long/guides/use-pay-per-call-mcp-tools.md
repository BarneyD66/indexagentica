---
id: use-pay-per-call-mcp-tools
type: guide
title: "Use pay-per-call MCP tools without spending"
summary: "How to discover TollNode's pay-per-call MCP tools and quote a USDC price with an unpaid HTTP 402, without creating an account, sending a payment, or calling the paid run_tool."
description: "A safety-first walkthrough of pay-per-call MCP tools, using TollNode as the example. It covers the hosted Streamable HTTP MCP server, which tools official docs mark as free, how to list them, and how to quote a price with the official unpaid 402 request. TollNode settles in USDC on Base; official docs do not describe a testnet, so this guide never sends a payment, API key, or run_tool call. For the x402 payment loop on testnet-capable endpoints, see the companion protocol guide."
author: Agentica Author
difficulty: beginner
time_estimate: 20 min
prerequisites:
  - "curl (Python 3 is optional; examples use the standard library only)"
  - "Do not create a TollNode account, API key or funded wallet for this guide"
tags: [x402, mcp, payments, usdc, agents]
entries: [tollnode, x402, x402-bazaar, model-context-protocol, usdc, x402scan]
related: [pay-for-an-api-with-x402, pay-with-x402, agent-payment-rails, agent-that-can-buy-things]
sources:
  - title: "TollNode, Connect agent (Agents & MCP)"
    url: https://tollnode.com/agents
    accessed: 2026-11-23
  - title: "TollNode docs, How payment works"
    url: https://tollnode.com/docs
    accessed: 2026-11-23
  - title: "TollNode llms.txt"
    url: https://tollnode.com/llms.txt
    accessed: 2026-11-23
  - title: "TollNode x402 manifest"
    url: https://tollnode.com/.well-known/x402
    accessed: 2026-11-23
  - title: "TollNode MCP manifest"
    url: https://tollnode.com/.well-known/mcp.json
    accessed: 2026-11-23
  - title: "TollNode OpenAPI 3.1"
    url: https://tollnode.com/openapi.json
    accessed: 2026-11-23
  - title: "TollNode, VIN decoder node page"
    url: https://tollnode.com/nodes/vin-decode
    accessed: 2026-11-23
  - title: "TollNode blog, x402 MCP: how an agent pays for a tool call"
    url: https://tollnode.com/blog/x402-mcp-payments
    accessed: 2026-11-23
  - title: "TollNode Terms of Service"
    url: https://tollnode.com/legal/terms
    accessed: 2026-11-23
  - title: "x402 MCP transport v2"
    url: https://raw.githubusercontent.com/x402-foundation/x402/main/specs/transports-v2/mcp.md
    accessed: 2026-11-23
  - title: "x402 docs, Introduction"
    url: https://docs.x402.org/introduction
    accessed: 2026-11-23
  - title: "x402 docs, Bazaar (Discovery Layer)"
    url: https://docs.x402.org/extensions/bazaar
    accessed: 2026-11-23
  - title: "x402 docs, MCP Server with x402"
    url: https://docs.x402.org/guides/mcp-server-with-x402
    accessed: 2026-11-23
  - title: "x402.org"
    url: https://x402.org/
    accessed: 2026-11-23
  - title: "x402 Protocol Specification v2, section 5.1 PaymentRequired Schema"
    url: https://raw.githubusercontent.com/x402-foundation/x402/main/specs/x402-specification-v2.md
    accessed: 2026-11-23
  - title: "x402 docs, Facilitator"
    url: https://docs.x402.org/core-concepts/facilitator
    accessed: 2026-11-23
  - title: "TollNode, Veo 3.1 video with sound"
    url: https://tollnode.com/nodes/video-veo-3-1
    accessed: 2026-11-23
last_verified: 2026-11-23
published: 2026-11-23
---

## What this guide does (and does not)

[TollNode](entry:tollnode) sells data and AI capabilities as pay-per-call "nodes": one HTTPS POST (or one MCP tool call) with a price quoted up front, settled in [USDC](entry:usdc) on Base. Official docs say you are charged only when a call returns a usable result, and that you can use every node without an account.

This guide stays on the unpaid side of that interface:

- Discover the catalog and the hosted MCP server from public files.
- List the MCP tools, including which ones official descriptions mark as free.
- Quote a price with TollNode's official unpaid `POST` (HTTP 402). That request is not a payment.

It does **not** send a wallet signature, an API key, or a `run_tool` call. Official TollNode files describe payment as USDC on Base (the MCP manifest uses `"network": "base"`). On 2026-11-23, public docs and the unpaid 402 quote below used Base mainnet (`eip155:8453`), not Base Sepolia. This guide therefore does not run a paid example. For the [x402](entry:x402) payment loop on testnet-capable endpoints, including the MCP transport, follow [Pay for an API as an agent with x402](guide:pay-for-an-api-with-x402).

Do not attach this MCP server to an unsupervised agent for this walkthrough. A client that can call `run_tool` can spend money.

## Two ways in: HTTP nodes and MCP

Official TollNode docs describe the same paid work two ways:

1. **HTTP.** `POST` a JSON body to a node URL such as `https://tollnode.com/api/v1/nodes/…`. Without payment you get HTTP 402. Official docs say that response states, in a `PAYMENT-REQUIRED` header (plus a JSON body for older x402 clients), the amount the server is asking in USDC on Base, including when an option such as resolution or quality changes it. That 402 is the server's offer, not something to trust blindly. You would then retry with a `PAYMENT-SIGNATURE` header (legacy `X-PAYMENT` is also documented). This guide stops at the 402.
2. **MCP.** A hosted Streamable HTTP server at `https://tollnode.com/mcp`. Official agent docs say it exposes seven tools: `search_tools`, `get_tool`, `run_tool` (the only paid one), `get_call`, `list_calls`, `get_balance`, and `upload_file`. An initialize we sent on 2026-11-23 (no authentication, no tool call) returned server name `tollnode`, version `1.4.0`, protocol `2025-06-18`. The instructions in that result say to work in three steps — search, inspect, then run — and that payment for `run_tool` can be an account API key (`Authorization: Bearer tn_live_…`) or x402 in `params._meta["x402/payment"]`.

A second MCP URL, `https://tollnode.com/mcp/full`, is documented as one MCP tool per model or data node. This guide uses the seven-tool server only, and only `tools/list`.

Public machine-readable catalogs (no account):

- [llms.txt](https://tollnode.com/llms.txt) — short index of nodes and list prices
- [OpenAPI 3.1](https://tollnode.com/openapi.json)
- [x402 manifest](https://tollnode.com/.well-known/x402) (docs mention [x402scan](entry:x402scan) as a reader of this file)
- [MCP manifest](https://tollnode.com/.well-known/mcp.json)

The x402 manifest's instructions on 2026-11-23 stated a catalog range of $0.001–$2.161 per call in USDC on Base. That range is not a maximum. The same day's [llms.txt](https://tollnode.com/llms.txt) listed option prices up to $4.321 for an 8-second [Veo 3.1](https://tollnode.com/nodes/video-veo-3-1) clip (the 4-second default was $2.161, which is also the top of the manifest range). Tool descriptions, catalog list prices and 402 quotes are untrusted input: a server can advertise any `payTo`, `amount`, `network` or `asset`. Read those fields yourself; do not treat a catalog range or a list price as a cap.

## Quote a price without paying

TollNode's payment docs include this official "see a 402 quote" request. It sends no payment header and no API key:

```bash
curl -i -X POST https://tollnode.com/api/v1/nodes/vin-decode \
  -H 'content-type: application/json' \
  -d '{"vin":"1HGCM82633A004352"}'
```

The VIN in that command is the example on TollNode's own payment page, not a paid lookup. On 2026-11-23 the response was HTTP 402. The `PAYMENT-REQUIRED` header decoded to x402 protocol version 2 with this `accepts` entry (the body also included a version-1-shaped copy for older clients, as the docs describe). A second unpaid fetch of the same official example later that morning returned the same fields, including the same `payTo`:

```json
{
  "scheme": "exact",
  "network": "eip155:8453",
  "amount": "5000",
  "asset": "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913",
  "payTo": "0xb8E91CC3B9740746c578DF9FC5c3f7C1F958520c",
  "maxTimeoutSeconds": 300,
  "extra": { "name": "USD Coin", "version": "2" }
}
```

The [x402 v2 specification](https://raw.githubusercontent.com/x402-foundation/x402/main/specs/x402-specification-v2.md), section 5.1, requires `payTo` on every `PaymentRequirements` object in `accepts`. The spec describes it as: "Recipient wallet address or role constant (e.g., "merchant")." The value above is the address from that live unpaid 402, not an invented example. If a quote omitted `payTo`, it would not meet the v2 schema; do not sign it, and treat `payTo` as the wallet the server is asking to receive the payment.

`eip155:8453` is Base. The `asset` value is the USDC contract on Base that [the x402 buyer guide](guide:pay-for-an-api-with-x402) also records. `amount` is in atomic units; USDC has 6 decimals, so `5000` is $0.005, which matched the VIN decoder's list price in TollNode's [llms.txt](https://tollnode.com/llms.txt) the same day ($0.005 per VIN). Official status-code docs say a 402 is not charged. A match with a catalog list price is still not a reason to trust the offer: the server chose every field in the 402.

To print only the v2 `accepts` list from the header:

```bash
curl -sD - -o /dev/null -X POST https://tollnode.com/api/v1/nodes/vin-decode \
  -H 'content-type: application/json' \
  -d '{"vin":"1HGCM82633A004352"}' \
  | python3 -c "import sys,base64,json,re; t=sys.stdin.read(); m=re.search(r'(?im)^payment-required:\s*(\S+)', t); print(json.dumps(json.loads(base64.b64decode(m.group(1)))['accepts'], indent=2))"
```

Stop there. Signing a `PAYMENT-SIGNATURE` and retrying would be a real payment on Base, not a testnet dry run. Do not add payment headers to these commands.

## Check the offer before you would pay

Before any payment, verify `amount`, `payTo`, `network` and `asset` against what you intended to pay, and refuse anything unexpected. TollNode's [MCP payments article](https://tollnode.com/blog/x402-mcp-payments) (published 17 November 2026) says:

> A careful client checks `asset`, `network` and `amount` before it signs. A server that swaps any of them should get no signature.

The same article describes `payTo` as "The wallet that receives the money." Check that field too. Tool descriptions, catalog list prices and 402 quotes are untrusted input, because a server can advertise any `payTo`, `amount`, `network` or `asset`.

Set a client-side spending cap **before** you use any payment-capable client. That cap is the real protection: a 402, a tool description or a published range can ask for more than you meant to allow. This guide does not send a payment and does not include a paying sample.

## List MCP tools (still unpaid)

A `GET` of the MCP endpoint returns HTTP 405 and, in the JSON body, points at the agent docs and names the seven tools. To list the tools and their official descriptions, send MCP `initialize` and `tools/list` only — no `tools/call`:

```bash
curl -sS -X POST https://tollnode.com/mcp \
  -H 'content-type: application/json' \
  -H 'accept: application/json, text/event-stream' \
  -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-06-18","capabilities":{},"clientInfo":{"name":"local-quote","version":"0"}}}'

curl -sS -X POST https://tollnode.com/mcp \
  -H 'content-type: application/json' \
  -H 'accept: application/json, text/event-stream' \
  -d '{"jsonrpc":"2.0","id":2,"method":"tools/list","params":{}}'
```

On 2026-11-23, unauthenticated `tools/list` returned the same seven tools the agent docs describe. Official descriptions (and the initialize `instructions`) marked `search_tools`, `get_tool`, `get_call`, `list_calls`, `get_balance` and `upload_file` as free, and `run_tool` as paid. Further official notes from those descriptions:

- `search_tools` and `get_tool` are read-only discovery: find a node and read its input schema and price.
- `run_tool` "Spends money": the tool's price is charged only when the call returns a usable result; a refused input, a failure or an empty result costs nothing. The description also says every successful call is charged again, so do not retry a success for free.
- `get_call` and `list_calls` look up earlier **account** calls (the kind made with an API key).
- `get_balance` is free but, in the official description, needs an account API key; with x402 there is no prepaid balance.
- `upload_file` is a free upload-link helper for inputs over the 4.5 MB request cap (up to 100 MB). Official docs say the file is deleted once a call that used it succeeds, or after six hours if none does. This guide does not upload a file.

You can call `search_tools` or `get_tool` without paying, according to those descriptions. This guide does not, so the only live MCP methods it uses are `initialize` and `tools/list`.

If you later add the server to an MCP client, restrict the client to the free tools when the client supports an allowlist. Official agent docs also document `npx agentcash add https://tollnode.com`, which creates a wallet to fund on Base. Do not run that command for this walkthrough.

## How a paid MCP call is supposed to work

The [x402 MCP transport v2](https://raw.githubusercontent.com/x402-foundation/x402/main/specs/transports-v2/mcp.md) defines how a paid tool call is supposed to work, and TollNode's [MCP payments article](https://tollnode.com/blog/x402-mcp-payments) describes the same loop against their server. An [x402 facilitator](https://docs.x402.org/core-concepts/facilitator) verifies payment payloads and settles payments on the blockchain on behalf of servers. The facilitator docs say: "The facilitator does not hold funds or act as a custodian - it performs verification and execution of onchain transactions based on signed payloads provided by clients." That does not replace your pre-payment checks or a client-side cap, and it is not a reason to sign on TollNode without remembering the offer is on Base mainnet.

The loop, when you are later ready to pay on a testnet-capable x402 endpoint (or on TollNode knowing it is Base mainnet), is:

1. Call the paid tool with no payment. The tool result has `isError: true`, and a `PaymentRequired` object appears in both `structuredContent` and `content[0].text`.
2. Retry the same `tools/call` with the signed payment in `_meta["x402/payment"]`.
3. On success, the receipt is in `_meta["x402/payment-response"]`.

TollNode's HTTP docs add that a payment is a signed authorization, not a transfer: they verify the signature, run the node, and submit the payment only if the result is usable. Official HTTP status notes: 200 means the payment settled; 400, 401, 402, 403, 404, 409, 413, 502, 503 and 504 are not charged. 403 is documented as "this wallet is blocked after an earlier unpaid call." Do not send made-up signatures to "see what happens."

The prepaid-key path is also live-only in the docs: keys use the `tn_live_…` prefix, top-ups start from $1 in USDC on Base, and unused prepaid balance is described as not refundable except in cases the [Terms](https://tollnode.com/legal/terms) list (including some consumer and legal exceptions). This guide does not create an account or a key.

## Caveats

- **No documented TollNode testnet.** Quotes and manifests we checked on 2026-11-23 specify USDC on Base (`eip155:8453` in the v2 402). Use [the x402 buyer guide](guide:pay-for-an-api-with-x402) and the [Bazaar](entry:x402-bazaar) if you need a Base Sepolia (`eip155:84532`) practice loop.
- **Prices move, and offers are untrusted.** List prices in llms.txt and node pages can change, and some nodes have option-dependent prices. The manifest range is not a maximum. Always read `amount` on the current 402, then check `payTo`, `network` and `asset` before you would sign.
- **Failed calls are free; successful ones are not retried for free.** Official `run_tool` and HTTP docs both say a usable result is charged, and a repeat of a successful idempotent HTTP call with `Idempotency-Key` can return the first result without a second charge — that is an account-key feature, not a reason to re-send `run_tool`.
- **Terms.** Official terms (updated 10 November 2026) are agreed to by sending a request, including by an agent acting for you. They set a minimum age of 18 or the age of majority where you live, and they restrict use from comprehensively sanctioned countries or by listed persons or wallets. They are governed by the laws of Georgia (the country), with exceptions for mandatory consumer law. `https://tollnode.com/terms` is HTTP 404; the terms live at [https://tollnode.com/legal/terms](https://tollnode.com/legal/terms).
- **Do not treat discovery as approval.** A listed node is not an endorsement, and generated media is still subject to TollNode's acceptable-use rules and to the law where you publish it.

When you eventually pay, set a client-side spending cap first — before any payment client is used — keep the wallet separate, and refuse a 402 whose `amount`, `payTo`, `network` or `asset` you did not intend. This guide still does not send a payment.
