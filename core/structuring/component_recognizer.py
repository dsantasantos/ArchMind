import logging

logger = logging.getLogger(__name__)

KNOWN_TECHNOLOGIES = {
    "rest api": "REST API",
    "graphql": "GraphQL",
    "grpc": "gRPC",
    "soap": "SOAP",
    "sql server": "SQL Server",
    "postgresql": "PostgreSQL",
    "postgres": "PostgreSQL",
    "mysql": "MySQL",
    "sqlite": "SQLite",
    "oracle": "Oracle",
    "mongodb": "MongoDB",
    "redis": "Redis",
    "cassandra": "Cassandra",
    "elasticsearch": "Elasticsearch",
    "react": "React",
    "angular": "Angular",
    "vue": "Vue",
    "svelte": "Svelte",
    "spring boot": "Spring Boot",
    "node.js": "Node.js",
    "nodejs": "Node.js",
    ".net": ".NET",
    "express": "Express",
    "django": "Django",
    "flask": "Flask",
    "fastapi": "FastAPI",
    "kafka": "Kafka",
    "rabbitmq": "RabbitMQ",
}

_HINT_TO_TYPE = {
    "frontend_framework": "frontend",
    "database_system": "database",
    "api_architecture_style": "service",
    "service_layer": "service",
    "communication_protocol": "service",
}

_TYPE_KEYWORDS = {
    "frontend": {"frontend", "ui", "client", "browser", "spa", "interface"},
    "database": {"database", "db", "storage", "persistence", "nosql"},
    "service": {"service", "api", "backend", "server", "gateway", "microservice"},
}

_LABEL_NOISE = {" component", " layer", " module", " group"}


def recognize_components(data, execution_id: str) -> list[dict]:
    hint_map = {kw.text: kw.hint for kw in data.detected_keywords}
    text_to_layer = {t: cg.name for cg in data.context_groups for t in cg.contains}

    components = []
    for idx, group in enumerate(data.grouped_elements, start=1):
        name = _clean_label(group.label)
        comp_type = _determine_type(group.label, group.texts, hint_map, text_to_layer)
        technology = _extract_technology(group.texts)
        aliases = [t for t in group.texts if t != group.label and t != name]

        components.append({
            "id": f"c{idx}",
            "name": name,
            "type": comp_type,
            "technology": technology,
            "aliases": aliases,
        })

    logger.info(
        "Components extracted",
        extra={
            "execution_id": execution_id,
            "count": len(components),
            "type_distribution": {
                t: sum(1 for c in components if c["type"] == t)
                for t in {c["type"] for c in components}
            },
        },
    )
    return components


def _clean_label(label: str) -> str:
    for noise in _LABEL_NOISE:
        if label.lower().endswith(noise):
            return label[: len(label) - len(noise)].strip()
    return label


def _determine_type(label: str, texts: list[str], hint_map: dict, text_to_layer: dict) -> str:
    for text in texts:
        hint = hint_map.get(text)
        if hint and hint in _HINT_TO_TYPE:
            return _HINT_TO_TYPE[hint]

    for text in texts + [label]:
        layer = text_to_layer.get(text, "").lower()
        if "frontend" in layer or "presentation" in layer or "ui" in layer:
            return "frontend"
        if "data" in layer or "database" in layer or "persistence" in layer:
            return "database"
        if "api" in layer or "service" in layer or "business" in layer:
            return "service"

    all_words = " ".join([label] + texts).lower()
    for comp_type, keywords in _TYPE_KEYWORDS.items():
        if any(kw in all_words for kw in keywords):
            return comp_type

    return "service"


def _extract_technology(texts: list[str]) -> str:
    for text in texts:
        if text.lower() in KNOWN_TECHNOLOGIES:
            return KNOWN_TECHNOLOGIES[text.lower()]
    for text in texts:
        matched = next((k for k in KNOWN_TECHNOLOGIES if k in text.lower()), None)
        if matched:
            return KNOWN_TECHNOLOGIES[matched]
    return ""
