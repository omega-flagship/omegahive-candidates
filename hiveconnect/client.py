"""Offline-testable read-only client core for OmegaDot's baseline MCP bridge.

No HTTP transport, credentials, invitation redemption, installation or grants.
The caller supplies an authorized transport. This client does not prove that
the host enforces authorization or that a source-declared tool is loaded.
"""
from __future__ import annotations

import copy
import json
from pathlib import Path


class ClientError(Exception):
    """A stable local error code; provider text and content are not logged."""


class ReadOnlyClient:
    ALLOWED = frozenset({"hive_whoami", "hive_query"})
    MAX_REQUEST = 16 * 1024
    MAX_RESPONSE = 256 * 1024

    def __init__(self, transport, snapshot=None):
        if snapshot is None:
            snapshot = json.loads(Path(__file__).with_name("baseline_schema.json").read_text())
        self.snapshot = copy.deepcopy(snapshot)
        self.schemas = {t["name"]: t["inputSchema"] for t in self.snapshot["tools"]}
        self.transport = transport
        self.ready = False
        self.discovered = frozenset()
        self.next_id = 0

    @staticmethod
    def _encode(value):
        try:
            return json.dumps(value, allow_nan=False, ensure_ascii=False).encode("utf-8")
        except (ValueError, TypeError, UnicodeError):
            raise ClientError("invalid_json") from None

    @staticmethod
    def _decode(raw):
        def pairs(items):
            out = {}
            for key, value in items:
                if key in out:
                    raise ValueError("duplicate key")
                out[key] = value
            return out

        def constant(_):
            raise ValueError("nonfinite JSON")

        try:
            return json.loads(raw, object_pairs_hook=pairs, parse_constant=constant)
        except (ValueError, TypeError, UnicodeError, RecursionError):
            raise ClientError("malformed_response") from None

    def _rpc(self, method, params):
        self.next_id += 1
        request_id = f"hiveconnect-{self.next_id}"
        wire = self._encode({"jsonrpc": "2.0", "id": request_id, "method": method, "params": params})
        if len(wire) > self.MAX_REQUEST:
            raise ClientError("request_too_large")
        try:
            # Exactly one dispatch. A transport failure never causes a retry.
            raw = self.transport(wire)
        except Exception:
            raise ClientError("transport_failed") from None
        if not isinstance(raw, bytes):
            raise ClientError("transport_must_return_bytes")
        if len(raw) > self.MAX_RESPONSE:
            raise ClientError("response_too_large")
        response = self._decode(raw)
        if not isinstance(response, dict) or response.get("jsonrpc") != "2.0":
            raise ClientError("invalid_rpc_envelope")
        if response.get("id") != request_id:
            raise ClientError("response_id_mismatch")
        if ("error" in response) == ("result" in response):
            raise ClientError("invalid_rpc_envelope")
        if "error" in response:
            self._rpc_error(response["error"])
        if not isinstance(response["result"], dict):
            raise ClientError("invalid_result")
        return response["result"]

    def _rpc_error(self, error):
        raise ClientError("rpc_error")

    def initialize(self):
        self.ready = False
        self.discovered = frozenset()
        result = self._rpc("initialize", {
            "protocolVersion": self.snapshot["protocol"],
            "capabilities": {},
            "clientInfo": {"name": "hiveconnect-readonly", "version": "0.1.0"},
        })
        if result.get("protocolVersion") != self.snapshot["protocol"]:
            raise ClientError("protocol_mismatch")
        server_info = result.get("serverInfo")
        if not isinstance(server_info, dict) or server_info.get("name") != "omegahive":
            raise ClientError("wrong_server")
        listed = self._rpc("tools/list", {})
        tools = listed.get("tools")
        if not isinstance(tools, list) or len(tools) > 512:
            raise ClientError("invalid_tool_list")
        found = {}
        for tool in tools:
            if not isinstance(tool, dict) or not isinstance(tool.get("name"), str):
                raise ClientError("invalid_tool_list")
            if tool["name"] in found:
                raise ClientError("duplicate_tool")
            found[tool["name"]] = tool
        for name in self.ALLOWED & found.keys():
            if found[name].get("inputSchema") != self.schemas[name]:
                raise ClientError("schema_mismatch")
        self.discovered = frozenset(self.ALLOWED & found.keys())
        self.ready = True
        return {"protocol": result["protocolVersion"], "advertised_read_tools": sorted(self.discovered),
                "qualification": "advertised_only; host policy/load state unverified"}

    def call(self, name, arguments):
        if not self.ready:
            raise ClientError("not_initialized")
        if name not in self.ALLOWED:
            raise ClientError("readonly_tool_refused")
        if name not in self.discovered:
            raise ClientError("tool_unavailable")
        schema = self.schemas[name]
        if not isinstance(arguments, dict):
            raise ClientError("arguments_not_object")
        props = schema["properties"]
        if set(arguments) - set(props) or set(schema.get("required", [])) - set(arguments):
            raise ClientError("invalid_arguments")
        # Baseline read tools have flat string fields only. Do not pretend
        # this is a general JSON Schema engine for future S3/S4 tools.
        for key, value in arguments.items():
            spec = props[key]
            if spec.get("type") != "string" or not isinstance(value, str):
                raise ClientError("invalid_arguments")
            if len(value) > spec.get("maxLength", 2000):
                raise ClientError("invalid_arguments")
        result = self._rpc("tools/call", {"name": name, "arguments": arguments})
        if type(result.get("isError")) is not bool:
            raise ClientError("invalid_tool_result")
        if result["isError"]:
            raise ClientError("tool_error")
        content = result.get("content")
        if not isinstance(content, list) or len(content) != 1:
            raise ClientError("unsupported_content")
        block = content[0]
        if not isinstance(block, dict) or block.get("type") != "text" or not isinstance(block.get("text"), str):
            raise ClientError("unsupported_content")
        return self._decode(block["text"])
