# Status: OmegaHive candidates

Tier: Open (Apache-2.0). Checked on 2026-10-10. Nothing here is installed in a host or deployed.

## Test counts

in a fresh Python 3.12.13 venv (fastapi 0.142.2, httpx 0.28.1, uvicorn 0.54.0, pytest 9.1.1, pillow 12.3.0, jsonschema 4.26.0, janus-swi 1.5.3), against the omegahive prep checkout at `7b1ce3f` (with the platform lane's uncommitted handover edits at the time), PeTTa `ae66fa8`, SWI-Prolog 10.1.14. Each line is `python -m pytest -q <path>` from the repository root with
`PYTHONPATH=.:<omegahive checkout>:$PETTA_PATH/python`.

| Path | Maturity | Result |
|---|---|---|
| `omegaflow/tests` | slice 1 | **45 passed** |
| `omegamatch/tests` | L0 candidate | **119 passed** |
| `omegaalignment/tests` | L0 candidate | **80 passed, 18 skipped** |
| `omegareason/tests` | slice 1 | **20 passed** |
| `omegalearn/tests` | slice 1 | **26 passed, 3 skipped** (with the omegaplanner repository also on `PYTHONPATH`: 33 passed, 2 skipped) |
| `omegaatom/tests` | L0 candidate | **116 passed, 1 skipped** |
| `omegaatom/host_tests` | L0 candidate | **5 passed** |
| `omegagraft/tests` | L0 candidate | **23 passed** (7 subtests) |
| `omegachill/tests` | L0 candidate | **8 passed** |
| `hiveconnect/tests` | plan | **41 passed** |

Total: 483 passed, 22 skipped, 0 failed.

Contract checks (`python -m hive.programs_check <folder>`): `omegamatch/program` and `omegalearn/program`
are **COMPATIBLE** with program contract 0.1.

## Skips and limits

- `omegaalignment/tests/test_connection_gate_candidate.py` (18) targets the superseded connection-only host
  candidate; it skips unless `OMEGAALIGNMENT_HOST_CANDIDATE=1`. Against the current host 17 of them fail, as
  expected; `test_integrated_connection_gate.py` covers the merged behaviour and passes.
- `omegalearn` (3) and `omegaatom/tests/test_e1.py` (1) need omegaplanner and a newer standalone OmegaBench
  (`omegabench.planner_adapter`, `omegabench.correction`) than the one in omegahive.
- Host probe files that pytest does not collect by default (`omegamatch/tests/host_*_probes.py`,
  `omegalearn/tests/host_artifact_probes.py`, `omegalearn/tests/attachment_scope_probe.py`,
  `omegaflow/tests/host_acceptance.py`) need host candidates and were not run.
- `omegaflow` browser acceptance scripts and several owner receipt runners (`qualify*.py`) are not included
  (see `CHANGELOG.md`); module READMEs still mention the counts they recorded.
- `omegaalignment`'s native MeTTa qualification is not included: it depended on a private donor body.
- Module READMEs cite owner workspace records (not included) and platform commits from before the handover.
