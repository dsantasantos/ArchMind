from core.structuring.validator import validate_structural_integrity

def test_validate_structural_integrity_removes_orphan_relationships():
    components = [
        {"id": "c1", "name": "API"},
        {"id": "c2", "name": "DB"}
    ]
    relationships = [
        {"from": "c1", "to": "c2", "type": "query"},  # Válido
        {"from": "c1", "to": "c3", "type": "query"},  # Inválido (c3 não existe)
        {"from": "c4", "to": "c1", "type": "query"},  # Inválido (c4 não existe)
    ]
    
    valid_rels = validate_structural_integrity(components, relationships)
    
    assert len(valid_rels) == 1
    assert valid_rels[0]["from"] == "c1"
    assert valid_rels[0]["to"] == "c2"

def test_validate_structural_integrity_keeps_all_valid_relationships():
    components = [
        {"id": "c1", "name": "API"},
        {"id": "c2", "name": "DB"}
    ]
    relationships = [
        {"from": "c1", "to": "c2", "type": "query"},
        {"from": "c2", "to": "c1", "type": "response"},
    ]
    
    valid_rels = validate_structural_integrity(components, relationships)
    
    assert len(valid_rels) == 2

def test_validate_structural_integrity_returns_empty_if_no_components():
    components = []
    relationships = [{"from": "c1", "to": "c2", "type": "query"}]
    
    assert validate_structural_integrity(components, relationships) == []
