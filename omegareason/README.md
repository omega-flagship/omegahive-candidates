# OmegaReason: bounded owner-local reasoning library

Implements the first slice requested in an owner workspace record (not included). Library-first; no loader, registry, coordinator, service or live activation is added.

## What runs

`run(job, arm)` accepts finite JSON data, never client MeTTa. Arms are `nal`, `pln`, `combined`, and `typed-memory`. Each native engine runs in its own bounded subprocess and interpreter. The native interpreter contains named input, prior and result spaces; NAL and PLN are never imported together.

- NAL consumes the existing `$PETTA_PATH/lib/lib_nars.metta`, invoking `NARS.Derive` with one selection per pair, queues 16/64. It preserves native evidence stamps. This is a pair pass, not a full NARS controller.
- PLN consumes `lib_pln.metta` (omegahive) and invokes `|~` (the reducer behind pln-step). Its constant STV stub is replaced in memory, under an exact-source guard, with lookup in the job's prior space. Missing priors refuse the pair. Priors use supplied counts (`positive/total`, confidence `total/(total+1)`); prior evidence ids join the premise list.
- Combined returns both outputs labelled; it does not fuse their truth values or vote.
- Only explicit `isa` → native `-->` / `Inheritance` translation is supported. Native outputs outside that fragment are refused, not relabelled.

Every result includes native statement/TV/stamp and D2-shaped Source, Status, Scope and Premises sidecars. Rule version binds both the library and adapter hashes. Premises identify direct inputs, whose own premise lists preserve ancestry; no engine supplies a hidden exact internal rule trace, so the recorded rule is the API (`nars-derive` or `pln-step`). Result source digest binds result material. These are **proposals** until admitted by OmegaAtom's validator.

## Contracts and limits

The authoritative envelope and validator belong to OmegaAtom. The initial low-level adapter uses the platform's D2 draft. `atom_bridge.infer_snapshot` now consumes the landed `omegaatom.envelope` validator, exact evidence ids, inert sidecars and canonical `lineage_state`. Use that bridge for canonical snapshot proposals; the low-level draft atoms are not the admission path. The JSON job is a local transport, not a rival evidence envelope.

`stale_ids` is an offline input-eligibility/reference helper, not the canonical maintenance planner. It follows premise dependencies to suppress withdrawn input and descendants. OmegaAtom owns production propagation; the platform owns host retraction and writes. The qualification fixture persists two JSON snapshots and reconstructs the native spaces in fresh processes; it does not prove a host archive or private data restore.

Limits: 24 input premises, 32 KiB encoded job, 20 seconds per native worker, one native selection per pair. This is trusted installed native code, not an OS sandbox for arbitrary user programs. Workers use no Hive, model, network or private corpus. `effects=[]` in the manifest describes effects; it grants nothing.

## Run

```sh
# omegareason.qualify (owner-workspace receipt runner) is not included in this repository
python -m omegareason.adapter combined < omegareason/example-job.json
```

The qualification covers independent and overlapping evidence, prior lineage, labelled combined output, two local snapshots, exact descendant invalidation, correction with a new evidence id, unrelated retention, fresh-process reconstruction and executable-input refusal. Results: an owner workspace record (not included). L0 only; E1's host and multi-owner loop, equal-cost synergy and E2's creative transfer remain unproven.

Donor separation pattern: Symega `docs/reasoning.md` and the pln_reasoner organ at commit `9ab07f4825956d060b9d8200ff4ee4f50bfbcd5c`. No Symega state or private records are imported. The existing native library implementations are consumed unchanged on disk.

## Canonical Atom bridge

`infer_snapshot(snapshot, arm)` validates the complete owner snapshot, filters Atom's retracted/stale records, consumes known Inheritance and known TermCounts statements, runs bounded engines, and returns a detached snapshot proposal validated by Atom. Unknown term counts are refused. Direct premise ids and their canonical stamp union are preserved, including prior evidence; NARS-native and wrapper-generated stamps remain labelled in the native report. Existing archived evidence and retraction events are retained. This pure bridge authenticates no issuer and grants no write authority.

```sh
OMEGAREASON_RECEIPT_DIR=<scratch dir> python -m omegareason.qualify_bridge
```

Bridge receipt: an owner workspace record (not included). It covers all arms, real canonical validation, exact staleness, archival retention, corrected evidence, prior stamps, unknown count refusal, and sampled fresh-process restoration/idempotence. It does not qualify S1/S1b or a live request. The low-level reference eligibility helper remains only for its standalone L0 fixture; the canonical path delegates lineage to Atom.

## Existing bound-request consumer (L1)

`bound_worker.prepare(goal, exhibit, agent_id, arm)` consumes an already claimed host goal and its complete exhibit. It reuses host binding/exhibit digest functions, verifies the envelope revision and digest, then runs the canonical Atom bridge. Each new result receives truthless `AdmissionState(... proposed)` and `Restriction(... proposal-only)` statement records with premise lineage, so status and restrictions remain reason-overable data. These are ordinary D2 statement atoms, not new envelope fields or grants.

`bound_worker.finalize(prepared, freshly_read_goal, current_owner_snapshot)` checks claim, assignment, lease/deadline, unchanged binding and owner revision/digest immediately before returning the existing goal-result payload. The consuming app must recheck the owner snapshot through its host `validate_result` callback as well; this closes the worker-side check-to-submit gap. Transport completion does not mean evidence adoption or review approval. A cancelled/expired request must stop; use the host's existing cancel-ack route. Expiry notification and acknowledgment eligibility are established by the existing host reconciler, not by this library.

```sh
# omegareason.qualify_bound (owner-workspace receipt runner) is not included in this repository
```

Receipt: an owner workspace record (not included). Six cases pass on the real disposable ASGI host and installed PeTTa with a fake supervisor: bound derivation and identical retry; cancellation/revocation/late-result refusal/ack; owner revision correction refused at worker and host; forged or partial exhibits and wrong worker refused; deadline and lease expiry; executable snapshot refused even with consistent transport hashes. No model or agent process is started, no usage is recorded, and synthetic host state is deleted after qualification.

This is the Reason consumer boundary for the existing Scientist route, not a service deployment, new scheduler or request API. S1/S1b evidence publication and retraction, S2 cross-swarm grants, full E1, matched-budget Bench synergy and E2 transfer remain separate. Source/role/grant authentication remains the host's responsibility. Any real deployment must resolve platform ownership and the restart hold first.

## Seam r2 preparation and independent Review (L0 / L1)

The accepted shared format is OmegaAtom envelope 0.1. This package consumes its validator and its canonical `format_evidence_ref` / `parse_evidence_ref` functions unchanged.

`publication_plan.prepare_batch(base, candidate)` prepares an untrusted batch proposal over an unchanged frozen base. Each fact gets a deterministic preparation digest and retry key; unknown facts omit `f` and `c`. It never issues a host id or stamp. `local_ref` is only a correlation label for a working-space result. The host must fetch its own admitted premise closure, authenticate custody and publication scope, allocate ids/stamps, rebind local references and validate/commit the complete batch atomically. The prepared digest is not the final host admission digest. Durable idempotency conflict checking and restart replay remain host work. This plan is not yet an S1 wire payload, because its preallocation/request conversion is still unfrozen.

`review_export.seal(snapshot)` creates bounded exact JSON artifact bytes for a Reason proposal; `open_revision(revision, subject)` consumes an authorized retained-revision read and checks both host artifact bytes/digest and the canonical Atom snapshot, evidence refs and lineage state. `review_request` builds the existing typed review-request payload with one versioned `reason-lineage` mandate. No new grant or transport is introduced. Read access does not imply derive/share authority. Unknown truth stays absent.

The interim r2.5 route is qualified across two real synthetic swarms in a disposable host. A retained revision remains readable with a newer revision present, while the newer revision is refused. A REAL reviewer-complete call records an unresolved, authority-none receipt and closes reads; request cancellation closes reads and refuses a late review. These are transport/lifecycle checks, not scientific independent validation or named-person adoption. Expected digest is checked locally after the existing authorized host read; general S2/S3 host-enforced expected-digest read admission remains unimplemented.

```sh
# omegareason.qualify_r2 (owner-workspace receipt runner) is not included in this repository
```

Receipt: an owner workspace record (not included): nine L1 cases and four L0 cases passed, source hashes unchanged. Includes requalification of the original six bound-route cases against the current accepted validator and host source. No listener, actual mind start, model call, S1 publication or shared commons mutation. All synthetic host state is disposable.

Personal/health content remains owner-local and never enters shared/app S1 publication. This library prepares data; the host must independently enforce scope, custody and privacy. Its pure plan grants no publish/derive/share permission.

## Withdrawal-safe query projections (r2.6, L0)

The platform accepted Reason's bound-route and retained-review paths in an owner workspace record (not included); S1 publication still waits for host issuance. r2.6 accepts OmegaAtom's withdrawal-aware projection as the reference.

`query_projection.project_and_reason(snapshot, roots, arm, record_limit)` calls OmegaAtom's **existing** `project_pages` before any inference. Pages retain premises, withdrawal controls, and controls on controls. If a complete group exceeds the bound, nothing is inferred from earlier groups. `join_pages` joins pages only within one owner/scope/revision, requiring final-result and complete-closure markers. Repeated ancestor records must match byte-equivalent data; conflicting evidence, mixed scopes/revisions and partial result sequences refuse. Joined data passes Atom validation, then the existing bounded native adapters reason over it.

This is an owner-local/reference consumer, not an implemented S3 query or cursor/grant client. A complete-closure marker is a host assertion: it cannot authenticate an untrusted sender or independently detect withheld history. The host must supply authorized complete groups and recheck grants/cursors; this library does not grant read, derive, share or publication authority. Control restoration changes lineage eligibility, never privacy permission.

```sh
# omegareason.qualify_r26 (owner-workspace receipt runner) is not included in this repository
```

Twenty checks pass: 11 L0 and 9 disposable-host L1. Seven new projection cases cover cross-page inference, withdrawal suppression, unrelated retention, retraction-of-retraction, overflow before computation, mixed/partial/conflicting pages, and fresh-process preservation. Receipt: an owner workspace record (not included); source pins unchanged. The original r2 qualification runner remains fixed to its own 13-case slice.
