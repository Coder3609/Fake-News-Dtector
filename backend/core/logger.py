import json
import sys
import time

def log_verification(
    verification_id: str,
    processing_time_ms: float,
    engine: str,
    cache_hit: bool,
    errors: str = None,
    api_usage: dict = None
) -> None:
    """
    Generate PII-free structured logs for verification metrics.
    """
    log_entry = {
        "event": "verification_metric",
        "verification_id": verification_id,
        "processing_time_ms": round(processing_time_ms, 2),
        "engine": engine,
        "cache_hit": cache_hit,
        "errors": errors,
        "api_usage": api_usage or {"llm_calls": 1, "search_calls": 1}
    }
    sys.stdout.write(json.dumps(log_entry) + "\n")
    sys.stdout.flush()
