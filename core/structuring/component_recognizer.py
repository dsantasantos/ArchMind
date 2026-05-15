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

_NAME_PREFERRED_SUFFIXES = {"service", "application", "server", "client", "manager", "handler", "processor"}

_LABEL_NOISE = {" component", " layer", " module", " group"}


def recognize_components(data) -> list[dict]:
    hint_map = {kw.text: kw.hint for kw in data.detected_keywords}

    text_to_layer: dict[str, str] = {}
    for cg in data.context_groups:
        for t in cg.contains:
            text_to_layer[t] = cg.name

    components = []
    for idx, group in enumerate(data.grouped_elements, start=1):
        comp_type = _determine_type(group.label, group.texts, hint_map, text_to_layer)
        name, technology, aliases = _categorize_texts(group.label, group.texts)
        components.append({
            "id": f"c{idx}",
            "name": name,
            "type": comp_type,
            "technology": technology,
            "aliases": aliases,
        })

    return components


def _determine_type(label: str, texts: list[str], hint_map: dict, text_to_layer: dict) -> str:
    for text in texts:
        hint = hint_map.get(text)
        if hint and hint in _HINT_TO_TYPE:
            return _HINT_TO_TYPE[hint]

    for text in texts + [label]:
        layer = text_to_layer.get(text, "")
        layer_lower = layer.lower()
        if "frontend" in layer_lower or "presentation" in layer_lower or "ui" in layer_lower:
            return "frontend"
        if "data" in layer_lower or "database" in layer_lower or "persistence" in layer_lower:
            return "database"
        if "api" in layer_lower or "service" in layer_lower or "business" in layer_lower:
            return "service"

    all_words = " ".join([label] + texts).lower()
    for comp_type, keywords in _TYPE_KEYWORDS.items():
        if any(kw in all_words for kw in keywords):
            return comp_type

    return "service"


def _categorize_texts(label: str, texts: list[str]) -> tuple[str, str, list[str]]:
    tech_exact: list[tuple[str, str]] = []
    tech_compound: list[tuple[str, str]] = []
    name_candidates: list[str] = []

    for text in texts:
        lower = text.lower()
        if lower in KNOWN_TECHNOLOGIES:
            tech_exact.append((text, KNOWN_TECHNOLOGIES[lower]))
        else:
            matched_key = next((k for k in KNOWN_TECHNOLOGIES if k in lower), None)
            if matched_key:
                tech_compound.append((text, KNOWN_TECHNOLOGIES[matched_key]))
            else:
                name_candidates.append(text)

    technology = ""
    if tech_exact:
        technology = tech_exact[0][1]
    elif tech_compound:
        technology = tech_compound[0][1]

    name = _select_name(name_candidates, label)

    aliases = [t for t in name_candidates if t != name] + [t for t, _ in tech_compound]

    return name, technology, aliases


def _select_name(candidates: list[str], label: str) -> str:
    if not candidates:
        clean_label = label
        for noise in _LABEL_NOISE:
            clean_label = clean_label.replace(noise, "").replace(noise.title(), "")
        return clean_label.strip()

    def score(text: str) -> tuple[int, int]:
        words = text.split()
        last_word_lower = words[-1].lower() if words else ""
        suffix_bonus = 1 if last_word_lower in _NAME_PREFERRED_SUFFIXES else 0
        return (len(words), suffix_bonus)

    return max(candidates, key=score)
