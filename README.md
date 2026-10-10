> **Legacy / reference.** Early candidate modules from earlier sessions. They are outdated compared with the current OmegaHive platform and apps; treat them as ideas and starting points, not current design.

# OmegaHive candidates

Early candidate modules for OmegaHive. Each folder is a small, independently importable Python package that was
built and checked against the OmegaHive host, but **none of them is installed in the host or deployed**. They are
kept together so the ideas, contracts and tests are not lost, and so each one can be promoted (into omegahive or
into its own repository) or retired on its merits.

Tier: **Open (Apache-2.0)**. See `LICENSE`.

For the history of these and other early experiments, and how they fed the platform, see
`docs/EARLIER_EXPERIMENTS.md` in the omegahive repository.

## Modules

Maturity: **L0 candidate** = offline library or configuration with synthetic tests, no host integration;
**slice 1** = first working slice, exercised against a disposable real host; **plan** = mainly design and
research, with at most an offline client.

| Folder | What it is | Maturity |
|---|---|---|
| `omegaflow/` | Typed object-and-link flow model (`omegaflow/1`), lossless JSON/MeTTa encoding, structural checks, admission preflight and a local authoring canvas. The host-side Flow studio grew out of it and lives in omegahive (`hive/flow_ir`, `hive/flow_studio`). | slice 1 |
| `omegamatch/` | Offernet matching mind over the hive's capability catalogue: needs interpretation, fit explanations, reuse alerts; result schemas and a semantic companion program. Recommends only. | L0 candidate |
| `omegaalignment/` | Proposed Alignment swarm (Drift, Flourishing, Coordinator) as configuration, plus an L0 correction-to-learning library and a connection-only host patch candidate. | L0 candidate |
| `omegareason/` | Bounded owner-local NAL/PLN reasoning over finite JSON jobs, an OmegaAtom bridge, a bound-request worker and withdrawal-safe query projections. | slice 1 |
| `omegalearn/` | LearningEvent intake, immutable improvement-package proposals, corrections, invalidation and checkpoint recovery; a learned-prerequisite skill and a Bench adapter. | slice 1 |
| `omegaatom/` | Evidence-envelope validation, lineage and withdrawal projection, offline maintenance planning; shared by most of the other modules. | L0 candidate |
| `omegagraft/` | Module-manifest validation, binding-graph analysis, unplug blast radius and swap proposals. | L0 candidate |
| `omegachill/` | Advisory monitor: loop/stall and spam suggestions, memory-pressure findings, a notification gate. Proposes only. | L0 candidate |
| `hiveconnect/` | Integration plan for application adapters and connections (research, catalog, contract, roadmap, conformance cases) with a read-only offline client draft. | plan |

Each folder's own `README.md` holds the owner's notes for that module. Those notes cite owner workspace records
and platform commits from before the handover; the records are not included and the commits are not in the
published omegahive history.

## How they relate to omegahive

- The host is the omegahive repository (`hive` package). Modules that test against a host use its in-process
  test client and a fake supervisor; nothing starts a listener, a model or a real mind.
- `omegamatch/program/` and `omegalearn/program/` are Dot programs in the shape `hive/PROGRAMS.md` (omegahive)
  describes; they are not mounted anywhere.
- Patches in `omegaalignment/host-candidate/` are against older omegahive commits and have not been merged.
- Dependencies between modules: every module except `omegaflow` imports `omegaatom`; `omegaalignment` also
  imports `omegalearn`. Run everything from this repository's root.
- Optional siblings: some `omegalearn` tests use the omegaplanner repository, and some `omegalearn` and
  `omegaatom` tests use a newer standalone OmegaBench than the one in omegahive; they skip when those are absent.

## Requirements

- Python 3.12 (checked with 3.12.13), with omegahive's `hive/requirements.txt` (checked with fastapi 0.142.2,
  httpx 0.28.1, uvicorn 0.54.0, pytest 9.1.1, janus-swi 1.5.3).
- An omegahive checkout.
- `PETTA_PATH` pointing at a PeTTa checkout (checked with `ae66fa8`) and SWI-Prolog 10.1.14 on `PATH`, for
  `omegareason` and the host tests.

## Test

From this repository's root, one module at a time (several modules have a `tests/test_program.py`, so do not
collect them in one run):

```sh
export PETTA_PATH=<PeTTa checkout>
export PYTHONPATH=.:<omegahive checkout>:$PETTA_PATH/python
for m in omegaflow omegamatch omegaalignment omegareason omegalearn omegaatom omegagraft omegachill hiveconnect; do
  python -m pytest -q $m/tests
done
python -m pytest -q omegaatom/host_tests
```

Current counts are in `STATUS.md`.

## Licence

Apache-2.0 (`LICENSE`).
