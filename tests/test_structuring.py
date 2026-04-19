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


class TestValidPayloads:
    def test_valid_payload_returns_200(self):
        response = client.post("/api/v1/structuring", json=VALID_PAYLOAD)
        assert response.status_code == 200

    def test_valid_payload_returns_success_status(self):
        response = client.post("/api/v1/structuring", json=VALID_PAYLOAD)
        assert response.json()["status"] == "success"

    def test_valid_payload_echoes_text_blocks(self):
        response = client.post("/api/v1/structuring", json=VALID_PAYLOAD)
        assert response.json()["data"]["text_blocks"] == VALID_PAYLOAD["text_blocks"]

    def test_valid_payload_uses_from_alias_not_from_underscore(self):
        response = client.post("/api/v1/structuring", json=VALID_PAYLOAD)
        element = response.json()["data"]["visual_elements"][0]
        assert "from" in element
        assert "from_" not in element
        assert element["from"] == "Frontend"
        assert element["to"] == "API"

    def test_valid_payload_complete_response_structure(self):
        response = client.post("/api/v1/structuring", json=VALID_PAYLOAD)
        body = response.json()
        assert "status" in body
        assert "data" in body
        assert "text_blocks" in body["data"]
        assert "visual_elements" in body["data"]


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
