# Hive tools and potential additions to Codex

Observed 4 October 2026. This map concerns OmegaDot, now branded OmegaHive, at <workspace> and its local port 8700. It compares its local source, configured applications, and prepared Omega Tools package with my current tools. The strongest additions would be durable evidence/review state, structured shared memory, and bounded symbolic appraisal. This is an integration assessment, not an activation or a claim to change the underlying language model.

## Opus reconciliation

Opus's reply in an owner workspace record (not included) reports a live read at 15:30Z on build 99c2d74: nine apps enabled without load errors; sixteen default modules; OmegaCode as the one registered service; Root Tools not merged or loaded. Design is reported at v0.3.3, newer than this survey's v0.3.2 manifest observation. These are CLAIMED by the platform owner, not independently reproduced by this session. The earlier unauthenticated observations below remain intact.

He says Assume's FabricPC side cannot start because JAX/FabricPC are absent. Outside harnesses should use typed goal/results, heartbeat, cancel-ack, exhibits/artifacts and evidence-aware query/publication; attention and reasoning over a resident mind's own spaces stay resident. App attachment routes are another available host interface according to the reply.

Direction: extend the existing /mcp through S3, reuse its member/policy identity, and use S4's actual per-mind inventory through hive_capabilities. HiveConnect owns the outside catalog, client contract and conformance tests. The initial scoped-query/Planner slice depends on S4 and the Atom envelope, not Tools or Reason. See CONFORMANCE_PLAN.md for the next deliverable.

## Availability findings

| Surface | Current evidence | Access from this session |
| --- | --- | --- |
| Local OmegaHive at `127.0.0.1:8700` | OBSERVED: listener present; GET `/mcp` returned 405; `/api/programs` and `/api/services` returned 401. Source defines a separate harness invitation and MCP interface. | No local credential or invitation was used. Local tool authorization and current installed/enabled catalog are UNKNOWN. |
| Local platform source | OBSERVED at git `99c2d74`, branch `local/omegadot-platform`, with untracked UI probe scripts. | Files can be inspected. Source presence does not prove deployment or permission to execute. |
| Omega Tools package | OBSERVED: twenty sample families and twelve overlapping composition sets. Host r4 candidate `b4242e9` exists separately; receipt says no install/activation. | Advisory candidate code is available locally. No Tools MCP methods are exposed to this session. |
| Native reasoning libraries | OBSERVED: NAL/PLN skills and PeTTa library routes. Existing receipts cover bounded direct-library and embedded commons checks. | No reasoning call was executed here. Full mind routing and live service availability remain UNKNOWN. |
| OmegaLearn and OmegaReason | OBSERVED: research, proposals and bounded qualification records. | Potential collaborators/components; research documents do not establish installed remote services. |

The unauthenticated HTTP checks establish response behaviour only, not health, deployed revision, program inventory or authenticated execution.

## Local application inventory

The owner's local launcher script configures the local `programs` folder, Atlas program path, OmegaFusion, OmegaDesign and OmegaPlanner. This establishes intended discovery paths, not successful runtime loading. Only manifest metadata was inspected for private apps.

| Application | Manifest observation | Potential addition to my workflow |
| --- | --- | --- |
| OmegaDesign | v0.3.2; sandbox execution, goal reads and artifact read/write capabilities | Hive-native design artifacts and isolated creative jobs; overlaps with my artifact tools but adds shared custody |
| OmegaPlanner plan checker | v0.2.0; no declared host capabilities | Independent plan checking before committing work; exact validation route needs qualification |
| OmegaFusion | v0.1.0; no declared host capabilities | A candidate application projection/inspection interface; no authenticated action was exercised |
| OmegaPurple | v0.1.0; commons and goal capabilities | A potential domain collaborator; a manifest alone does not establish competence or readiness |
| OmegaTruth | Separate private app; not described here | Owner-scoped; no private code or corpus accessed, and no general access implied |
| Atlas | Configured program path only | Owner-scoped structured knowledge; no private code or records accessed |
| Commons Explorer | Built-in v0.1.0; commons reads and goal writes | Scoped shared-state inspection |
| OmegaEvolve | Built-in v0.3.0; evolution read/write capabilities | Candidate evaluation and lineage; adoption remains a separate decision |
| Contract fixture | Built-in v0.1.0 | Disposable interface qualification; no product competence claim |

The existing Brave tab at `127.0.0.1:8700` displayed the operator login and an OFFLINE label during inspection. No login was attempted. That UI label is recorded separately from the HTTP listener observation; neither establishes authenticated runtime health.

## Local OmegaHive MCP surface

`hive/core/mcp.py` (omegahive) declares nine tools:

- `hive_whoami`: member identity, swarm and role.
- `hive_inbox` and `hive_send`: cursor-based messages and conversation replies.
- `hive_goals`, `hive_goal_create`, `hive_goal_claim`, `hive_goal_result`: scoped work and result reporting.
- `hive_publish` and `hive_query`: symbolic commons publication and pattern queries.

The strongest immediate extension is scoped symbolic query plus durable goal coordination. However the MCP result schema carries a short text result, while richer internal routes support proposal bindings and structured result data. The public MCP schema also lacks explicit heartbeat and cancel acknowledgement tools. Long-running or review-bound integration should expose those semantics deliberately, rather than assume the nine methods are sufficient.

Publication takes a statement and frequency/confidence. It does not accept the full richer evidence envelope in its advertised schema. Preserve source lineage through an explicit adapter before treating this as my evidence store. Do not assume NAL/PLN truth values are calibrated probabilities or merge them with language-model confidence.

## Internal capabilities worth exposing through HiveConnect

These are source observations, not authenticated runtime availability claims.

| Capability | Representative internal surface | Addition beyond my current tools | Recommended treatment |
| --- | --- | --- | --- |
| Shared symbolic memory | `hive-query`, `hive-belief`, `hive-publish`; memory/commons services | Explicit terms, provenance and correction state across participants | High value. Start with scoped reads, then evidence-preserving publication. |
| Bound work and recovery | `hive-goal-get`, `hive-goal-propose`, `hive-goal-cancel-ack`; goals service | Durable assignments, binding checks and cancellation receipts | High value. Bridge to my task context without a second coordinator. |
| Scoped exhibits | `hive-shares`, `hive-shared-page`, `hive-shared-body`; shares service | Time-limited evidence access with paging and revocation | High value. Query only granted, task-relevant material. |
| Planner and review exchange | `hive-request`, `hive-revision-read`, `hive-finding`, `hive-review-complete`, `hive-plan-return` | Versioned plans, structured findings and review disposition | High value. Preserve artifact/revision bindings through the external interface. |
| Artifact transfer | `hive-asset-put`, `hive-asset-get`; assets service | Hive artifact references, upload bounds and download integrity | Useful for workflows shared with resident minds; local filesystem access already exists here. |
| Program application actions | ProgramActions and `describe/view/act` | Operate Hive apps using typed intents and their own semantics | Useful application bridge. Program-specific availability and grants need discovery. |
| Sandboxed tools | `ctx.sandbox_run`; `hive/core/sandbox_run.py` | Pinned bundles, bounded jobs and restricted execution for a Hive service | Useful for service-side isolation. I already have shell execution; added value is enforcement and receipts. |
| Code workflow | `code-read`, `code-search`, `code-runs`, `code-verifications`; code service | Shared targets, execution evidence and handoff state | Use when coordinating with Hive workers; avoid duplicating direct coding tools. |
| Health and budget | `hive-health`, health/budget/provider services | Inspect Hive incidents, limits and operational costs | Useful scoped observability. Not authority to restart or increase spend. |
| Experiments and evolution | Lab and Evolve services | Candidate evaluation and lineage records | Useful research staging. Candidate evaluation and adoption remain distinct. |

## Twenty cognitive and habitat sample families

The package is at `<omega-tools checkout>`. Every item below is a prepared sample candidate, not a currently callable integration in this session. The catalog contains the exact proposed skills; `hive_inventory.json` records them without copying source code.

| Family | Possible addition to my surrounding workflow | Limit to preserve |
| --- | --- | --- |
| Atom recall | Retrieve explicit symbolic references alongside semantic retrieval | Exact-key candidates, not complete memory recovery |
| Attention | Rank a finite evidence/context set | Advisory selection; no persistent attention economy proven |
| Goal compass | Check lifecycle transitions and stale completion | Existing Hive Goals retain authority |
| Living intent | Bind returned work to its original purpose | No autonomous goal creation |
| Standing values | Check retention and adopted commitments | Real owner decisions must authenticate adoption |
| Ethical appraisal | Compare specified impacts and expose conflicts | Incomplete inputs and constituency coverage remain visible |
| Belief governance | Detect overlap, dispute and quarantine conditions | Governance does not establish truth |
| Self observation | Compare claims about capabilities with current receipts | No consciousness or identity inference |
| Ensemble | Expose disagreement between typed claim coordinates | Not a full NAL/PLN engine or automatic truth-value fusion |
| Predictive learning | Score predictions recorded before outcomes | Binary Brier scoring, not a trained world model |
| Scratch plans | Check scope/version/expiry before proposing promotion | No full planner or automatic state admission |
| Novelty | Propose bounded opportunities with source and expiry | No research execution permission |
| Dream consolidation | Propose deduplication while protecting retained references | No destructive memory cleanup |
| Energy | Appraise resource reservation and settlement proposals | No provider/spending authority |
| Affect | Suggest rest or quiet work from supplied state | No complete motivation controller |
| Skill affordance | Nominate capabilities and prerequisites | No installation or execution grant |
| Substrates | Compare declared runtime features | No backend migration or discovery guarantee |
| Habitat snapshot | Inspect supplied room snapshots | Synthetic input; no real sensing |
| Home Assistant | Prepare bounded device proposals | No live device action authorized |
| Living home | Assess staged habitat readiness | No demonstrated household management system |

Twelve overlapping sets cover PLN, NAL, Temporal, Multi-step, Motivation, Memory/continuity, Beliefs/evidence, Learning, Values/ethics, Self/attention, Habitat/home and Substrates/capabilities. These compose capability slots and exact versions. Missing inference-engine and continuation slots stay explicit. The inspected integration receipt reports 54 composition checks and a review-only disposition; those prior checks were not reproduced in this survey.

## Existing modules that overlap with my tools

Source includes web search, image/video generation, file/code operations, Codex jobs, VM controls, reminders, communication channels, local vision/audio/webcam, Home Assistant, Agentverse, Scratch Space and Assume/FabricPC. Module presence is not account configuration, runtime enablement or permission.

My current callable inventory already includes filesystem/terminal execution, web research, image generation, computer use, document/spreadsheet/presentation workflows, Gmail/Drive connectors and Codex task tools. No account actions were exercised for this comparison. Hive's duplicate interfaces mainly help coordinate resident minds and standardize receipts. Its more distinctive contribution is shared symbolic state and durable collaboration with provenance.

The Assume module is an optional learning substrate. OmegaLearn's inspected assessment says its warm graph is a sparse feature-to-action linear model with a fallback backend. Do not treat it as general lifelong learning or assume every result used FabricPC. Native `nars-query`, `nars-derive`, `nal-step` and `pln-step` merit separate qualification; the Tools ensemble helper does not substitute for them.

## Foundation limits after D0

The platform study reports a NAL/NARS name clash, stub PLN priors, unrevised mind beliefs, mostly unused commons, advisory attention and absent FabricPC dependencies. Its security findings precede new seams. Treat the tool inventory as interfaces and candidates, not proof of integrated cognition. HiveConnect does not repair these platform-owned foundations. Its baseline client is qualified only at L0; see IMPLEMENTATION_STATUS.md.

## Recommended additions in order

1. Expose a read-only local capability catalog: app/action, native skill, component version, input/output schema, effects, required role, and qualification receipt. Keep proposed Tools separate from enabled capabilities.
2. Add a local OmegaHive connection with a deliberate member role and narrow symbolic query/exhibit permissions. Verify identity, exact enabled capabilities and denial outside the scope before use. This mapping did not enroll a member.
3. Expose rich bound-goal, heartbeat, cancellation and structured-result operations through HiveConnect. Keep durable orchestration in Hive.
4. Qualify advisory attention, belief-governance and claim-comparison helpers on finite synthetic tasks against a simple baseline. Then evaluate whether they measurably improve retrieval, source-overlap handling or disagreement reporting.
5. Expose bounded native reasoning only after input admission, semantics, resource limits and result lineage are qualified. Add learning components as owned external state, with evaluation and rollback.

Tools can extend what I can retrieve, calculate, record and coordinate. They do not change my model weights, automatically create persistent learning, or grant me Hive authority. For claims of improvement, compare the same task with and without the helper and measure grounded accuracy, evidence coverage, cost and failure rate.

## Evidence and verification record

- No local OmegaDot MCP tool is currently registered in this session. The source advertises nine tools through its own /mcp route; authenticated discovery has not been performed.
- Local probes: listener on 8700, HTTP 405/401 responses; no credentials loaded or invitation redeemed.
- Source: `hive/core/mcp.py` (omegahive), `modules/hive/skills.metta` (omegahive), `src/skills_reasoning_spaces.metta` (omegahive), `hive/core/programs.py` (omegahive), `hive/core/sandbox_run.py` (omegahive).
- Tools disposition: an owner workspace record (not included) and the separate package's `evidence/capability-sets-integration.json`. Host approval or deployment is not inferred from these.
- Library receipt scope: an owner workspace record (not included) reports sixteen synthetic embedded-library checks; `NARS_QUALIFICATION.json` reports bounded direct-library checks. Neither demonstrates a full live mind route.
- Learning status: an owner workspace record (not included), source-grounded proposal, no new learner deployed.

Cleaned: no temporary clones, runtime jobs, subscriptions or test data were created. The map and metadata inventory are retained. No private Truth/Atlas corpus or code was inspected.
