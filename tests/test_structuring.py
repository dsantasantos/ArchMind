from unittest.mock import patch, MagicMock
from starlette.testclient import TestClient

from main import app

client = TestClient(app)

VALID_PAYLOAD = {
    "text_blocks": ["Frontend", "React Application", "HTTP Request", "API", "Backend Service", "REST API", "Database Queries", "Database", "SQL Server"],
    "grouped_elements": [
        {"label": "Frontend Component", "texts": ["Frontend", "React Application"]},
        {"label": "API Component", "texts": ["API", "Backend Service", "REST API"]},
        {"label": "Database Component", "texts": ["Database", "SQL Server"]},
    ],
    "detected_keywords": [
        {"text": "React Application", "hint": "frontend_framework"},
        {"text": "REST API", "hint": "api_architecture_style"},
        {"text": "Backend Service", "hint": "service_layer"},
        {"text": "SQL Server", "hint": "database_system"},
        {"text": "HTTP Request", "hint": "communication_protocol"},
    ],
    "relationship_hints": [
        {"from": "Frontend", "to": "API", "label": "HTTP Request"},
        {"from": "API", "to": "Database", "label": "Database Queries"},
    ],
    "context_groups": [
        {"name": "Frontend Layer", "contains": ["Frontend", "React Application"]},
        {"name": "API Layer", "contains": ["API", "Backend Service", "REST API"]},
        {"name": "Data Layer", "contains": ["Database", "SQL Server"]},
    ],
}

MOCK_LLM_RESPONSE = '[{"id":"c1","name":"Frontend","type":"frontend"},{"id":"c2","name":"API","type":"service"},{"id":"c3","name":"Database","type":"database"}]'

MOCK_RELATIONSHIPS_RESPONSE = '[{"from":"c1","to":"c2","type":"http_request"},{"from":"c2","to":"c3","type":"database_query"}]'

MOCK_ARCHITECTURE_RESPONSE = "layered"

MOCK_COMPONENTS = [
    {"id": "c1", "name": "Frontend", "type": "frontend"},
    {"id": "c2", "name": "API", "type": "service"},
    {"id": "c3", "name": "Database", "type": "database"},
]

MOCK_RELATIONSHIPS = [
    {"from": "c1", "to": "c2", "type": "http_request"},
    {"from": "c2", "to": "c3", "type": "database_query"},
]


def _make_mock_component_llm():
    mock = MagicMock()
    mock.generate.return_value = MOCK_LLM_RESPONSE
    return mock


def _make_mock_relationship_llm():
    mock = MagicMock()
    mock.generate.return_value = MOCK_RELATIONSHIPS_RESPONSE
    return mock


def _make_mock_architecture_llm():
    mock = MagicMock()
    mock.generate.return_value = MOCK_ARCHITECTURE_RESPONSE
    return mock


def _patch_all_llms():
    return (
        patch("core.structuring.component_recognizer.ClaudeClient", return_value=_make_mock_component_llm()),
        patch("core.structuring.relationship_recognizer.ClaudeClient", return_value=_make_mock_relationship_llm()),
        patch("core.structuring.architecture_recognizer.ClaudeClient", return_value=_make_mock_architecture_llm()),
    )


class TestValidPayloads:
    def test_valid_payload_returns_200(self):
        p1, p2, p3 = _patch_all_llms()
        with p1, p2, p3:
            response = client.post("/api/v1/structuring", json=VALID_PAYLOAD)
        assert response.status_code == 200

    def test_valid_payload_returns_success_status(self):
        p1, p2, p3 = _patch_all_llms()
        with p1, p2, p3:
            response = client.post("/api/v1/structuring", json=VALID_PAYLOAD)
        assert response.json()["status"] == "success"

    def test_response_does_not_include_input_fields(self):
        p1, p2, p3 = _patch_all_llms()
        with p1, p2, p3:
            response = client.post("/api/v1/structuring", json=VALID_PAYLOAD)
        data = response.json()["data"]
        assert "text_blocks" not in data
        assert "relationship_hints" not in data
        assert "grouped_elements" not in data
        assert "detected_keywords" not in data
        assert "context_groups" not in data

    def test_valid_payload_returns_components(self):
        p1, p2, p3 = _patch_all_llms()
        with p1, p2, p3:
            response = client.post("/api/v1/structuring", json=VALID_PAYLOAD)
        data = response.json()["data"]
        assert "components" in data
        assert isinstance(data["components"], list)

    def test_valid_payload_returns_relationships(self):
        p1, p2, p3 = _patch_all_llms()
        with p1, p2, p3:
            response = client.post("/api/v1/structuring", json=VALID_PAYLOAD)
        data = response.json()["data"]
        assert "relationships" in data
        assert isinstance(data["relationships"], list)

    def test_valid_payload_returns_architecture_style(self):
        p1, p2, p3 = _patch_all_llms()
        with p1, p2, p3:
            response = client.post("/api/v1/structuring", json=VALID_PAYLOAD)
        data = response.json()["data"]
        assert "architecture_style" in data
        assert data["architecture_style"] == "layered"

    def test_valid_payload_components_have_correct_fields(self):
        p1, p2, p3 = _patch_all_llms()
        with p1, p2, p3:
            response = client.post("/api/v1/structuring", json=VALID_PAYLOAD)
        components = response.json()["data"]["components"]
        assert len(components) == 3
        for c in components:
            assert "id" in c
            assert "name" in c
            assert "type" in c

    def test_valid_payload_component_types_are_valid(self):
        p1, p2, p3 = _patch_all_llms()
        with p1, p2, p3:
            response = client.post("/api/v1/structuring", json=VALID_PAYLOAD)
        components = response.json()["data"]["components"]
        valid_types = {"frontend", "service", "database"}
        for c in components:
            assert c["type"] in valid_types

    def test_valid_payload_relationships_have_correct_fields(self):
        p1, p2, p3 = _patch_all_llms()
        with p1, p2, p3:
            response = client.post("/api/v1/structuring", json=VALID_PAYLOAD)
        relationships = response.json()["data"]["relationships"]
        assert len(relationships) == 2
        for r in relationships:
            assert "from" in r
            assert "to" in r
            assert "type" in r

    def test_valid_payload_relationship_types_are_valid(self):
        p1, p2, p3 = _patch_all_llms()
        with p1, p2, p3:
            response = client.post("/api/v1/structuring", json=VALID_PAYLOAD)
        relationships = response.json()["data"]["relationships"]
        valid_types = {"http_request", "database_query", "internal_call"}
        for r in relationships:
            assert r["type"] in valid_types

    def test_valid_payload_relationship_ids_reference_components(self):
        p1, p2, p3 = _patch_all_llms()
        with p1, p2, p3:
            response = client.post("/api/v1/structuring", json=VALID_PAYLOAD)
        data = response.json()["data"]
        component_ids = {c["id"] for c in data["components"]}
        for r in data["relationships"]:
            assert r["from"] in component_ids
            assert r["to"] in component_ids

    def test_valid_payload_complete_response_structure(self):
        p1, p2, p3 = _patch_all_llms()
        with p1, p2, p3:
            response = client.post("/api/v1/structuring", json=VALID_PAYLOAD)
        body = response.json()
        assert "status" in body
        assert "data" in body
        assert "components" in body["data"]
        assert "relationships" in body["data"]
        assert "architecture_style" in body["data"]


class TestInvalidPayloads:
    def test_text_blocks_not_a_list_returns_422(self):
        payload = {**VALID_PAYLOAD, "text_blocks": "not a list"}
        response = client.post("/api/v1/structuring", json=payload)
        assert response.status_code == 422
        assert response.json()["status"] == "error"
        assert response.json()["message"] == "Invalid payload structure"

    def test_relationship_hints_not_a_list_returns_422(self):
        payload = {**VALID_PAYLOAD, "relationship_hints": "not a list"}
        response = client.post("/api/v1/structuring", json=payload)
        assert response.status_code == 422
        assert response.json()["status"] == "error"

    def test_relationship_hint_missing_from_returns_422(self):
        payload = {
            **VALID_PAYLOAD,
            "relationship_hints": [{"to": "API", "label": "HTTP Request"}],
        }
        response = client.post("/api/v1/structuring", json=payload)
        assert response.status_code == 422
        assert response.json()["status"] == "error"

    def test_relationship_hint_missing_to_returns_422(self):
        payload = {
            **VALID_PAYLOAD,
            "relationship_hints": [{"from": "Frontend", "label": "HTTP Request"}],
        }
        response = client.post("/api/v1/structuring", json=payload)
        assert response.status_code == 422
        assert response.json()["status"] == "error"

    def test_relationship_hint_missing_label_returns_422(self):
        payload = {
            **VALID_PAYLOAD,
            "relationship_hints": [{"from": "Frontend", "to": "API"}],
        }
        response = client.post("/api/v1/structuring", json=payload)
        assert response.status_code == 422
        assert response.json()["status"] == "error"

    def test_missing_text_blocks_field_returns_422(self):
        payload = {k: v for k, v in VALID_PAYLOAD.items() if k != "text_blocks"}
        response = client.post("/api/v1/structuring", json=payload)
        assert response.status_code == 422
        assert response.json()["status"] == "error"

    def test_missing_relationship_hints_field_returns_422(self):
        payload = {k: v for k, v in VALID_PAYLOAD.items() if k != "relationship_hints"}
        response = client.post("/api/v1/structuring", json=payload)
        assert response.status_code == 422
        assert response.json()["status"] == "error"

    def test_missing_grouped_elements_field_returns_422(self):
        payload = {k: v for k, v in VALID_PAYLOAD.items() if k != "grouped_elements"}
        response = client.post("/api/v1/structuring", json=payload)
        assert response.status_code == 422
        assert response.json()["status"] == "error"

    def test_missing_detected_keywords_field_returns_422(self):
        payload = {k: v for k, v in VALID_PAYLOAD.items() if k != "detected_keywords"}
        response = client.post("/api/v1/structuring", json=payload)
        assert response.status_code == 422
        assert response.json()["status"] == "error"

    def test_missing_context_groups_field_returns_422(self):
        payload = {k: v for k, v in VALID_PAYLOAD.items() if k != "context_groups"}
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

    def test_null_relationship_hints_returns_422(self):
        payload = {**VALID_PAYLOAD, "relationship_hints": None}
        response = client.post("/api/v1/structuring", json=payload)
        assert response.status_code == 422

    def test_relationship_hint_with_all_fields_missing_returns_422(self):
        payload = {
            **VALID_PAYLOAD,
            "relationship_hints": [{}],
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


class TestRelationshipRecognizer:
    def test_recognizer_returns_empty_list_on_invalid_json(self):
        from core.structuring.relationship_recognizer import _parse_relationships
        assert _parse_relationships("not json") == []

    def test_recognizer_parses_json_wrapped_in_markdown(self):
        from core.structuring.relationship_recognizer import _parse_relationships
        text = '```json\n[{"from":"c1","to":"c2","type":"http_request"}]\n```'
        result = _parse_relationships(text)
        assert len(result) == 1
        assert result[0]["type"] == "http_request"

    def test_recognizer_parses_clean_json(self):
        from core.structuring.relationship_recognizer import _parse_relationships
        result = _parse_relationships(MOCK_RELATIONSHIPS_RESPONSE)
        assert len(result) == 2
        assert result[0]["from"] == "c1"
        assert result[0]["to"] == "c2"
        assert result[1]["type"] == "database_query"


class TestArchitectureRecognizer:
    def test_parse_returns_first_word(self):
        from core.structuring.architecture_recognizer import _parse_architecture_style
        assert _parse_architecture_style("layered") == "layered"

    def test_parse_strips_whitespace(self):
        from core.structuring.architecture_recognizer import _parse_architecture_style
        assert _parse_architecture_style("  microservices extra") == "microservices"

    def test_parse_returns_unknown_on_empty(self):
        from core.structuring.architecture_recognizer import _parse_architecture_style
        assert _parse_architecture_style("") == "unknown"

    def test_parse_lowercases_result(self):
        from core.structuring.architecture_recognizer import _parse_architecture_style
        assert _parse_architecture_style("LAYERED") == "layered"
