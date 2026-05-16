import logging

logger = logging.getLogger(__name__)

_ASYNC_KEYWORDS = {"kafka", "rabbitmq", "event", "async", "message", "queue", "publish", "subscribe"}
_QUERY_KEYWORDS = {"database_query", "sql", "query", "db", "database", "persist", "read", "write"}
_GRPC_KEYWORDS = {"grpc"}
_REST_KEYWORDS = {"http", "rest", "api", "graphql", "https", "request"}


def enrich_relationships(relationships: list[dict], components: list[dict], execution_id: str) -> list[dict]:
    comp_ids = {c["id"] for c in components if "id" in c}
    reverse_pairs = {
        (r.get("to"), r.get("from"))
        for r in relationships
    }

    async_count = 0
    sync_count = 0

    for rel in relationships:
        combined = " ".join([
            str(rel.get("type", "")),
            str(rel.get("protocol", "")),
            str(rel.get("description", "")),
        ]).lower()

        interaction_style = _determine_interaction_style(combined)
        synchrony = "asynchronous" if interaction_style == "event_driven" else "synchronous"

        from_id = rel.get("from", "")
        to_id = rel.get("to", "")
        if (from_id, to_id) in reverse_pairs and (to_id, from_id) in reverse_pairs:
            direction = "bidirectional"
        else:
            direction = "outbound"

        rel["interaction_style"] = interaction_style
        rel["synchrony"] = synchrony
        rel["direction"] = direction

        if synchrony == "asynchronous":
            async_count += 1
        else:
            sync_count += 1

    logger.info(
        "Relationship enrichment completed",
        extra={
            "execution_id": execution_id,
            "step": "enrichment",
            "relationships_enriched": len(relationships),
            "synchronous": sync_count,
            "asynchronous": async_count,
        },
    )
    return relationships


def _determine_interaction_style(combined: str) -> str:
    if any(kw in combined for kw in _ASYNC_KEYWORDS):
        return "event_driven"
    if any(kw in combined for kw in _QUERY_KEYWORDS):
        return "query"
    if any(kw in combined for kw in _GRPC_KEYWORDS):
        return "request_response"
    if any(kw in combined for kw in _REST_KEYWORDS):
        return "request_response"
    return "request_response"
