"""Focused tests for Codex-format support that do not depend on snapshot plugins."""

import json

from claude_code_transcripts import parse_session_file


def test_parses_codex_json_file_with_items_array(tmp_path):
    """Codex JSON exports with top-level items should be normalized."""
    session_file = tmp_path / "codex-session.json"
    session_file.write_text(
        json.dumps(
            {
                "items": [
                    {
                        "timestamp": "2026-01-01T00:00:00Z",
                        "type": "response_item",
                        "payload": {
                            "type": "message",
                            "role": "user",
                            "content": [
                                {"type": "input_text", "text": "Create an API client"}
                            ],
                        },
                    },
                    {
                        "timestamp": "2026-01-01T00:00:01Z",
                        "type": "response_item",
                        "payload": {
                            "type": "message",
                            "role": "assistant",
                            "content": [{"type": "output_text", "text": "Done"}],
                        },
                    },
                ]
            }
        )
    )

    result = parse_session_file(session_file)
    assert "loglines" in result
    assert [item["type"] for item in result["loglines"]] == ["user", "assistant"]


def test_codex_failed_function_call_output_maps_to_error_tool_result(tmp_path):
    """Codex function_call_output with failed status should set is_error."""
    session_file = tmp_path / "codex-errors.jsonl"
    session_file.write_text(
        '{"timestamp":"2026-01-01T00:00:00Z","type":"response_item","payload":{"type":"function_call_output","call_id":"call_1","status":"failed","output":"command failed"}}\n'
    )

    result = parse_session_file(session_file)
    block = result["loglines"][0]["message"]["content"][0]

    assert block["type"] == "tool_result"
    assert block["is_error"] is True
