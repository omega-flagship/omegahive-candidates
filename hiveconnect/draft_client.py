"""Read-only S3/S4 prototype at r2.4, L0 only; full schemas unfrozen.

No live transport or credentials. Query projection and scopes are not invented:
callers can pass the owner's validator for a separately supplied Atom snapshot.
"""
import copy
import re

from .client import ClientError, ReadOnlyClient


# Proposed JSON schemas, derived from amended prose, NOT build-frozen schemas.
READ_SCHEMAS = {
    "hive_whoami": {"type": "object", "properties": {}, "additionalProperties": False},
    "hive_capabilities": {"type": "object", "properties": {}, "additionalProperties": False},
    "hive_goal_get": {"type": "object", "properties": {"goal_id": {"type": "string"}},
                      "required": ["goal_id"], "additionalProperties": False},
    "hive_evidence_query": {"type": "object", "properties": {"pattern": {"type": "string"},
                            "scopes": {"type": "array", "items": {"type": "object"}}},
                            "required": ["pattern"], "additionalProperties": False},
    "hive_artifact_read": {"type": "object", "properties": {"artifact_id": {"type": "string"},
                           "revision": {"type": "integer"}, "expected_digest": {"type": "string"}},
                           "required": ["artifact_id", "revision", "expected_digest"], "additionalProperties": False},
    "hive_exhibit_read": {"type": "object", "properties": {"share_id": {"type": "string"},
                          "cursor": {"type": "string"}, "expected_digest": {"type": "string"}},
                          "required": ["share_id", "expected_digest"], "additionalProperties": False},
}
ERROR_CODES = frozenset({"not_assigned", "binding_mismatch", "deadline_passed", "share_closed",
                         "stale_revision", "digest_mismatch", "schema_invalid", "spend_limit",
                         "grant_closed", "idempotency_conflict"})
WIRE_HASH = re.compile(r"sha256:[a-f0-9]{64}\Z")


class HiveRemoteError(ClientError):
    def __init__(self, code):
        self.code = code
        super().__init__(code)


class DraftReadClient(ReadOnlyClient):
    ALLOWED = frozenset(READ_SCHEMAS)

    def __init__(self, transport, *, expected_server_version, expected_mind_id, atom_validator=None):
        if not isinstance(expected_server_version, str) or not expected_server_version:
            raise ClientError("server_version_pin_required")
        if not isinstance(expected_mind_id, str) or not expected_mind_id:
            raise ClientError("member_identity_pin_required")
        super().__init__(transport)
        self.schemas = copy.deepcopy(READ_SCHEMAS)
        self.expected_server_version = expected_server_version
        self.expected_mind_id = expected_mind_id
        self.atom_validator = atom_validator

    def _rpc_error(self, error):
        data = error.get("data") if isinstance(error, dict) else None
        code = data.get("code") if isinstance(data, dict) else None
        status = data.get("http_status") if isinstance(data, dict) else None
        valid = (isinstance(error, dict) and error.get("code") == -32000
                 and type(status) is int and 400 <= status <= 599)
        raise HiveRemoteError(code if valid and isinstance(code, str) and code in ERROR_CODES else "unclassified_remote_error")

    def initialize(self):
        self.ready = False
        self.discovered = frozenset()
        result = self._rpc("initialize", {
            "protocolVersion": self.snapshot["protocol"], "capabilities": {},
            "clientInfo": {"name": "hiveconnect-draft-readonly", "version": "0.1.0"},
        })
        info = result.get("serverInfo")
        if result.get("protocolVersion") != self.snapshot["protocol"]:
            raise ClientError("protocol_mismatch")
        if not isinstance(info, dict) or info.get("name") != "omegahive":
            raise ClientError("wrong_server")
        if info.get("version") != self.expected_server_version:
            raise ClientError("server_version_mismatch")
        listed = self._rpc("tools/list", {})
        meta = listed.get("_meta")
        if not isinstance(meta, dict) or meta.get("x-hive-schema") != "s3-r1":
            raise ClientError("draft_schema_mismatch")
        items = listed.get("tools")
        if not isinstance(items, list) or len(items) > 512:
            raise ClientError("invalid_tool_list")
        found = {}
        for item in items:
            if not isinstance(item, dict) or not isinstance(item.get("name"), str):
                raise ClientError("invalid_tool_list")
            if item["name"] in found:
                raise ClientError("duplicate_tool")
            found[item["name"]] = item
        for name in self.ALLOWED & found.keys():
            if found[name].get("inputSchema") != self.schemas[name]:
                raise ClientError("draft_input_schema_mismatch")
        self.discovered = frozenset(self.ALLOWED & found.keys())
        self.ready = True
        return {"schema": "s3-r1", "read_tools": sorted(self.discovered), "qualification": "unfrozen_L0_prototype"}

    def call(self, name, arguments):
        if not self.ready:
            raise ClientError("not_initialized")
        if name not in self.ALLOWED:
            raise ClientError("readonly_tool_refused")
        if name not in self.discovered:
            raise ClientError("tool_unavailable")
        if not isinstance(arguments, dict):
            raise ClientError("arguments_not_object")
        spec = self.schemas[name]
        if set(arguments) - set(spec["properties"]) or set(spec.get("required", [])) - set(arguments):
            raise ClientError("draft_arguments_refused")
        for key, value in arguments.items():
            if key == "revision":
                if type(value) is not int or value < 0:
                    raise ClientError("draft_arguments_refused")
            elif key == "scopes":
                if not isinstance(value, list) or len(value) > 100:
                    raise ClientError("draft_arguments_refused")
                for tag in value:
                    if (not isinstance(tag, dict) or set(tag) not in ({"scope_id"}, {"grant_id"})
                            or not isinstance(next(iter(tag.values())), str)
                            or not next(iter(tag.values())) or len(next(iter(tag.values()))) > 2000):
                        raise ClientError("draft_arguments_refused")
            elif not isinstance(value, str) or not value or len(value) > 2000:
                raise ClientError("draft_arguments_refused")
            if key == "expected_digest" and not WIRE_HASH.fullmatch(value):
                raise ClientError("invalid_expected_digest")
        result = self._rpc("tools/call", {"name": name, "arguments": arguments})
        if "structuredContent" not in result:
            raise ClientError("structured_content_required")
        data = result["structuredContent"]
        if not isinstance(data, dict):
            raise ClientError("structured_content_not_object")
        content = result.get("content")
        if (not isinstance(content, list) or len(content) != 1 or not isinstance(content[0], dict)
                or content[0].get("type") != "text" or not isinstance(content[0].get("text"), str)
                or "\n" in content[0]["text"] or "\r" in content[0]["text"]):
            raise ClientError("summary_shape_mismatch")
        if result.get("isError", False) is not False:
            raise ClientError("unexpected_tool_error_format")
        if name == "hive_whoami" and data.get("id") != self.expected_mind_id:
            raise ClientError("member_identity_mismatch")
        if name == "hive_capabilities":
            self.validate_inventory(data)
        if name in {"hive_artifact_read", "hive_exhibit_read"}:
            if data.get("digest") != arguments["expected_digest"]:
                raise ClientError("read_digest_mismatch")
            if name == "hive_artifact_read" and data.get("revision") != arguments["revision"]:
                raise ClientError("read_revision_mismatch")
        return copy.deepcopy(data)

    def validate_inventory(self, data):
        if data.get("mind_id") != self.expected_mind_id:
            raise ClientError("inventory_identity_mismatch")
        revision = data.get("inventory_revision")
        if revision is not None and (not isinstance(revision, str) or not WIRE_HASH.fullmatch(revision)):
            raise ClientError("invalid_inventory_revision")
        skills = data.get("skills")
        if not isinstance(skills, list) or len(skills) > 4096:
            raise ClientError("invalid_inventory_skills")
        if revision is None and (data.get("loaded_at") is not None or data.get("availability") != "no-boot-receipt"):
            raise ClientError("missing_receipt_shape")
        if not isinstance(data.get("snapshot_at"), str) or not data["snapshot_at"]:
            raise ClientError("policy_snapshot_time_required")
        seen = set()
        for skill in skills:
            if not isinstance(skill, dict) or not isinstance(skill.get("id"), str) or skill["id"] in seen:
                raise ClientError("invalid_inventory_skill")
            seen.add(skill["id"])
            if skill.get("status") not in {"configured", "imported", "callable", "unknown"}:
                raise ClientError("invalid_inventory_status")
            if revision is None and skill["status"] != "unknown":
                raise ClientError("missing_boot_receipt")
            policy = skill.get("policy")
            if not isinstance(policy, dict) or policy.get("decision") not in {"allow", "ask", "deny"}:
                raise ClientError("invalid_inventory_policy")
        # This is shape validation only. An allow/callable pair is not a grant
        # to execute it and may change immediately after discovery.
        return copy.deepcopy(data)

    def validate_query_page(self, page, snapshots):
        """Validate an explicit page + snapshots; do not guess wire field name.

        The full JSON schema will specify where snapshots sit in the result.
        An incomplete result may contain complete premise/control closures.
        Validation cannot detect a withdrawal control omitted by the host;
        closure_complete is a host assertion, not a client completeness proof.
        """
        if not isinstance(page, dict) or page.get("closure_complete") is not True:
            raise ClientError("query_closure_incomplete")
        if type(page.get("result_complete")) is not bool or type(page.get("end")) is not bool:
            raise ClientError("query_page_flags_required")
        cursor = page.get("next_cursor")
        if page["end"]:
            if cursor is not None or not page["result_complete"]:
                raise ClientError("query_end_mismatch")
        elif not isinstance(cursor, str) or not cursor or len(cursor) > 2000 or page["result_complete"]:
            raise ClientError("query_cursor_mismatch")
        if not isinstance(snapshots, list) or len(snapshots) > 100:
            raise ClientError("query_snapshots_refused")
        validated = [self.validate_atom_snapshot(s) for s in snapshots]
        if len({s["scope"] for s in validated}) != len(validated):
            raise ClientError("duplicate_query_scope")
        if sum(len(s["records"]) for s in validated) > 200:
            raise ClientError("query_page_limit")
        return {"page": copy.deepcopy(page), "snapshots": validated}

    def validate_atom_snapshot(self, snapshot):
        if self.atom_validator is None:
            raise ClientError("atom_validator_required")
        try:
            return self.atom_validator(snapshot)
        except Exception:
            raise ClientError("atom_envelope_refused") from None
