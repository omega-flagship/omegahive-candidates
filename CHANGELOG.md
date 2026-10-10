# Changelog

## Handover (2026-10-10)

New repository for the private SingularityNET handover, collecting nine early candidate modules copied from the
owner's workspace: omegaflow, omegamatch, omegaalignment, omegareason, omegalearn, omegaatom, omegagraft,
omegachill and hiveconnect. No module versions changed.

- Owner-workspace paths, links and names in the module notes replaced with neutral wording.
- Tests made portable: the host is found through the `hive` package and PeTTa through `PETTA_PATH`
  (`omegamatch/tests/test_schema.py`, `omegareason/adapter.py`, `omegareason/tests/test_bound_route.py`,
  `omegalearn/tests/host_artifact_probes.py`, `omegaatom/host_tests/test_bound_maintenance.py`).
- Two synthetic fixtures the `omegalearn` worker tests read were copied into `omegalearn/tests/fixtures/`.
- Tests that need sibling packages that are not here (omegaplanner, a newer standalone OmegaBench) skip when they
  are absent; `omegaalignment/tests/test_connection_gate_candidate.py` skips unless
  `OMEGAALIGNMENT_HOST_CANDIDATE=1` (superseded host candidate).
- `omegareason.qualify_bridge` writes its receipt to `OMEGAREASON_RECEIPT_DIR`.
- `hiveconnect/hive_inventory.json`: the entry for a private app's manifest removed.
- Left out (owner-workspace receipt runners and private-donor material): `omegareason/qualify.py`,
  `qualify_bound.py`, `qualify_r2.py`, `qualify_r26.py`; `omegaatom/qualify.py`; `omegaalignment/native/qualify*.py`
  and `omegaalignment/native/candidate/`; `omegaflow/editor/*acceptance.mjs` and `omegaflow/tests/browser_fixture.py`.
- Added README, STATUS, CONTRIBUTING, CODE_OF_CONDUCT, SECURITY, LICENSE, this changelog and
  `.github/repo-description.txt`.
