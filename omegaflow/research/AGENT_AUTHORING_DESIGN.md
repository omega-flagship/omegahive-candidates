# OmegaFlow agent authoring and reusable skills

Design proposal, 4 October 2026. Implements the owner's requirement at the design level: the Hive should interact with the workflow builder as needed, including creating workflows it can retain as skills. This document does not claim these APIs exist.

## Shared authoring model

The canvas is a view and editor over the typed workflow model. Minds use structured host operations over that same model. Graphical computer use can remain an optional interaction method; the normal agent path should not depend on pixel coordinates. Changes become immutable revisions with authorship, explanatory intent and base-revision checks. Layout is independently editable.

A mind acts under its actual Hive identity and current capability. The inspected Flow host currently requires a named person session. Add an explicit scoped agent path rather than impersonating a person or weakening the existing endpoint. Let minds author freely within their authorized workspace; request human intervention only when current policy requires adoption, registration or effects beyond delegated scope.

## Proposed operations

| Operation | Result | Boundary |
| --- | --- | --- |
| discover | Visible workflows and skill descriptions matching a need. | Visibility-filtered metadata; retrieve larger bodies when needed. |
| read | Exact revision and authorized supporting records. | No inferred permission from a reference. |
| draft | New local or stored draft with reason and provenance. | Agent may create within its granted authoring scope; no invocation. |
| revise | New immutable revision from a specified parent. | Expected revision required; conflicts reported without overwrite. |
| validate | Structural, contract and host-binding findings. | Declares what was checked and what remains unknown. |
| evaluate | Results from isolated declared fixtures. | No live effects in a dry run; integration tests need their own scope. |
| propose skill | Skill contract referring to a pinned revision and dependencies. | Uses existing registry where possible; no capability grant. |
| register | Discoverable skill revision within a namespace. | Separate publication policy; drafts can remain private to a mind or swarm. |
| invoke | New run with actor, inputs and current capability binding. | Existing host admission, budget and effect checks apply. |
| inspect and revise from evidence | Run explanation and proposed improved definition. | Preserve provenance; do not silently alter active runs or adoption. |

Tool results should carry stable ids, revision digests and structured errors. Bound request sizes, patch count and returned context. Return handles and summaries before large graph bodies. A stale revision, unavailable dependency or denied binding should be a useful result the mind can plan around.

## Skill contract

Proposed fields: stable skill id and revision; purpose and discovery description; input and output schemas; exact workflow digest and pinned dependencies; parameter mapping; required capabilities and permitted effect classes; budget and deadline limits; evaluation references; failure and cancellation behavior; author, scope and retirement status.

Pin all behavior-bearing dependencies, including instruction or validator versions where applicable. Resolve an invocation to an exact skill and workflow revision and retain its binding. A graph digest alone cannot pin changing tools, prompts or host behavior.

Permissions are checked at invocation and before advancing effectful work. A stored requirement or allowed-tools hint is a declaration, not a host grant. Scoped delegation can permit recurring invocation without a person clicking every run. Human review remains attached only where the applicable policy requires it.

When retiring a skill, distinguish preventing new invocations from cancelling existing runs. A later policy revocation can still block a pinned run. Display both definition history and operational history to the authorized viewer.

## Coauthoring and composition

Human and mind edits share revision conflict handling. A mind returns a typed patch and its reason. The canvas shows the affected objects and meaningful differences. Moving an object does not invalidate semantic adoption; changing a trigger, participant binding or action does.

Composition must not expand authority. A parent can invoke a child only when the effective scope satisfies both contracts. Child cost and deadline count against the invocation budget. Detect recursive dependencies and set depth limits. The current execution subset refuses subflows; this is a later extension requiring qualification.

Inferred or generated steps should retain their origin and supporting sources. Do not equate a model-generated rationale with evidence of correct behavior. Future Hyperon reasoning produces typed proposals through the same revision mechanism.

## First acceptance scenario

An authenticated synthetic mind receives a research need, discovers no suitable skill, creates a four-step draft and publishes a revision within its authoring scope. A person reads and edits the same definition. A conflicting mind edit is rejected with the current revision rather than overwriting the person's changes.

The mind proposes a reusable skill with explicit inputs and outputs. Policy permits registration in a synthetic swarm namespace. An authorized invocation creates only permitted native goals and pauses at the configured review gate. It retains actor and binding records. A second invocation uses different inputs without carrying instance-specific identities or secrets from the first.

Revoke invocation permission and verify advancement blocks. Restart the disposable controller and verify no duplicate goals. Change the workflow and verify the existing run still references its original revision. Check discovery from a foreign scope does not disclose private skill metadata or evaluation material.

These checks qualify a narrow capability loop. They do not establish external effect deduplication, general self-improvement, or live production acceptance.

## Platform review questions

1. Which existing Hive agent authentication and capability path should authorize draft publication and revision?
2. Which existing skill registry stores discovery metadata, pinned resources, ownership and retirement?
3. How does an agent invocation bind current authority without a named-person session, and how does revocation reach the coordinator?
4. Which operations can be admitted now while preserving the conservative goals-only execution subset?

Review outcome should identify source entry points and the smallest proposed change. Agent authoring is required by the product direction; the unresolved choice is how to integrate it cleanly with the current host.

## Existing OmegaDot skill discovery

Source inspection identifies the symbolic directory in `src/skills_affordance.metta` (omegahive) and discovery signatures in `src/skill_signatures_affordance.metta` (omegahive): query-skill-space, choose-skill-for, explain-skill and skill-card. Extend this directory for discoverable workflow skills while retaining durable definition revisions in the artifact store. This establishes a source integration point, not live registration or invocation. See [OmegaDot tool map](OMEGADOT_TOOL_MAP.md).

## Opus implementation feedback received

Opus's OPUS_AGENT_AUTHORING_REVIEW.md specifies member-token routes through agent_from, own-swarm C39 draft revisions attributed to agent:<id>, exact-only permission for hive-flow-publish, fixed native discovery/invocation skills and a durable flow_skills host table. The existing symbolic directory is module-declared discovery, not a dynamic workflow registry. Reusable definitions belong in the proposed host table with pinned artifacts. Agent runs should recheck lifecycle, run policy and published digest before advancement. Person adoption remains on the existing path.

The staged candidate plan and remaining binding questions are in an owner workspace record (not included). Registration and execution have not been implemented as part of this feedback exchange.
