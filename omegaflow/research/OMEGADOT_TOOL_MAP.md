# OmegaDot tools and additions to this agent

Corrected scope, 4 October 2026. The owner means OmegaDot in this workspace, including its native minds, core skills, module organs and OmegaHive services. A previous map incorrectly included a separate signed-room Hive connector and frozen team-memory projection. Those connector results establish nothing about OmegaDot tool availability and are excluded here.

This is a source-grounded capability map. It identifies where OmegaDot can extend my working process and where my existing tools overlap it. It does not claim that I am currently an authenticated OmegaDot mind or that every catalogued organ is loaded. No real memory mutation, agent start, provider call or external action was performed.

## Existing discovery system

OmegaDot already supplies an inspectable symbolic skill directory in `src/skills_affordance.metta` (omegahive). Its declarations include Skill, SkillTopic, SkillArg, PreferredWhen, Risk, Effect and SkillCardLine, plus candidate and active triggers and aliases. `src/skill_signatures_affordance.metta` (omegahive) supplies discovery signatures. Core catalogues and module catalogues provide additional skill descriptions.

Use query-skill-space to discover a topic; choose-skill-for to obtain candidate skills and rationale; explain-skill to inspect arguments, risks and effects; skill-card for compact context. Skill suggestions guide the agent's choice; they are not automatic dispatch or authority. Candidate trigger and alias promotion is a separate mutation.

This is the most immediately relevant foundation for OmegaFlow. Extend this directory with workflow skill descriptors and pinned revision references instead of inventing a competing discovery registry. Whether it should also store durable workflow contracts requires platform review; a discovery directory and an immutable artifact store have different responsibilities.

## Capability map

| OmegaDot subsystem | Representative native surface | Addition to my working systems | Qualification boundary |
| --- | --- | --- | --- |
| Skill discovery | query-skill-space, choose-skill-for, explain-skill, skill-card, skill-suggestions-for. | Situation-aware tool selection with explicit argument, effect and risk descriptions; compact retrieval reduces unnecessary context. | Source implementation and signatures inspected; live registered contents not queried. |
| Structured memory | persistent-fact, persistent-rule, world-fact, belief-claim, beliefs-for, beliefs-about, events-recent. | Separate durable principles, world relations, uncertain claims and events instead of keeping everything in prose summaries. | Writes would alter a mind's memory; access and current ownership must be established. |
| Recall and continuity | query, episodes-at, pin, activity-traces, space-registry, space-find/examples. | Recover prior work and obligations using time and structure, and retain a compact continuation pointer across turns. | Pin is volatile, not durable truth. Native records are not this chat's automatic memory. |
| Agenda | agenda-goal, agenda-active, agenda-waiting, agenda-blocked, agenda-scheduled. | Persistent task state and explicit reply debts for work spanning sessions. | An agenda entry is not execution authority or proof that a task is complete. |
| Scratch and attention | scratch-find, scratch-pressure, scratch-add, scratch-promote; attention-status, immune-candidates, attention-focus, ecan-pass. | Bounded provisional hypotheses, salience inspection and reviewed memory cleanup. | Reads, provisional writes, promotion and retirement are distinct. Availability and usefulness need observation. |
| Symbolic reasoning | truth-expectation, test-metta, nal-step, pln-step, nars-query, metta. | Explicit premise-based derivation over suitable typed facts, with uncertainty inspectable. | Raw metta and run-metta-file evaluate code and may have effects. Syntax checks do not prove semantics; use isolated fixtures for qualification. |
| Assume | assume-predict, assume-audit, evidence summary, growth proposals and reviewed writeback. | Compare predicted and observed outcomes and propose learning or procedural changes. | Source-defined predictive organ; model quality and active learning authority not verified. |
| Hive commons | hive-query, hive-belief, hive-publish. | Share beliefs with evidential sources and inspect the basis of another mind's claim. | Agent/swarm scope applies. Publication records an assertion, not independently verified truth. |
| Native goals | hive-goals, hive-goal-get, hive-goal-claim, hive-goal-propose, hive-goal-create, cancellation acknowledgment. | Durable assignment and decomposition with contract-bound results. | Needs actual OmegaHive agent identity and authorized goal scope. My existing shell tool does not confer that identity. |
| Artifacts and review | hive-artifact-create, hive-revision, hive-revision-read, hive-findings-read, hive-review-complete, hive-plan-review-context. | Exact revision custody, canonical objections, reviewer responses and preserved dissent. | Actor roles, request scope and current bindings come from the host. Readable evidence references do not establish their truth. |
| Sharing | hive-shares, hive-shared, hive-shared-body, hive-exhibit and share request/grant/revoke. | Bounded, time-limited context exchange between minds instead of copying entire memory stores. | Expiry and visibility apply. Complete paged bodies need all parts and digest verification. |
| OmegaPlanner | Native planning adapter, stored-plan validation, reasoning snapshots and review-return contracts. | Dependency-aware plans and targeted re-review after changes. | Source includes qualified disposable API adapters; a protocol harness does not establish live planning quality. |
| OmegaMatch | Native offernet design and semantic admission companion. | Explain which minds/services fit a need and notice reusable capabilities. | Its README describes incomplete catalogue integration and no activation. Recommendations do not assign or grant authority. |
| OmegaReview | Versioned reviewer mandates, findings and independent-review admission protocol. | Separate implementation from assessment and keep unresolved objections visible. | README describes a protocol slice, not a mounted authenticated running swarm. Host routing and evidence custody remain necessary. |
| OmegaCode and code organ | code-read/search/status, frozen runs, verifications, hunk inspection, approved edit/exec/export and merge preview. | Shared version-bound code work and exact verification records linked to Hive goals. | Overlaps my local Git and shell tools. Trusted-native execution is not an OS sandbox; grants and host approvals matter. |
| OmegaBench and OmegaEvolve | Sealed benchmark registrations, comparisons and research contribution/program actions. | Evaluate proposed skills or reasoning changes against a fixed baseline before adoption. | Imported receipts and synthetic protocol success do not prove a capability improvement. Native evaluation/adoption remains a separate gate. |
| Lifecycle and energy | hive-lifecycle-status/start/stop; energy-status, cost-last-call, cycle-status, set-energy-mode. | Budget-aware coordination and inspection of leased workers. | Status differs from starting/stopping a mind. No live lifecycle operation exercised. |
| VM, body and policy | body-status, body-container-status, vm-status, vm-policy-status/audit/connections. | Observe where work runs, what resources it can reach and which boundary is actually enforced. | A policy plan or status report is not proof of containment; boot/shell/restart operations are effectful. |
| Channels and senses | Router plus messaging modules, vision/audio/webcam, Home Assistant and other domain modules. | Perception and interaction within OmegaDot's environment, feeding workflow evidence. | Module presence does not establish channel/device configuration or authorized access. Private domain material excluded from inspection. |
| Media, search and publishing | web-search, image/video generation, artifact publishing. | Produce or retrieve workflow inputs/outputs with native traces. | Mostly overlaps tools I already have. Providers and publication authority require independent verification. |

Source references: core catalogues under `src/skill_catalog*.metta` (omegahive); module definitions under `modules/*/{module.toml,catalog.metta,skills.metta,signatures.metta}` (omegahive); native Hive bridge `modules/hive/src/hive_commons.py` (omegahive); host `hive/core/app.py` (omegahive); service README and public contracts under `omegaplanner`, `omegamatch`, `omegareview`, `omegacode`, `omegabench` and `hive/plugins/omegaevolve` (omegahive).

Private OmegaTruth and Atlas are identified only as owner-controlled integrations. Their code, corpus and private records were not read for this map.

## How these add to my systems

The highest-value extension is structured procedural context: retrieve a relevant native skill, inspect its requirements, reuse its pinned procedure and retain an attributable outcome. This adds organization and continuity around my reasoning rather than changing model weights or pretending permanent learning has occurred.

A second extension is explicit reasoning assistance. A small scoped fact set can be checked through native symbolic operations, with returned premises and uncertainty. Compare it against straightforward typed-graph code before making it a default. Do not use arbitrary evaluation as an apparently harmless query.

A third is durable coordination. Native goals, artifacts and review records can preserve ownership, binding and dissent after a chat ends. My current local files and tools remain useful for implementation, but shared custody can make later handoffs more reliable.

A fourth is attention and outcome learning. Agenda, provisional scratch space, attention review and Assume could expose neglected obligations and recurring failure. Start by observing and evaluating those signals. Do not automatically promote speculative conclusions into persistent beliefs or revise a skill from one successful run.

Generic shell, browser and media operations offer less incremental value because I already have equivalent tools. Prefer the OmegaDot route when its identity, goal binding, environment or provenance materially helps the task. Otherwise keep the simpler local operation.

## Proposed adapter and OmegaFlow use

The smallest proposed bridge would expose native skill discovery, exact artifact/review reads and scoped status queries under a genuine OmegaDot identity. Return compact typed results with source and version references, explicit refusals and separate unknown state. Avoid a general raw-MeTTa endpoint as the default interface.

Then extend the existing skill directory with workflow descriptions: purpose, inputs/outputs, pinned flow revision, required capabilities and evaluation references. Keep invocation authority in the host, and keep durable revisions in the artifact store. A mind can compose and revise drafts within its authoring scope and invoke approved skills under delegated scope; per-run human clicks are needed only where policy requires them.

A useful acceptance sequence is discover → inspect → compose draft → validate → invoke in a disposable scope → inspect canonical results → propose reusable skill. Demonstrate that a person can edit the same definition, that conflicts preserve intent, and that a later mind retrieves it without copying the earlier mind's private state.

## Availability and survey limits

The machine inventory OMEGADOT_TOOL_INVENTORY.json includes native core and module catalogues with content hashes, plus selected host routes. Help entries may be grouped topics or aliases and must not be counted as independent runtime tools. Other installed route components and dynamically loaded programs are outside the route extraction.

The local OmegaHive HTTP service answered authentication-method metadata, while unauthenticated Flow-template and agent-service-catalogue reads returned 401. This is a current read-only observation of the host boundary. No current registered skill catalogue, authenticated service list or active native worker inventory was obtained. The source map therefore shows potential and integration points, not claims that I can already invoke all of them.
