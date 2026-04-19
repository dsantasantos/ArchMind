from unittest.mock import patch, MagicMock
from starlette.testclient import TestClient

from main import app

client = TestClient(app)

VALID_PAYLOAD = {
    "text_blocks": ["Frontend", "React Application", "API", "Database"],
    "visual_elements": [
        {"from": "Frontend", "to": "API"},
        {"from": "API", "to": "Database"},
    ],
}

MOCK_LLM_RESPONSE = '[{"id":"c1","name":"Frontend","type":"frontend"},{"id":"c2","name":"API","type":"service"},{"id":"c3","name":"Database","type":"database"}]'

MOCK_COMPONENTS = [
    {"id": "c1", "name": "Frontend", "type": "frontend"},
    {"id": "c2", "name": "API", "type": "service"},
    {"id": "c3", "name": "Database", "type": "database"},
]


def _make_mock_llm():
    mock = MagicMock()
    mock.generate.return_value = MOCK_LLM_RESPONSE
    return mock


class TestValidPayloads:
    def test_valid_payload_returns_200(self):
        with patch("core.structuring.component_recognizer.ClaudeClient", return_value=_make_mock_llm()):
            response = client.post("/api/v1/structuring", json=VALID_PAYLOAD)
        assert response.status_code == 200

    def test_valid_payload_returns_success_status(self):
        with patch("core.structuring.component_recognizer.ClaudeClient", return_value=_make_mock_llm()):
            response = client.post("/api/v1/structuring", json=VALID_PAYLOAD)
        assert response.json()["status"] == "success"

    def test_response_does_not_include_input_fields(self):
        with patch("core.structuring.component_recognizer.ClaudeClient", return_value=_make_mock_llm()):
            response = client.post("/api/v1/structuring", json=VALID_PAYLOAD)
        data = response.json()["data"]
        assert "text_blocks" not in data
        assert "visual_elements" not in data

    def test_valid_payload_returns_components(self):
        with patch("core.structuring.component_recognizer.ClaudeClient", return_value=_make_mock_llm()):
            response = client.post("/api/v1/structuring", json=VALID_PAYLOAD)
        data = response.json()["data"]
        assert "components" in data
        assert isinstance(data["components"], list)

    def test_valid_payload_components_have_correct_fields(self):
        with patch("core.structuring.component_recognizer.ClaudeClient", return_value=_make_mock_llm()):
            response = client.post("/api/v1/structuring", json=VALID_PAYLOAD)
        components = response.json()["data"]["components"]
        assert len(components) == 3
        for c in components:
            assert "id" in c
            assert "name" in c
            assert "type" in c

    def test_valid_payload_component_types_are_valid(self):
        with patch("core.structuring.component_recognizer.ClaudeClient", return_value=_make_mock_llm()):
            response = client.post("/api/v1/structuring", json=VALID_PAYLOAD)
        components = response.json()["data"]["components"]
        valid_types = {"frontend", "service", "database"}
        for c in components:
            assert c["type"] in valid_types

    def test_valid_payload_complete_response_structure(self):
        with patch("core.structuring.component_recognizer.ClaudeClient", return_value=_make_mock_llm()):
            response = client.post("/api/v1/structuring", json=VALID_PAYLOAD)
        body = response.json()
        assert "status" in body
        assert "data" in body
        assert "components" in body["data"]


class TestInvalidPayloads:
    def test_text_blocks_not_a_list_returns_422(self):
        payload = {**VALID_PAYLOAD, "text_blocks": "not a list"}
        response = client.post("/api/v1/structuring", json=payload)
        assert response.status_code == 422
        assert response.json()["status"] == "error"
        assert response.json()["message"] == "Invalid payload structure"

    def test_visual_elements_not_a_list_returns_422(self):
        payload = {**VALID_PAYLOAD, "visual_elements": "not a list"}
        response = client.post("/api/v1/structuring", json=payload)
        assert response.status_code == 422
        assert response.json()["status"] == "error"

    def test_visual_element_missing_from_returns_422(self):
        payload = {
            "text_blocks": ["A", "B"],
            "visual_elements": [{"to": "B"}],
        }
        response = client.post("/api/v1/structuring", json=payload)
        assert response.status_code == 422
        assert response.json()["status"] == "error"

    def test_visual_element_missing_to_returns_422(self):
        payload = {
            "text_blocks": ["A", "B"],
            "visual_elements": [{"from": "A"}],
        }
        response = client.post("/api/v1/structuring", json=payload)
        assert response.status_code == 422
        assert response.json()["status"] == "error"

    def test_missing_text_blocks_field_returns_422(self):
        payload = {"visual_elements": [{"from": "A", "to": "B"}]}
        response = client.post("/api/v1/structuring", json=payload)
        assert response.status_code == 422
        assert response.json()["status"] == "error"

    def test_missing_visual_elements_field_returns_422(self):
        payload = {"text_blocks": ["A", "B"]}
        response = client.post("/api/v1/structuring", json=payload)
        assert response.status_code == 422
        assert response.json()["status"] == "error"

    def test_empty_payload_returns_422(self):
        response = client.post("/api/v1/structuring", json={})
        assert response.status_code == 422
        assert response.json()["status"] == "error"

    def test_null_text_blocks_returns_422(self):
        payload = {**VALID_PAYLOAD, "text_blocks": None}
        response = client.post("/api/v1/structuring", json=payload)
        assert response.status_code == 422

    def test_null_visual_elements_returns_422(self):
        payload = {**VALID_PAYLOAD, "visual_elements": None}
        response = client.post("/api/v1/structuring", json=payload)
        assert response.status_code == 422

    def test_visual_elements_with_both_fields_missing_returns_422(self):
        payload = {
            "text_blocks": ["A"],
            "visual_elements": [{}],
        }
        response = client.post("/api/v1/structuring", json=payload)
        assert response.status_code == 422
        assert response.json()["status"] == "error"


class TestComponentRecognizer:
    def test_recognizer_returns_empty_list_on_invalid_json(self):
        from core.structuring.component_recognizer import _parse_components
        assert _parse_components("not json") == []

    def test_recognizer_parses_json_wrapped_in_markdown(self):
        from core.structuring.component_recognizer import _parse_components
        text = '```json\n[{"id":"c1","name":"A","type":"frontend"}]\n```'
        result = _parse_components(text)
        assert len(result) == 1
        assert result[0]["name"] == "A"

    def test_recognizer_parses_clean_json(self):
        from core.structuring.component_recognizer import _parse_components
        result = _parse_components(MOCK_LLM_RESPONSE)
        assert len(result) == 3
        assert result[0]["type"] == "frontend"
