import copy
import json
import unittest
from pathlib import Path

from hiveconnect.client import ClientError, ReadOnlyClient

SNAPSHOT = json.loads(Path(__file__).resolve().parents[1].joinpath("baseline_schema.json").read_text())


class FixtureTransport:
    def __init__(self):
        self.calls = []
        self.tools = copy.deepcopy(SNAPSHOT["tools"])
        self.protocol = SNAPSHOT["protocol"]
        self.server = "omegahive"
        self.transform = lambda response: response
        self.value = {"id": "synthetic-member", "swarm": {"id": "synthetic-swarm"}}

    def __call__(self, wire):
        request = json.loads(wire)
        self.calls.append(request)
        method = request["method"]
        if method == "initialize":
            result = {"protocolVersion": self.protocol, "serverInfo": {"name": self.server}}
        elif method == "tools/list":
            result = {"tools": self.tools}
        else:
            result = {"content": [{"type": "text", "text": json.dumps(self.value)}], "isError": False}
        response = self.transform({"jsonrpc": "2.0", "id": request["id"], "result": result})
        return response if isinstance(response, bytes) else json.dumps(response).encode()


class ClientChecks(unittest.TestCase):
    def setUp(self):
        self.transport = FixtureTransport()
        self.client = ReadOnlyClient(self.transport)

    def ready(self):
        self.client.initialize()

    def test_identity_and_unknown_truth_roundtrip(self):
        self.ready()
        self.assertEqual(self.client.call("hive_whoami", {}), self.transport.value)
        self.transport.value = {"observations": [{"statement": "synthetic", "evidence_id": "ev1"}]}
        result = self.client.call("hive_query", {"pattern": "(Current $statement $tv $stamp)"})
        self.assertNotIn("tv", result["observations"][0])

    def test_mutations_and_future_tools_refused_before_dispatch(self):
        self.ready()
        count = len(self.transport.calls)
        for name in ("hive_publish", "hive_send", "hive_goal_create", "hive_capabilities"):
            with self.assertRaisesRegex(ClientError, "readonly_tool_refused"):
                self.client.call(name, {})
        self.assertEqual(len(self.transport.calls), count)

    def test_input_admission(self):
        self.ready()
        count = len(self.transport.calls)
        for arguments in ({}, {"pattern": 7}, {"pattern": "x", "actor": "other"}, {"pattern": "x" * 2001}, []):
            with self.assertRaises(ClientError):
                self.client.call("hive_query", arguments)
        self.assertEqual(len(self.transport.calls), count)

    def test_missing_tool_is_explicit(self):
        self.transport.tools = [t for t in self.transport.tools if t["name"] != "hive_query"]
        self.ready()
        with self.assertRaisesRegex(ClientError, "tool_unavailable"):
            self.client.call("hive_query", {"pattern": "x"})

    def test_schema_drift_fail_closed(self):
        next(t for t in self.transport.tools if t["name"] == "hive_query")["inputSchema"]["properties"]["pattern"]["maxLength"] = 9999
        with self.assertRaisesRegex(ClientError, "schema_mismatch"):
            self.ready()
        self.assertFalse(self.client.ready)

    def test_protocol_and_server_checked(self):
        self.transport.protocol = "unknown"
        with self.assertRaisesRegex(ClientError, "protocol_mismatch"):
            self.ready()
        self.transport.protocol = SNAPSHOT["protocol"]
        self.transport.server = "other-hive"
        with self.assertRaisesRegex(ClientError, "wrong_server"):
            self.ready()

    def test_duplicate_tools_refused(self):
        self.transport.tools.append(copy.deepcopy(self.transport.tools[0]))
        with self.assertRaisesRegex(ClientError, "duplicate_tool"):
            self.ready()

    def test_response_correlation(self):
        self.ready()
        self.transport.transform = lambda r: dict(r, id="wrong-request")
        with self.assertRaisesRegex(ClientError, "response_id_mismatch"):
            self.client.call("hive_whoami", {})

    def test_provider_errors_do_not_expose_payload(self):
        self.ready()
        secret = "synthetic-secret-do-not-copy"
        def error(r):
            r["result"] = {"isError": True, "content": [{"type": "text", "text": secret}]}
            return r
        self.transport.transform = error
        with self.assertRaisesRegex(ClientError, "^tool_error$"):
            self.client.call("hive_whoami", {})

    def test_malformed_and_oversized_response(self):
        self.ready()
        for raw, error in ((b'{"id":"a","id":"b"}', "malformed_response"),
                           (b'{"value":NaN}', "malformed_response"),
                           (b"x" * (ReadOnlyClient.MAX_RESPONSE + 1), "response_too_large")):
            self.transport.transform = lambda r, raw=raw: raw
            with self.assertRaisesRegex(ClientError, error):
                self.client.call("hive_whoami", {})

    def test_transport_failure_has_one_dispatch_no_secret(self):
        self.ready()
        calls = []
        def broken(wire):
            calls.append(wire)
            raise TimeoutError("synthetic-token")
        self.client.transport = broken
        with self.assertRaisesRegex(ClientError, "^transport_failed$"):
            self.client.call("hive_whoami", {})
        self.assertEqual(len(calls), 1)

    def test_invalid_result_and_unsupported_content(self):
        self.ready()
        for result in ({"content": [], "isError": False}, {"content": [], "isError": "false"},
                       {"content": [{"type": "image", "text": "x"}], "isError": False}):
            self.transport.transform = lambda r, result=result: dict(r, result=result)
            with self.assertRaises(ClientError):
                self.client.call("hive_whoami", {})

    def test_invalid_initialize_shape(self):
        self.transport.transform = lambda r: dict(r, result={"protocolVersion": SNAPSHOT["protocol"], "serverInfo": []})
        with self.assertRaisesRegex(ClientError, "wrong_server"):
            self.ready()
        self.assertFalse(self.client.ready)


if __name__ == "__main__":
    unittest.main()
