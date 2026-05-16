_REQUIRED_TYPES_THREE_TIER = {"frontend", "service", "database"}


def _has_three_tier(component_types: set[str]) -> bool:
    return _REQUIRED_TYPES_THREE_TIER.issubset(component_types)


def _has_microservices(components: list[dict]) -> bool:
    return sum(1 for c in components if c.get("type") == "service") >= 2


def _has_event_driven(output_model: dict) -> bool:
    return "event-driven" in output_model.get("communication_patterns", [])


def infer_architecture_style(components: list[dict], output_model: dict) -> None:
    component_types = {c.get("type") for c in components}

    event_driven = _has_event_driven(output_model)
    microservices = _has_microservices(components)
    three_tier = _has_three_tier(component_types)

    if event_driven and microservices:
        style = "event-driven microservices"
    elif event_driven and three_tier:
        style = "event-driven 3-tier architecture"
    elif event_driven:
        style = "event-driven architecture"
    elif microservices:
        style = "microservices"
    elif three_tier:
        style = "3-tier architecture"
    else:
        style = "unknown"

    output_model["architecture_style"] = style
