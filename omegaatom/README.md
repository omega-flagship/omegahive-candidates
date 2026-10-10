# OmegaAtom

Pure, independently importable evidence-envelope validation and offline maintenance planning for OmegaDot. Implemented to Opus's accepted design; L0 candidate only.

```sh
PYTHONPATH=. python -B -m pytest omegaatom/tests -q -p no:cacheprovider
```

The public library also exports `stage_append`, `lineage_delta`, exact evidence-reference parsing/formatting and revision eligibility. All work over supplied data and return detached results. No interpreter, scheduler, networking, grant issuance or accepted-space mutation occurs. See an owner workspace record (not included) for schema, scope and host responsibilities.

The owner-only `omegaatom.qualify` receipt command is not included in this repository. The E1 component helper uses Bench's offline scorer and a bounded fresh Python process for data reconstruction. This is L0 component preparation, not E1 host or cross-swarm acceptance.

`project` prepares a complete lineage group, including withdrawal controls, from an already authorized snapshot. The host owns grants and pagination. `bound_worker` prepares and finalizes maintenance proposals through the existing HTTP bound-request contract; it grants no mutation authority.

The separate L1 route checks use real ASGI and PeTTa with synthetic data and a fake supervisor:

```sh
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=<omegahive checkout>:. python -B -m pytest omegaatom/host_tests -q -p no:cacheprovider
```

See an owner workspace record (not included) for the narrow qualification and remaining limits.

`project_pages` packs authorized query roots into complete lineage groups within the draft's 200-record page bound. It returns validated snapshots and completion flags; the host adds transport cursors and checks access on every read.

`python -B -m omegaatom.conformance` emits eight synthetic portable S1/S1b staging vectors for the platform's host test rig. Expected digests, deltas and sidecars are component references; host authentication, atomic storage and replay need separate qualification.
