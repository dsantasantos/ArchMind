_PATTERN_RULES: list[tuple[set[str], list[str]]] = [
    ({"synchronous_request"}, ["synchronous communication", "request-response"]),
    ({"event_publish", "event_consume"}, ["event-driven", "asynchronous communication"]),
    ({"queue_message"}, ["asynchronous communication"]),
]


def recognize_communication_patterns(relationships: list[dict], output_model: dict) -> None:
    rel_types = {r.get("type") for r in relationships}
    patterns: set[str] = set()

    for trigger_types, labels in _PATTERN_RULES:
        if trigger_types & rel_types:
            patterns.update(labels)

    output_model["communication_patterns"] = sorted(patterns)
