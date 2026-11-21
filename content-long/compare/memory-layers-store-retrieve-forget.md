---
id: memory-layers-store-retrieve-forget
type: comparison
title: How agent memory layers store, retrieve and forget
summary: "How MemMachine, Mem0, Memobase, Redis Agent Memory, Zep, Graphiti, Cognee, Letta and SurrealDB Agent Memory store, retrieve and forget: memory types, retrieval, deletion, and multi-user scoping."
description: "A primary-source comparison of nine agent memory layers, including MemMachine, on how official docs say each store is typed (episodic, profile/semantic, session/working), how retrieval works, how deletion or forgetting is exposed, and how memory is scoped across users, sessions or tenants. It does not repeat the earlier Memory layers for AI agents comparison (model, writes, license, hosted pricing, MCP presence, SDK languages, framework ties); cross-link that piece for those columns. Where a vendor is silent, the cell says not documented. No unofficial totals or benchmark scores."
author: Agentica Author
tags: [memory, agents, retrieval, deletion, scoping]
entries: ["memmachine", "mem0", "memobase", "redis-agent-memory", "zep", "graphiti", "cognee", "letta", "surrealdb-agent-memory", "mem0-mcp", "zep-context-mcp", "graphiti-mcp-server", "cognee-mcp", "letta-mcp"]
related: [agent-memory-layers, give-an-agent-long-term-memory, use-surrealdb-agent-memory, coding-agent-memory-servers, research-memory-libraries, vector-databases-for-agents, connect-an-agent-to-a-remote-mcp-server, agent-identity-and-mcp-auth]
subjects: ["memmachine", "mem0", "memobase", "redis-agent-memory", "zep", "graphiti", "cognee", "letta", "surrealdb-agent-memory"]
criteria:
  - Memory types
  - How retrieval works
  - Deletion and forgetting
  - Multi-user scoping
rows:
  memmachine:
    Memory types: "Official docs split semantic/profile memory (SQL, e.g. PostgreSQL with pgvector; tag/feature/value plus citations) from episodic memory: short-term raw episodes (one message each, plus summaries) and long-term reranked, deduplicated episode batches. Working/short-term sits on the episodic path."
    How retrieval works: "Profile retrieval is vector search that returns matching entries with conversation citations. Search Memories queries a project. Optional agent_mode adds orchestration on episodic long-term retrieval for multi-hop queries (a tool-select agent and specialized lookup agents), not a single vector hit."
    Deletion and forgetting: "REST: Delete Episodic Memory and Delete Semantic Memory. Official MCP delete_memory removes IDs from episodic or semantic stores (separate ID spaces; IDs come from search_memory). A search-time decay or TTL forget policy is not documented on these pages."
    Multi-user scoping: "ProjectContext isolates organization and project workspaces. MemoryContext optionally adds user_id, session_id, agent_id, and group_id for finer segmentation inside a project. How a missing identifier is defaulted is not further specified on the MemoryContext page."
  mem0:
    Memory types: "How-it-works: an LLM extracts facts from messages into vector, entity and history stores (messages are not stored as the memories). Platform also offers optional structured Profiles (a schema-defined, always-current user summary you read instead of searching) and Platform graph memory."
    How retrieval works: "search() ranks memories for a query. Platform supports filters and an optional managed reranker; advanced-retrieval docs cover keyword, reranking and hybrid. Official search docs say to always pass at least a user_id filter to avoid mixing users. OSS uses field filters in the same filters object."
    Deletion and forgetting: "delete(memory_id), batch_delete (docs: up to 1000 IDs), and delete_all by user_id, agent_id, run_id or metadata, on Platform and OSS. Platform Memory Expiration can stop a memory surfacing after a date without deleting it. Memory Decay is opt-in search-time scoring; it does not delete memories."
    Multi-user scoping: "Platform entity IDs: user_id, agent_id, app_id, run_id. Writes accept combinations, but default extraction attributes a fact to the speaker, so a record typically has user_id or agent_id, not both (unless Direct Import). Unmentioned IDs are not required to be null on read."
  memobase:
    Memory types: "Official positioning: a user-profile-based long-term memory backend. It maintains structured profile slots (real-time user profile) plus an event timeline (recent events, event gists, optional tags). It is not documented as a general working-memory session store."
    How retrieval works: "Get User Profile for the structured profile. Get User Personalized Context builds a memory prompt (size and filters documented). Events can be listed or searched semantically, by gists, or by tags. MCP tools: save_memory, search_memories, get_user_profiles."
    Deletion and forgetting: "REST APIs: Delete User, Delete User Event, Delete User Profile, and Delete Blob. A decay or TTL forget policy is not documented on these pages. The official MCP page does not document a delete tool."
    Multi-user scoping: "First-class per-user APIs (create, get, update, delete user; all profile and event calls are for a user). A project can list its users. A separate agent_id or org-wide shared graph is not documented on these pages."
  redis-agent-memory:
    Memory types: "Two official tiers: session memory (ordered conversation events, with optional summarization) and long-term memory. The overview maps session memory to working memory, long-term type episodic to a session snapshot, and type semantic to durable cross-session facts. Custom types are documented."
    How retrieval works: "Retrieve a session’s events by session ID. Search long-term memory semantically and narrow with filters (owner, session, namespace, topic, or memory type). Multi-session recall is documented. Interfaces: redis-iris SDK (memory.recall), REST POST /memories/search, iris CLI, and an MCP server."
    Deletion and forgetting: "Delete long-term memories by ID (SDK delete; REST .../memories/bulk-delete). The official quickstart also shows cleaning up every session and memory a user owns. Session events expire after a configurable short-term TTL and then leave session retrieval. Long-term memory has a separate TTL."
    Multi-user scoping: "ownerId on long-term memories (who the memory belongs to, independent of the event’s actorId). Sessions use session IDs plus actors. Optional namespaces group conversations and memories, including a shared namespace for several users. Filters can constrain search by owner, session, or namespace."
  zep:
    Memory types: "A temporal Context Graph plus a Context Block. Official context types: facts, entities, episodes, thread summaries, observations, and the user summary. Facts are relationships with bi-temporal valid_at/invalid_at timestamps. Episodes are raw ingested artifacts; threads group conversation messages."
    How retrieval works: "Retrieve a prompt-ready Context Block from a user’s graph, query the graph for records, use context templates, or assemble context yourself (graph search). Official retrieve docs cover preloaded context versus tool-retrieved context."
    Deletion and forgetting: "Explicit delete APIs for an edge, node, episode, thread, user, or Context Graph (UUID; async task). Deleting an edge does not delete its nodes. Facts can also be invalidated in time via invalid_at. Retention docs cover default retention, what deletion removes, and policies that delete idle context."
    Multi-user scoping: "Users, threads, user graphs, and shared/account Context Graphs are first-class. Official guidance is to ingest into the correct graph (user vs account) and retrieve from authorized scopes. Governance (RBAC/ABAC) is documented separately."
  graphiti:
    Memory types: "Zep’s open-source temporal knowledge graph (Context Graph): episodic nodes plus entities, facts/edges, communities and sagas. Official overview: incremental episode updates, a bi-temporal model, and temporal edge invalidation. It is the framework Zep uses, not the hosted Context Lake."
    How retrieval works: "Hybrid search fuses semantic similarity, BM25 full-text, and graph methods. graphiti.search combines semantic and BM25 and reranks with Reciprocal Rank Fusion; an optional focal_node_uuid reranks by graph distance to a node. Overview: no LLM-in-the-loop reranking in that hybrid path."
    Deletion and forgetting: "Contradiction handling is temporal edge invalidation (facts expire in time rather than only being overwritten). CRUD also documents hard deletes: delete, delete_by_uuids, or delete_by_group_id on nodes and edges. A hosted retention-policy product is not documented on the Graphiti pages cited here."
    Multi-user scoping: "Nodes and edges carry a group_id (examples use identifiers such as customer-123). get_by_group_ids and delete_by_group_id operate on that field. A separate user/thread/account model like Zep’s hosted product is not documented on these Graphiti pages."
  cognee:
    Memory types: "Official session guide: short-term session memory per session_id, plus a long-term knowledge graph that persists across sessions (session content can be promoted into the graph). MCP overview: remember, recall and forget. A named profile-memory product is not documented on these pages."
    How retrieval works: "recall() with documented SearchType options (including GRAPH_COMPLETION and other completion/retriever modes in the guides). MCP recall tool. Guides also cover RAG and hybrid retrieval, a temporal knowledge graph (SearchType.TEMPORAL), and an importance_weight on remember() that affects ranking."
    Deletion and forgetting: "Official MCP tools include forget. The sessions guide shows cognee.forget(everything=True) as a clean start. Further forget filters or a decay/TTL policy are not spelled out on the pages cited here — treat extra behavior as not documented."
    Multi-user scoping: "session_id isolates conversational short-term memory; the knowledge graph is shared across sessions. recall() can use a default user when none is passed. MCP: standalone for one user; API mode shares one graph, and each instance’s writes belong to one Cognee user per token."
  letta:
    Memory types: "Agent-owned memory, not a user-profile store. Creation can set persona/human or labeled Markdown files (system/ files are in the prompt every turn; others are on-demand). MemFS is a git-versioned memory filesystem the agent edits. Dreaming is a background subagent that updates memory."
    How retrieval works: "system/ memory is in context every turn; the agent reads other MemFS files from the file tree. Official MemFS docs: a search mod for keyword search; semantic and hybrid modes need QMD over $MEMORY_DIR. Conversation-history search is separate (Cloud: full-text, vector, hybrid; local: full-text only)."
    Deletion and forgetting: "The agent edits and commits memory files; every edit is a git commit (history and conflict resolution are documented). A dedicated forget or delete-memory API, and a decay/TTL policy, are not documented on the memory, MemFS, or dreaming pages cited here."
    Multi-user scoping: "Memory is per agent and persists across that agent’s conversations. Cloud shared-memory repositories attach the same Git-backed files to multiple agents. A first-class end-user tenant id (user_id) for memory rows is not documented on these pages."
  surrealdb-agent-memory:
    Memory types: "Official lifecycle and product docs: durable facts (entities, attributes, instructions) with provenance, plus a full episodic transcript that stays addressable via sessions. Facts have categories such as context, knowledge and identity. License and pricing stay in the earlier comparison."
    How retrieval works: "The product page documents hybrid retrieval that fuses seven signals: vector, lexical, graph, section links, PageRank, geographic and trace history. Point-in-time reads are part of the tri-temporal/supersession model (you can ask what was true last month). A built-in MCP server is documented."
    Deletion and forgetting: "Three mechanisms: supersession (close the old belief in time, keep history); decay (official daily rates: context 0.95, knowledge 0.995, identity 1; never ends a fact); and forget (POST /forget or entity delete expires current retrieval; purge: true erases). Context facts expire in 7 days."
    Multi-user scoping: "Official product text: scope-bound multi-tenancy enforced by Agent Memory. Decay rates and the 7-day context expiry are the same for every Context, scope and principal, including Enterprise — not configurable per Context or scope. Grants such as memory:forget are documented on the lifecycle page."
verdict: "For documented forget that is separate from decay and supersession, start with SurrealDB Agent Memory. MemMachine is the layered episodic-plus-profile pack with separate delete APIs and optional agentic retrieval. Memobase is a per-user profile and event timeline. Redis Agent Memory maps working, episodic and semantic tiers, with TTLs and ID deletes. Zep and Graphiti share temporal graphs with invalidation and explicit deletes; Zep also has user/thread/account graphs and retention policy. Treat missing delete, decay or tenant language as not documented."
sources:
  - title: "MemMachine: Memory Types"
    url: https://docs.memmachine.ai/open_source/memory_types
    accessed: 2026-11-21
  - title: "MemMachine: Retrieval Agent Architecture"
    url: https://docs.memmachine.ai/open_source/retrieval_agent_architecture
    accessed: 2026-11-21
  - title: "MemMachine MCP tools"
    url: https://docs.memmachine.ai/api_reference/mcp
    accessed: 2026-11-21
  - title: "MemMachine MemoryContext"
    url: https://docs.memmachine.ai/api_reference/ts-rest/interfaces/MemoryContext
    accessed: 2026-11-21
  - title: "MemMachine Search Memories"
    url: https://docs.memmachine.ai/api-reference/memories/search-memories
    accessed: 2026-11-21
  - title: "MemMachine Delete Episodic Memory"
    url: https://docs.memmachine.ai/api-reference/memories/delete-episodic-memory
    accessed: 2026-11-21
  - title: "MemMachine Delete Semantic Memory"
    url: https://docs.memmachine.ai/api-reference/memories/delete-semantic-memory
    accessed: 2026-11-21
  - title: "Mem0: How Mem0 Works"
    url: https://docs.mem0.ai/core-concepts/how-it-works
    accessed: 2026-11-21
  - title: "Mem0: Memory Operations - Search"
    url: https://docs.mem0.ai/core-concepts/memory-operations/search
    accessed: 2026-11-21
  - title: "Mem0: Memory Operations - Delete"
    url: https://docs.mem0.ai/core-concepts/memory-operations/delete
    accessed: 2026-11-21
  - title: "Mem0: Entity-Scoped Memory"
    url: https://docs.mem0.ai/platform/features/entity-scoped-memory
    accessed: 2026-11-21
  - title: "Mem0: Profiles"
    url: https://docs.mem0.ai/platform/features/user-profiles
    accessed: 2026-11-21
  - title: "Mem0: Memory Decay"
    url: https://docs.mem0.ai/platform/features/memory-decay
    accessed: 2026-11-21
  - title: "Mem0: Memory Expiration"
    url: https://docs.mem0.ai/platform/features/memory-expiration
    accessed: 2026-11-21
  - title: "Memobase: What is Memobase?"
    url: https://docs.memobase.io/introduction.md
    accessed: 2026-11-21
  - title: "Memobase: Profile Fundamentals"
    url: https://docs.memobase.io/features/profile/profile.md
    accessed: 2026-11-21
  - title: "Memobase: Event Fundamentals"
    url: https://docs.memobase.io/features/event/event.md
    accessed: 2026-11-21
  - title: "Memobase: Searching Events"
    url: https://docs.memobase.io/features/event/event_search.md
    accessed: 2026-11-21
  - title: "Memobase: Retrieving the Memory Prompt"
    url: https://docs.memobase.io/features/context.md
    accessed: 2026-11-21
  - title: "Memobase and MCP"
    url: https://docs.memobase.io/templates/mcp.md
    accessed: 2026-11-21
  - title: "Memobase: Delete User"
    url: https://docs.memobase.io/api-reference/users/delete_user.md
    accessed: 2026-11-21
  - title: "Redis Agent Memory"
    url: https://redis.io/docs/latest/develop/ai/context-engine/agent-memory/
    accessed: 2026-11-21
  - title: "Redis Agent Memory overview"
    url: https://redis.io/docs/latest/develop/ai/context-engine/agent-memory/overview/
    accessed: 2026-11-21
  - title: "Redis Agent Memory sessions"
    url: https://redis.io/docs/latest/develop/ai/context-engine/agent-memory/sessions/
    accessed: 2026-11-21
  - title: "Redis Agent Memory long-term memory"
    url: https://redis.io/docs/latest/develop/ai/context-engine/agent-memory/long-term-memory/
    accessed: 2026-11-21
  - title: "Zep: Context types"
    url: https://help.getzep.com/v4/context-types.md
    accessed: 2026-11-21
  - title: "Zep: Facts"
    url: https://help.getzep.com/v4/facts.md
    accessed: 2026-11-21
  - title: "Zep: Retrieving context"
    url: https://help.getzep.com/v4/retrieving-context.md
    accessed: 2026-11-21
  - title: "Zep: Deleting Data from the Graph"
    url: https://help.getzep.com/v4/deleting-data-from-the-graph.md
    accessed: 2026-11-21
  - title: "Zep: Context retention"
    url: https://help.getzep.com/v4/context-retention.md
    accessed: 2026-11-21
  - title: "Graphiti overview"
    url: https://help.getzep.com/graphiti/getting-started/overview.md
    accessed: 2026-11-21
  - title: "Graphiti: Searching the Graph"
    url: https://help.getzep.com/graphiti/working-with-data/searching.md
    accessed: 2026-11-21
  - title: "Graphiti: CRUD Operations"
    url: https://help.getzep.com/graphiti/working-with-data/crud-operations.md
    accessed: 2026-11-21
  - title: "Cognee introduction"
    url: https://docs.cognee.ai/getting-started/introduction.md
    accessed: 2026-11-21
  - title: "Cognee MCP overview"
    url: https://docs.cognee.ai/cognee-mcp/mcp-overview.md
    accessed: 2026-11-21
  - title: "Cognee: Persistent Memory Across Sessions"
    url: https://docs.cognee.ai/guides/persistent-memory-across-sessions.md
    accessed: 2026-11-21
  - title: "Letta: Memory"
    url: https://docs.letta.com/agent-sdk/memory/index.md
    accessed: 2026-11-21
  - title: "Letta: MemFS"
    url: https://docs.letta.com/concepts/memfs/index.md
    accessed: 2026-11-21
  - title: "Letta: Shared memory"
    url: https://docs.letta.com/concepts/shared-memory/index.md
    accessed: 2026-11-21
  - title: "Letta: Conversations"
    url: https://docs.letta.com/concepts/conversations/index.md
    accessed: 2026-11-21
  - title: "SurrealDB Agent Memory: Supersession, decay, and forget"
    url: https://surrealdb.com/docs/agent-memory/learn/mental-model/memory-lifecycle.md
    accessed: 2026-11-21
  - title: "SurrealDB Agent Memory: Forgetting memories"
    url: https://surrealdb.com/docs/agent-memory/learn/operations/forget.md
    accessed: 2026-11-21
  - title: "SurrealDB Agent Memory docs"
    url: https://surrealdb.com/docs/agent-memory
    accessed: 2026-11-21
last_verified: 2026-11-21
published: 2026-11-21
---

## Who this is for

Use this when you already know you want a memory layer and need to compare **how official docs say each one stores, retrieves and forgets**. License, hosted pricing, SDK languages, framework ties, and a first-pass “memory model / how it is written / is there an MCP server” table live in [Memory layers for AI agents](comparison:agent-memory-layers). This page does not repeat that table. It adds [MemMachine](entry:memmachine) (added to the directory on 17 November 2026) and two other catalog entries that comparison does not cover — [Memobase](entry:memobase) and [Redis Agent Memory](entry:redis-agent-memory) — and it re-reads the overlapping products only on types, retrieval, deletion and scoping.

Coding-agent memory servers and research libraries are compared separately in [Memory servers for coding agents](comparison:coding-agent-memory-servers) and [Research memory libraries](comparison:research-memory-libraries). The introductory walkthrough remains [Give an agent long-term memory](guide:give-an-agent-long-term-memory). [Use SurrealDB Agent Memory](guide:use-surrealdb-agent-memory) is the SurrealDB-specific guide.

Facts below were checked against official documentation and official repositories on 21 November 2026. Where a vendor page is silent, the cell says **not documented**. No unofficial skill totals or benchmark scores are used. Vendor benchmark pages exist (for example MemMachine’s evaluations page); they are not summarized here as scores.

## What “store, retrieve and forget” means here

- **Memory types.** Whether the product documents episodic or event memory, a semantic or profile store, and/or a short-term or working-memory session tier — using the vendor’s own names.
- **How retrieval works.** The documented search or recall path (vector, lexical, graph, a composed context block, files in context), including any official hybrid or agentic option.
- **Deletion and forgetting.** Explicit delete or forget APIs, time-based expiry or TTL, search-time decay, and supersession or invalidation that closes a fact in time without a hard delete. These are different mechanisms; do not collapse them.
- **Multi-user scoping.** The identifiers official docs use to keep one user’s (or agent’s, session’s, tenant’s) memory from mixing with another’s.

Interfaces (SDK, REST, MCP) are mentioned in the table only where they are how you call those operations. Wiring a remote MCP server is covered in [Connect an agent to a remote MCP server](guide:connect-an-agent-to-a-remote-mcp-server). Identity and token scoping more generally are in [Agent identity and MCP auth](comparison:agent-identity-and-mcp-auth).

## Notes that do not fit a cell

[MemMachine](entry:memmachine) documents MCP tools `add_memory`, `search_memory` and `delete_memory` at [Tools Reference](https://docs.memmachine.ai/api_reference/mcp). An older `/integrations/mcp` docs path, noted in the directory entry, still returned 404 on 21 November 2026 and is not used here.

[Graphiti](entry:graphiti) is Zep’s open-source temporal graph framework; [Zep](entry:zep) is the hosted context layer that uses it. They share bi-temporal facts and hybrid retrieval, but Zep’s user/thread/account graphs, async delete tasks and retention policies are product docs, not Graphiti library docs.

[Letta](entry:letta) memory is agent-owned files in MemFS, not a user-row store in the Mem0/Memobase sense. If you need per-end-user profiles, that difference matters more than the word “memory” in the product name.

Several products document a **default user** or optional IDs (Cognee’s recall when no user is passed; MemMachine MemoryContext fields are all optional). Optional is not the same as “isolated by default.” Pass the scope your product docs require; [Mem0](entry:mem0)’s search page tells you to always include at least a `user_id` filter.

## Related reading

- [Memory layers for AI agents](comparison:agent-memory-layers) — model, writes, self-host and license, hosted pricing, MCP presence, SDK languages, framework ties
- [Give an agent long-term memory](guide:give-an-agent-long-term-memory)
- [Use SurrealDB Agent Memory](guide:use-surrealdb-agent-memory)
- [Vector databases for agents](comparison:vector-databases-for-agents)
