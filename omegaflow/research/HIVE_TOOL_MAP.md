> Superseded for the owner's request: this document incorrectly mixes a separate signed-room connector with OmegaDot. Use [OmegaDot tool map](OMEGADOT_TOOL_MAP.md). Connector probes do not establish OmegaDot access.

# Hive tools and additions to this agent

Observed 4 October 2026. This map identifies capabilities that could extend this agent's working process. It distinguishes callable connectors, successful read probes, exposed write contracts and source-defined OmegaHive skills. No agents were started, messages sent, permissions changed or memory proposals written during the survey.

## Current access and distinct systems

The current tool inventory exposes 20 signed-room Hive tools and seven OmegaV2 team-memory tools. Read calls succeeded for Hive whoami, scopes, board, permits, federation and search, and team-memory status and search. Write contracts were inspected but not exercised; exposure does not establish that an operation will be permitted.

The signed-room connector identifies this connection as a team seat in a shared room, backed by the fusion Hive. The scope describes a committed-room policy with quorum two. It returned one closed card and no active cards, no merge permits, and federation metadata identifying imported records. These are a point-in-time view of this room, not a census of all Hive work or permission to act as a principal. A search for OmegaFlow workflow tools and skills returned no hits and embedder null; semantic retrieval is not established by this probe.

OmegaHive in the workspace is a separate agent/swarm system. Local localhost:8700 returned 200 for authentication-method metadata and 401 for both Flow templates and the agent service catalogue without credentials. This verifies a reachable HTTP surface and an access boundary, not authenticated agent access. The signed-room seat does not supply an OmegaHive agent token.

The separate team-memory connector reports snapshot omegav2-pilot-2026-07-14-a: seven facts, six accepted facts, one nonaccepted fact, and three proposals pending review authorization. These are two separate sets, not a sum of accepted facts and proposals. Search for workflow skill returned no items. This is a frozen pilot projection with a proposal overlay; it is not a current all-memory view.

## Callable tool map

| Tools | Status established here | Addition to my working process |
| --- | --- | --- |
| whoami, scopes | Successful read probes. | Establish identity, room policy, participants and reported presence before collaboration. |
| board, permits | Successful read probes; no active cards or merge permits returned. | Durable work-state inspection and explicit permission evidence alongside local task tracking. |
| search, fetch, artifact_get | Search responds; fetch and artifact_get contracts inspected. | Retrieve prior decisions and exact artifacts using provenance pointers. Search results need source inspection before becoming claims. |
| federation | Successful metadata read. | Track imported records and their origin without treating an import as local adoption or current runtime evidence. |
| inbox, mailbox, wait | Exposed contracts, not called. | Addressed work and asynchronous continuation. Reserve wait for an authorized collaboration loop; it may conflict with an existing consumer. |
| artifact_put | Exposed write contract, not called. | Shared content-addressed deliverables rather than chat-only context. Storage and registration remain distinct. |
| message, reply, finish | Exposed write contracts, not called. | Addressed requests, replies and outcome reporting when the user authorizes communication. |
| review_commit, review_reveal, reviews | Exposed contracts, not called. | Review of exact subjects with commitment before disclosure. Room quorum and reviewer identity must be honored. |
| post, ack | Exposed mutation contracts, not called. | Typed work events, claims, evidence, decisions and receipts. post includes governance mutations; admit only a narrow operation set for a given task. |
| memory_status, search_memory | Successful read probes on the frozen pilot. | Retrieve accepted, provenance-bound information without mixing it with claims or proposals. |
| open_memory, temporal_memory, list_superseded_memory | Exposed read contracts, not called. | Inspect sources, facts valid at a time and explicit replacements. Useful for resolving contradictory or stale context. |
| list_memory_proposals, propose_memory | Exposed contracts, not called. | Inspect quarantined claims or propose additions for review. Proposal creation is not accepted memory and was not authorized as part of this mapping. |

The machine-readable callable inventory preserves all 27 argument contracts in HIVE_CALLABLE_TOOL_INVENTORY.json. Discovery came from this task's actual tool registry, not assumed account sign-in or configuration.

## OmegaHive source tools

The workspace survey found 29 module catalogues and 218 SkillHelp entries. Entries include grouped help and aliases; they are not 218 independently registered tools. HIVE_SOURCE_TOOL_INVENTORY.json retains catalogue text, help entries, file hashes and 63 selected app.py routes. Other route-installing components exist, so 63 is not a total API count.

Source checkout HEAD was 99c2d740322b5c14f728dc2a8a4c5b99c5f84633. Untracked probe scripts were present and left untouched. File hashes identify the inspected catalogue contents. This source snapshot is not proof of the running service's commit.

| Source family and representative tools | Potential addition | Access and limits |
| --- | --- | --- |
| Hive goals: hive-goals, hive-goal-get, hive-goal-claim, hive-goal-propose, hive-goal-create, cancellation acknowledgment. | Durable decomposition, task ownership and results bound to a goal's contract. | Needs a real OmegaHive agent identity, visible swarm and permitted goal actions. |
| Hive commons: hive-query, hive-belief, hive-publish. | Shared relational knowledge with truth values and evidential sources. | Source-defined; successful publication is an assertion, not proof. Do not merge dependent evidence as independent support. |
| Artifacts and review: hive-artifact-create, hive-revision-read, hive-findings-read, hive-plan-review-context, hive-review-complete, hive-plan-return. | Exact revision custody, canonical findings, dissent and review receipts. | Request/role scoped; source distinguishes planner responses from reviewer dispositions. These are not the signed-room review protocol. |
| Sharing: hive-shares, hive-shared, hive-shared-body, hive-exhibit and share request/grant/revoke. | Retrieve larger context through bounded pages and time-limited sharing. | Access and expiry apply; a long body is complete only after all parts and digest verification. |
| Services and programs: agent service-catalogue, connections, requests, program act route. | Discover specialists and request structured work across swarms. | Source-defined; live catalogue read returned 401. Requires connections, service policy and actor permissions. |
| Code: code-read, code-search, code-status, code-runs, code-verifications, code-hunks, merge-preview and approved edit/exec/export operations. | Version-bound code work and retained verification records tied to Hive goals. | Overlaps my shell and Git tools. Its value is shared custody and authority. History is not liveness; mutations and runs have host approval requirements. |
| Scratch: scratch-find, scratch-pressure, scratch-add, scratch-gc, scratch-promote. | Provisional symbolic working memory with expiry and deliberate promotion. | Agent-local source capability; mutation and promotion are distinct from reading. Not a new accepted-memory path for this task. |
| Assume: assume-predict, assume-audit, evidence summary, growth proposals and reviewed writeback. | Inspectable prediction and candidate learning from outcomes. | Source capability only. Quality, readiness and installed mutation authority remain unverified. |
| VM policy and body: vm-policy-status, vm-policy-audit, body-container-status, omega_vm. | Observe execution boundaries and confinement evidence. | Observational plans are not enforcement; boot, shell and launch operations have effects. |
| Agentverse and codex_code | Remote agent exchange or coding delegation. | Overlaps existing agent tooling; reachability and authority unverified. Calling it requires an authorized delegation task. |
| Scheduler reminders | Agent-local reminders and due work. | Overlaps existing scheduling tools; choose the owner of the reminder to avoid duplicate wakeups. |
| Search, image/video generation, vision, audio and webcam senses | Evidence gathering and media/sensory tools for workflows. | Source-defined; many overlap my current tools. Provider and device access are not established. |
| Channel router, WhatsApp, Telegram, Slack, Mattermost, IRC and web control | Workflow inputs, outputs and addressed communication. | Catalogues do not prove configured live channels. Sending requires explicit user authorization. |
| Publishing | Artifact identity, shelves and publication operations. | Source-defined. Observation and stored files do not establish publication; actual publication is a separate effect. |
| Home Assistant, glucose observation and Game Boy | Domain-specific observations and environment interactions. | Source-defined; physical/device and private health access were not probed. |

## Recommended integration order

First, use the callable read surfaces during relevant work: establish scope, search for prior decisions, inspect exact supporting records and retain references in local artifacts. Keep the frozen team-memory snapshot labeled by its identity and date. Negative search results are not proof that a capability or decision does not exist elsewhere.

Second, use Hive artifact and review mechanisms for authorized collaboration. The same deliverable can have a local editable source and an exact shared revision; preserve both identities. Communication and review requests require the relevant user-authorized task. Do not autonomously claim room cards or publish proposals merely to populate this map.

Third, add a narrow OmegaHive adapter after the platform supplies the genuine identity and capability path. Start with service discovery, exact artifact reads, findings and goal inspection. Later admit draft workflow creation and skill registration under separately scoped mutations. Never borrow a person session or assume the MCP seat can impersonate a Hive mind.

Fourth, connect procedural reuse: need → retrieve a skill → bind inputs and current scope → invoke native work → inspect receipts → propose a revision. This agent can use the external loop without changing its model weights or claiming permanent learning. A reusable artifact or skill is durable procedural context; the runtime must actually retrieve and invoke it on later work for continuity to be demonstrated.

## OmegaFlow use of the map

Represent each tool as a capability descriptor with stable identity, system/transport, argument schema, input/output contract, effect class, required actor and scope, discovery source, version and observed availability. Separate unknown effect classification from a safe read classification. Attach health and admission results as observations with timestamps, rather than changing the capability definition based on one probe.

A workflow should bind exact tool and policy versions where applicable, and resolve its current actor's authority at invocation and before effects. The canvas can display unavailable tools and the missing prerequisites. Agent authoring uses the same descriptors. A generated tool choice must be checked against the actual catalogue; a catalogued choice must still pass runtime admission.

The largest likely gain is coordinated work with persistent, attributable evidence. Generic execution and generation are already available in this task. Hive integration should earn its complexity by making handoffs, retrieval, review and procedural reuse more reliable and inspectable.
