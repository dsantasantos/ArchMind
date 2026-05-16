import logging

logger = logging.getLogger(__name__)

_AUTH_KEYWORDS = {"auth", "authentication", "authorization", "oauth", "jwt", "sso", "identity", "login"}
_CACHE_TECH = {"cache_db"}
_MESSAGING_TECH_TYPE = {"messaging"}


def detect_gaps(components: list[dict], relationships: list[dict], execution_id: str) -> list[dict]:
    gaps: list[dict] = []

    component_names = " ".join(
        " ".join([c.get("name", ""), c.get("technology", ""), c.get("raw_technology", "")])
        for c in components
    ).lower()

    has_auth = any(kw in component_names for kw in _AUTH_KEYWORDS)
    has_cache = any(c.get("technology_normalized") in _CACHE_TECH for c in components)
    has_messaging = any(c.get("tech_type") in _MESSAGING_TECH_TYPE for c in components)
    has_async = any(r.get("synchrony") == "asynchronous" for r in relationships)

    if not has_auth:
        gaps.append({
            "type": "no_authentication_layer",
            "description": "No authentication or authorization component detected in the architecture.",
        })
    if not has_cache:
        gaps.append({
            "type": "no_cache_layer",
            "description": "No caching component detected. Consider adding a cache layer for performance.",
        })
    if not has_messaging:
        gaps.append({
            "type": "no_messaging_layer",
            "description": "No messaging or event broker component detected. Architecture is fully synchronous.",
        })
    if not has_async:
        gaps.append({
            "type": "no_async_communication",
            "description": "All detected relationships are synchronous. No asynchronous communication found.",
        })

    logger.info(
        "Gap detection completed",
        extra={
            "execution_id": execution_id,
            "step": "enrichment",
            "gaps_found": len(gaps),
            "gap_types": [g["type"] for g in gaps],
        },
    )
    return gaps
