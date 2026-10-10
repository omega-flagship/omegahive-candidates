import copy
import json
import unittest

from hiveconnect.client import ClientError
from hiveconnect.draft_client import DraftReadClient, HiveRemoteError, READ_SCHEMAS
from omegaatom import validate, lineage_state, parse_evidence_ref, format_evidence_ref, project_pages


class DraftFixture:
    def __init__(self):
        self.calls = []
        self.schema = "s3-r1"
        self.version = "0.2.0"
        self.transform = lambda r: r
        self.data = {"id": "fixture-member"}
        self.schemas = copy.deepcopy(READ_SCHEMAS)

    def __call__(self, wire):
        request = json.loads(wire)
        self.calls.append(request)
        if request["method"] == "initialize":
            result = {"protocolVersion": "2025-06-18", "serverInfo": {"name": "omegahive", "version": self.version}}
        elif request["method"] == "tools/list":
            result = {"_meta": {"x-hive-schema": self.schema}, "tools": [{"name": k, "inputSchema": v} for k, v in self.schemas.items()]}
        else:
            result = {"structuredContent": self.data, "content": [{"type": "text", "text": "Synthetic result."}]}
        return json.dumps(self.transform({"jsonrpc": "2.0", "id": request["id"], "result": result})).encode()


def atom_fixture():
    return {"version": "0.1", "owner": "fixture-owner", "scope": "fixture-swarm", "revision": 1,
            "records": [{"id": ["ev", "fixture-owner", 1], "statement": ["Observation", "sample"],
                         "source": {"owner": "fixture-owner", "subject": "sample", "revision": 1, "digest": "a" * 64},
                         "status": "observed", "scope": "fixture-swarm", "stamp": [["ev", "fixture-owner", 1]],
                         "unknown": True}]}


class DraftChecks(unittest.TestCase):
    def setUp(self):
        self.transport = DraftFixture()
        self.client = DraftReadClient(self.transport, expected_server_version="0.2.0",
                                      expected_mind_id="fixture-member", atom_validator=validate)

    def ready(self):
        self.client.initialize()

    def inventory(self, revision="sha256:" + "b" * 64, status="callable"):
        return {"mind_id": "fixture-member", "inventory_revision": revision, "loaded_at": None,
                "snapshot_at": "2026-10-04T16:40:00Z", "availability": "no-boot-receipt" if revision is None else "available", "modules": [], "skills": [{"id": "sample-read", "status": status, "policy": {"decision": "deny", "reason": "fixture"}}],
                "provider": {"model": "mock/echo", "resolved_model": None, "payer_kind": "fixture", "budget_route": []}}

    def test_structured_identity(self):
        self.ready()
        self.assertEqual(self.client.call("hive_whoami", {}), {"id": "fixture-member"})

    def test_member_mismatch(self):
        self.ready()
        self.transport.data = {"id": "other-member"}
        with self.assertRaisesRegex(ClientError, "member_identity_mismatch"):
            self.client.call("hive_whoami", {})

    def test_version_and_schema_mismatch(self):
        self.transport.version = "changed"
        with self.assertRaisesRegex(ClientError, "server_version_mismatch"):
            self.ready()
        self.transport.version = "0.2.0"
        self.transport.schema = "s3-r2"
        with self.assertRaisesRegex(ClientError, "draft_schema_mismatch"):
            self.ready()

    def test_input_schema_mismatch(self):
        self.transport.schemas["hive_goal_get"]["required"] = []
        with self.assertRaisesRegex(ClientError, "draft_input_schema_mismatch"):
            self.ready()

    def test_summary_not_used_as_data(self):
        self.ready()
        self.transport.data = {"rows": [], "unknown": True}
        def changed(r):
            r["result"]["content"][0]["text"] = '{"unknown": false, "truth": 1}'
            return r
        self.transport.transform = changed
        self.assertEqual(self.client.call("hive_evidence_query", {"pattern": "sample"}), {"rows": [], "unknown": True})

    def test_legacy_payload_not_silently_accepted(self):
        self.ready()
        def legacy(r):
            del r["result"]["structuredContent"]
            return r
        self.transport.transform = legacy
        with self.assertRaisesRegex(ClientError, "structured_content_required"):
            self.client.call("hive_whoami", {})

    def test_hive_error_codes_preserved_without_messages(self):
        self.ready()
        for code in ("not_assigned", "binding_mismatch", "deadline_passed", "share_closed", "stale_revision",
                     "digest_mismatch", "schema_invalid", "spend_limit", "grant_closed"):
            self.transport.transform = lambda r, code=code: {"jsonrpc": "2.0", "id": r["id"],
                "error": {"code": -32000, "message": "synthetic-sensitive-payload", "data": {"code": code, "http_status": 403}}}
            with self.assertRaises(HiveRemoteError) as raised:
                self.client.call("hive_whoami", {})
            self.assertEqual(raised.exception.code, code)
            self.assertNotIn("synthetic-sensitive", str(raised.exception))

    def test_unknown_error_not_invented(self):
        self.ready()
        self.transport.transform = lambda r: {"jsonrpc": "2.0", "id": r["id"], "error": {"data": {"code": "secret-code"}}}
        with self.assertRaisesRegex(HiveRemoteError, "^unclassified_remote_error$"):
            self.client.call("hive_whoami", {})

    def test_callable_and_denied_remain_distinct(self):
        self.ready()
        self.transport.data = self.inventory()
        result = self.client.call("hive_capabilities", {})
        self.assertEqual(result["skills"][0]["status"], "callable")
        self.assertEqual(result["skills"][0]["policy"]["decision"], "deny")

    def test_missing_boot_receipt_not_inferred(self):
        self.ready()
        self.transport.data = self.inventory(revision=None)
        with self.assertRaisesRegex(ClientError, "missing_boot_receipt"):
            self.client.call("hive_capabilities", {})
        self.transport.data = self.inventory(revision=None, status="unknown")
        self.assertEqual(self.client.call("hive_capabilities", {})["skills"][0]["status"], "unknown")

    def test_foreign_inventory_refused(self):
        self.ready()
        self.transport.data = self.inventory()
        self.transport.data["mind_id"] = "other-member"
        with self.assertRaisesRegex(ClientError, "inventory_identity_mismatch"):
            self.client.call("hive_capabilities", {})

    def test_no_mutations_or_unfrozen_scope_shape(self):
        self.ready()
        n = len(self.transport.calls)
        for name in ("hive_goal_result", "hive_goal_heartbeat", "hive_goal_cancel_ack", "hive_request", "hive_evidence_publish"):
            with self.assertRaisesRegex(ClientError, "readonly_tool_refused"):
                self.client.call(name, {})
        with self.assertRaisesRegex(ClientError, "draft_arguments_refused"):
            self.client.call("hive_evidence_query", {"pattern": "x", "scopes": ["untagged-scope"]})
        self.assertEqual(len(self.transport.calls), n)

    def test_authoritative_atom_validator_unknown_and_executable(self):
        data = atom_fixture()
        validated = self.client.validate_atom_snapshot(data)
        self.assertNotIn("truth", validated["records"][0])
        data["records"][0]["truth"] = ["stv", 1, 0.5]
        with self.assertRaisesRegex(ClientError, "atom_envelope_refused"):
            self.client.validate_atom_snapshot(data)
        data = atom_fixture()
        data["records"][0]["statement"] = ["py-call", "sample"]
        with self.assertRaisesRegex(ClientError, "atom_envelope_refused"):
            self.client.validate_atom_snapshot(data)

    def test_validator_is_required(self):
        self.client.atom_validator = None
        with self.assertRaisesRegex(ClientError, "atom_validator_required"):
            self.client.validate_atom_snapshot(atom_fixture())

    def test_tagged_scope_requests_preserve_host_filters(self):
        self.ready()
        self.transport.data = {"rows": []}
        scopes = [{"scope_id": "fixture-swarm"}, {"grant_id": "fixture-grant"}]
        self.client.call("hive_evidence_query", {"pattern": "sample", "scopes": scopes})
        self.assertEqual(self.transport.calls[-1]["params"]["arguments"]["scopes"], scopes)
        # Local shape acceptance makes no claim that the grant exists.

    def test_artifact_exact_binding_and_retained_revision(self):
        self.ready()
        digest = "sha256:" + "d" * 64
        self.transport.data = {"revision": 2, "latest_revision": 3, "digest": digest, "body": "synthetic retained body"}
        args = {"artifact_id": "fixture-artifact", "revision": 2, "expected_digest": digest}
        self.assertEqual(self.client.call("hive_artifact_read", args)["revision"], 2)
        self.transport.data["revision"] = 3
        with self.assertRaisesRegex(ClientError, "read_revision_mismatch"):
            self.client.call("hive_artifact_read", args)

    def test_digest_required_and_mismatch_content_not_returned(self):
        self.ready()
        n = len(self.transport.calls)
        with self.assertRaisesRegex(ClientError, "draft_arguments_refused"):
            self.client.call("hive_exhibit_read", {"share_id": "fixture-share"})
        self.assertEqual(len(self.transport.calls), n)
        self.transport.data = {"digest": "sha256:" + "c" * 64, "atoms": ["synthetic"]}
        with self.assertRaisesRegex(ClientError, "read_digest_mismatch"):
            self.client.call("hive_exhibit_read", {"share_id": "fixture-share", "expected_digest": "sha256:" + "d" * 64})

    def test_revocation_on_next_page_not_cached(self):
        self.ready()
        digest = "sha256:" + "d" * 64
        self.transport.data = {"digest": digest, "next_cursor": "opaque-fixture", "atoms": []}
        self.client.call("hive_exhibit_read", {"share_id": "fixture-share", "expected_digest": digest})
        self.transport.transform = lambda r: {"jsonrpc": "2.0", "id": r["id"], "error": {
            "code": -32000, "data": {"code": "grant_closed", "http_status": 410}}}
        with self.assertRaisesRegex(HiveRemoteError, "grant_closed"):
            self.client.call("hive_exhibit_read", {"share_id": "fixture-share", "expected_digest": digest, "cursor": "opaque-fixture"})
        self.assertEqual(len([c for c in self.transport.calls if c["method"] == "tools/call"]), 2)

    def test_complete_closure_can_be_incomplete_result(self):
        page = {"closure_complete": True, "result_complete": False, "next_cursor": "opaque-fixture", "end": False}
        result = self.client.validate_query_page(page, [atom_fixture()])
        self.assertFalse(result["page"]["result_complete"])
        self.assertNotIn("truth", result["snapshots"][0]["records"][0])
        page["closure_complete"] = False
        with self.assertRaisesRegex(ClientError, "query_closure_incomplete"):
            self.client.validate_query_page(page, [atom_fixture()])

    def test_terminal_cursor_consistency(self):
        page = {"closure_complete": True, "result_complete": True, "next_cursor": None, "end": True}
        self.client.validate_query_page(page, [])
        page["next_cursor"] = "cursor-after-end"
        with self.assertRaisesRegex(ClientError, "query_end_mismatch"):
            self.client.validate_query_page(page, [])

    def test_partial_lineage_refused_by_atom(self):
        snapshot = atom_fixture()
        row = snapshot["records"][0]
        row["status"] = "inferred"
        row["premises"] = [["ev", "missing-owner", 1]]
        row["rule"] = ["fixture-rule", "0.1"]
        with self.assertRaisesRegex(ClientError, "atom_envelope_refused"):
            self.client.validate_query_page({"closure_complete": True, "result_complete": True, "end": True, "next_cursor": None}, [snapshot])

    def test_canonical_refs_use_atom_api(self):
        value = ["ev", "org:fixture", 12]
        self.assertEqual(parse_evidence_ref(format_evidence_ref(value)), value)
        for bad in ("ev:fixture:01", "ev:fixture:0", "ev:%:1", "ev:fixture:$n"):
            with self.assertRaises(ValueError):
                parse_evidence_ref(bad)

    def test_retraction_of_retraction_is_not_permission(self):
        snapshot = atom_fixture()
        for n, target in ((2, 1), (3, 2)):
            snapshot["records"].append({"id": ["ev", "fixture-owner", n],
                "statement": ["Retracted", ["ev", "fixture-owner", target], "synthetic", "fixture-owner", n],
                "source": {"owner": "fixture-owner", "subject": f"fixture-control-{n}", "revision": n, "digest": str(n) * 64},
                "status": "observed", "scope": "fixture-swarm", "stamp": [["ev", "fixture-owner", n]],
                "unknown": False, "truth": ["stv", 1, 0.5]})
        checked = self.client.validate_atom_snapshot(snapshot)
        state = {tuple(row["id"]): row for row in lineage_state(checked)}
        self.assertFalse(state[("ev", "fixture-owner", 1)]["retracted"])
        self.assertTrue(state[("ev", "fixture-owner", 2)]["retracted"])
        self.assertNotIn("grant", checked)

    def test_inventory_wire_hash_and_snapshot_clock(self):
        self.ready()
        self.transport.data = self.inventory()
        self.transport.data["inventory_revision"] = "b" * 64
        with self.assertRaisesRegex(ClientError, "invalid_inventory_revision"):
            self.client.call("hive_capabilities", {})
        self.transport.data = self.inventory()
        del self.transport.data["snapshot_at"]
        with self.assertRaisesRegex(ClientError, "policy_snapshot_time_required"):
            self.client.call("hive_capabilities", {})


    def controlled_snapshot(self, restore=False):
        snapshot = atom_fixture()
        for n, target in ((2, 1), (3, 2)) if restore else ((2, 1),):
            snapshot["records"].append({"id": ["ev", "fixture-owner", n],
                "statement": ["Retracted", ["ev", "fixture-owner", target], "synthetic", "fixture-owner", n],
                "source": {"owner": "fixture-owner", "subject": f"control-{n}", "revision": n, "digest": str(n) * 64},
                "status": "observed", "scope": "fixture-swarm", "stamp": [["ev", "fixture-owner", n]],
                "unknown": False, "truth": ["stv", 1, 0.5]})
        return snapshot

    def test_r26_projection_preserves_withdrawal(self):
        pages = project_pages(self.controlled_snapshot(), [["ev", "fixture-owner", 1]])
        snapshot = pages[0]["snapshot"]
        self.assertEqual(len(snapshot["records"]), 2)
        self.assertTrue(lineage_state(snapshot)[0]["retracted"])
        checked = self.client.validate_query_page(
            {"closure_complete": True, "result_complete": True, "end": True, "next_cursor": None}, [snapshot])
        self.assertEqual(len(checked["snapshots"][0]["records"]), 2)

    def test_r26_projection_preserves_controls_on_controls(self):
        pages = project_pages(self.controlled_snapshot(restore=True), [["ev", "fixture-owner", 1]])
        self.assertEqual(len(pages[0]["snapshot"]["records"]), 3)
        self.assertFalse(lineage_state(pages[0]["snapshot"])[0]["retracted"])

    def test_r26_oversized_control_group_refuses_partial_page(self):
        with self.assertRaises(ValueError):
            project_pages(self.controlled_snapshot(restore=True), [["ev", "fixture-owner", 1]], record_limit=2)

    def test_r26_missing_control_is_not_detectable_from_page_alone(self):
        # A structurally valid subset can omit an unseen control. Completeness
        # must be established by host projection over authenticated source data.
        snapshot = self.controlled_snapshot()
        snapshot["records"] = snapshot["records"][:1]
        checked = self.client.validate_query_page(
            {"closure_complete": True, "result_complete": True, "end": True, "next_cursor": None}, [snapshot])
        self.assertFalse(lineage_state(checked["snapshots"][0])[0]["retracted"])


if __name__ == "__main__":
    unittest.main()
