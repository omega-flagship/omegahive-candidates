import json
import os
import subprocess
import sys
from pathlib import Path
from omegaatom.e1 import qualify, fixture, reconstruct
from omegaatom.envelope import lineage_state


def test_atom_e1_component_uses_bench_oracle_and_reconstructs_data():
    import pytest
    pytest.importorskip('omegabench.correction', reason='needs the standalone omegabench package with correction.py')
    result = qualify()
    assert result["level"] == "L0"
    assert result["bench_fixture_score"]["score"] == 1
    assert result["bench_fixture_score"]["capture_authentication"] == "unverified"
    assert len(result["withdrawal_delta"]["newly_stale"]) == 5
    assert len(result["restore_delta"]["newly_eligible"]) == 6


def test_fresh_process_reconstructs_exact_state():
    snapshot, _, _ = fixture()
    assert reconstruct(snapshot)["states"] == lineage_state(snapshot)


def test_reconstruction_refuses_executable_input():
    root = Path(__file__).resolve().parents[2]
    result = subprocess.run([sys.executable, "-B", "-m", "omegaatom.reconstruct"],
                            input='!(import! &self "bad")', text=True, capture_output=True, cwd=root,
                            env={"PYTHONPATH": str(root), "PYTHONDONTWRITEBYTECODE": "1"}, timeout=10)
    assert result.returncode == 2
    assert result.stdout == ""
    assert "schema_invalid" in result.stderr
