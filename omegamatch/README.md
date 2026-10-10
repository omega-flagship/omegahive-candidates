# OmegaMatch candidate

OmegaMatch is a native offernet reasoning mind over the hive's shared capability
catalogue and existing matcher. It interprets needs, explains candidate fits and
notices reusable code/services. Planner owns planning and plan-to-code work with
Code and Review. Match recommends; it does not assign, dispatch or grant authority.

## Current state

- Hyperon theory: `HYPERON_THEORY.md`, grounded in primary metagraph/MeTTa research.
- Result contract and host-subset schema: `CONTRACTS.md`, `schema.py`,
  `reuse-alert.schema.json`.
- Self-contained semantic companion: `program/`, including the canonical admission
  implementation in `program/protocol.py`. Root `protocol.py` re-exports it.
- Native blueprint: `swarm.py` / `swarm-blueprint.json`: omega members, stopped,
  zero budget, no public services, proposed connection-only match.
- **73 pure checks pass**, including standalone Python isolated-import loading.
- Contract 0.1 checker compatible: all four stages valid and IDs stable.
- **3 host semantic refusal probes pass** against a retained uncommitted host
  snapshot: missing catalogue, evidence promotion and unknown validator refuse
  completion; claimed state and failed-attempt evidence are preserved.

Host catalogue integration remains incomplete; the generic semantic hook and
lifecycle correction are adopted in committed platform source. No shared program mount,
swarm registration, native worker activation or deployment has occurred.

## Host boundary

The current host calls `validate_result(ctx, goal, proposal)` synchronously and
provides `ctx.validation`. Match supports that attribute or the proposed generic
`ctx.validation_context(goal)` method. It then requires `ctx.viewer_for_requester`
and `ctx.catalogue(scope)`; without them completion is refused. Async resolver values
are refused cleanly for this synchronous host. Exact catalogue record shape remains
a proposal in `program/HOST_CONTEXT_CONTRACT.md`.

The host snapshot is commit `d9e2c8109e285650187430fb91d54e7c13923fa5` plus a
retained working-tree patch, not a clean released revision. Receipt and source hashes:
`evidence/host-semantic-receipt.json`. It has no catalogue resolver. Successful semantic
admission, atomic validation/persistence, concurrent revocation/drift and live matching
quality remain unqualified. Refusal probes do not establish these properties.

## Verification

Pure checks:

```sh
python -m pytest omegamatch/tests -q
```

Explicit current host refusal probes (disposable data, fake supervisor, in-process
ASGI, no listener or provider calls):

```sh
PATH=<swipl-patched>/bin:$PATH \
PETTA_PATH=$PETTA_PATH \
PYTHONPATH=<host-hook candidate checkout of omegahive>:. \
python -m pytest omegamatch/tests/host_semantic_probes.py -q
```

`examples/reuse.metta` retains four literal offline pattern checks. Earlier transport
probes at `d7dc7dc` reproduced schema-only evidence promotion; they qualify transport,
not semantic admission. Their module identities are invented transport fixtures,
not the native blueprint. Retained receipts distinguish these stages.

The companion now admits three offline result kinds: proposed typed needs,
reuse alerts and scoped no-candidate results. Host derivations for all three remain
proposed until the catalogue contract lands. Host owns catalogue generation, scoring, authenticated scope,
evidence custody, transactions and acceptance routing. Requester/Planner accepts
outputs separately from schema and semantic validation.

## Lifecycle correction prepared

Committed host `4fcd9c9` reproduces cancellation/reopening overwritten during
semantic validation. an owner workspace record (not included) fixes final
persistence in an isolated source copy, returning 409 when the validated lifecycle
changed. Five focused probes and twelve existing host schema/review tests pass.
That patch is superseded by Opus's own adopted correction (`be6e0e5`),
independently verified at committed `eafd789`. Opus reports deployment; this
session has verified source behavior, not current runtime deployment. This closes only the
result/goal-state write race, not the pending catalogue transaction boundary.
Details: an owner workspace record (not included).

## All result kinds prepared

`typed-need.schema.json`, `no-candidate.schema.json` and `match-result.schema.json`
use the host's supported schema subset. The composite schema bounds the union of
fields; the subset has no conditional schemas, so it **must** be paired with
`validate: program:omegamatch`. The companion enforces the exact field set and
semantics for the selected kind. Schema-only shape validity is insufficient.

Typed needs preserve normalized source constraints/preferences/references and
source unknowns. They use only supplied visible operation names and remain proposed,
with requester acceptance pending. This proves preservation, not interpretation quality.
No-candidate results require a host-derived zero-candidate search receipt, exact
visible scope, search-completion flag and truncation reason. They never establish
global absence or grant permission to widen a search.

73 pure checks pass; receipt `evidence/result-kinds-receipt.json` binds this stage's
code, schemas and test output. Host context fields for these result kinds are
proposals, not fabricated catalogue data. The lifecycle fix is verified in committed platform source; no production
catalogue or live mind has been claimed.

## Adopted host and native evidence reasoning

Committed host `eafd78913f762030f9a8c9304c4c29efc71f62e9` passes **21 selected checks**:
Match semantic refusal probes, cancellation/reopening interleavings, and existing
host result-schema/review tests. The lifecycle finding is resolved in that source.
`evidence/adopted-host-receipt.json` records the pin, file hashes and selected output.

`examples/evidence_reasoning.metta` adds six native literal checks: supported
conditions, preserved support plus contradiction, missing-fact unknowns, changed-tree
unknowns, offers absent from the visible projection and an unrelated capability query.
All six pass on local PeTTa with patched SWI, no reported errors. This is an inspected
synthetic relational query example, not a full paraconsistent reasoner, visibility
proof, probability model or host matching/scoring replacement. Condition reports
provide explanations only. Receipt: `evidence/evidence-reasoning-receipt.json`.

Next dependency remains Opus's catalogue/requester-viewer contract and connection-
only service gate. Successful host admission, transactional catalogue consistency,
real-provider reasoning and registration are not qualified by these receipts.


## Catalogue draft reconciliation

Opus adopted service candidate `433c699` and published draft 1. Follow-up candidate
`9cc04da` corrects missing R13 provider filtering with a non-admin requester-owner
Viewer; **12** selected host checks pass. Adoption/deployment of this follow-up is
pending. The adapter now calls catalogue with the host-derived requester swarm
string. Draft offer projections cannot supply semantic witnesses or search receipts
and refuse explicitly. **77** pure checks pass. Details:
an owner workspace record (not included).


## Request-bound partial host catalogue candidate

`match/catalogue-scope` tip `1cddcf1` includes R13 correction and synchronous
request-bound host catalogue plumbing. **32 selected checks passed** (13 service/
connection/collaboration,18 existing result/review/refusal,1 actual Match hook).
The actual hook refuses incomplete semantic context and preserves claimed status
and failed attempt. Service-only advertised offers; other families unavailable,
truncated=true. Candidate review/integration/deployment pending. Details:
an owner workspace record (not included).


## Assigned role projection candidate

Candidate tip `9ffecdc` adds advertised role media/mandate offers for visible,
non-deleted assigned agents. Both agent and swarm visibility are required.
Role source digests include mandate revision; hidden role edits do not alter
requester digests. Skills/programs/code remain unavailable.14 selected host checks
and1 actual Match hook probe pass;7 focused checks passed after the final test edit.
Review/integration pending; semantic admission still closed. See
an owner workspace record (not included).


## Catalogue HTTP endpoint candidate

Prior scope/context/role commits were adopted in platform source as351acf9,
09cdecf and7e1cedf. New candidatebb601cb adds /api/match/catalogue with
agent swarm binding and person owner/admin scope selection. Shared requester
visibility cannot borrow its owner's wider view.12 final catalogue/visibility
checks pass; endpoint adoption/runtime deployment remain pending. Details:
an owner workspace record (not included).


## Program action projection candidate and cleanup

Candidate733f2e6 adds advertised action identifiers from enabled, digest-bound,
activated apps in visible swarms; it supplies no attachment/execution authority.
10 focused checks plus1 actual host refusal probe pass. Skills/code/witnesses remain
unavailable. Own merged/obsolete snapshots were reduced to recoverable source
archives, recorded in an owner workspace record (not included);
historical expanded paths require extraction. One working candidate checkout remains.
See an owner workspace record (not included).

## Catalogue to Hyperon data bridge

catalogue_atoms.py projects supplied metadata into literal MeTTa facts with
reversible encoded string symbols. Scope/digest, source unavailability, coverage,
visibility, tier/evidence refs and unknowns survive without executable metadata.
83 pure checks and4 native literal query checks pass on a synthetic catalogue.
No evaluator/rules, authority, ranking or performance inference is added.
See an owner workspace record (not included).

## Literal skill metadata candidate

skill_metadata.py reads a bounded literal card subset without importing or
executing MeTTa. Arguments/topics/risks/effects/cards and topic-level SkillHelp
carry source digests.89 pure tests pass. Full signatures, cross-file joins,
runtime provider binding, visibility and policy remain pending; this subset is
not wired into the host catalogue. No new clone or dependencies created.
See an owner workspace record (not included).


## Module skill metadata joins

project_module_metadata joins host-selected literal source files and records exact
module Provides declarations plus syntactic rule-head call shapes. Bodies are
excluded; source digests, variants and topic-level help retained.93 pure checks
pass. Runtime source-set derivation, provider/visibility/policy binding and full
signature qualification remain pending; no host integration claimed.
See an owner workspace record (not included).


## Loader-selection metadata boundary

project_loader_selection retains direct configured imports in order without
resolving/loading sources. Unsupported/dynamic imports remain explicit gaps.
96 pure tests pass. Actual-agent loader selection/import-success receipts and
requester/policy binding remain host dependencies. See
an owner workspace record (not included).

## Further Hyperon runtime theory

HYPERON_RUNTIME_THEORY.md expands independent capability dimensions, exact-context
and generation-bound evidence, revocation, reflection and admission boundaries.
runtime_dimensions.metta passes6 native synthetic relational checks; this is
explanation-level qualification, not live readiness, authorization or acceptance.


## Contextual readiness explanation helper

readiness.py reports six independent dimensions over exact host-supplied context.
Conflicts and evidence origin retained; duplicate references do not vote; other
contexts omitted. All-positive reports still confer no acceptance or execution.
109 pure tests pass. Helper remains synthetic/unintegrated pending host runtime
and evidence contracts. See an owner workspace record (not included).

## S4 library revision 2

Manifest0.1.1-candidate adds direct per-skill help and top-level explicit typed
signature declarations, distinct from topic help/syntactic call shapes. Conflicts
are preserved; no runtime type validation inferred.113 L0 pure checks pass.
Platform owns S4; envelope adaptation waits for OmegaAtom's authoritative schema.
See an owner workspace record (not included).
