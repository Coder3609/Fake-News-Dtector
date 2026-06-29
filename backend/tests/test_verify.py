import pytest
from fastapi.testclient import TestClient
import uuid
import time

from backend.main import app
from backend.trust.source_registry import source_registry
from backend.core.redis_client import redis_client

client = TestClient(app)

def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "TruthLens Backend"

def test_verify_validation_errors():
    # Empty payload
    response = client.post("/api/v1/verify", json={})
    assert response.status_code == 422
    
    # Missing platform
    response = client.post("/api/v1/verify", json={"url": "https://example.com"})
    assert response.status_code == 422

def test_source_trust_layer():
    # Tier 1 checks
    assert source_registry.get_source_tier("https://www.reuters.com/article/123") == 1
    assert source_registry.get_source_tier("https://nasa.gov/news") == 1
    assert source_registry.get_source_tier("https://cdc.gov") == 1
    
    # Tier 2 checks
    assert source_registry.get_source_tier("https://www.nytimes.com/2026/06") == 2
    assert source_registry.get_source_tier("https://harvard.edu") == 2
    
    # Tier 4 checks
    assert source_registry.get_source_tier("https://twitter.com/nasa") == 4
    assert source_registry.get_source_tier("https://reddit.com/r/science") == 4
    
    # Aggregate Evaluation
    quality, reason = source_registry.evaluate_evidence([
        "https://reuters.com/1", "https://apnews.com/2"
    ])
    assert quality == "High"
    assert "multiple Tier 1" in reason

    quality, reason = source_registry.evaluate_evidence([
        "https://twitter.com/1", "https://reddit.com/2"
    ])
    assert quality == "Low"

def test_redis_fingerprint():
    payload1 = {
        "url": "https://x.com/nasa",
        "platform": "x",
        "text": "Temperature anomalies confirmed.",
        "image_url": None,
        "video_url": None
    }
    payload2 = {
        "url": "https://x.com/nasa",
        "platform": "x",
        "text": "Temperature anomalies confirmed.",
        "image_url": None,
        "video_url": None,
        "metadata": {"timestamp": "different"} # Metadata should not alter fingerprint
    }
    
    hash1 = redis_client.get_content_hash(payload1)
    hash2 = redis_client.get_content_hash(payload2)
    assert hash1 == hash2

def test_verify_caching_and_queue():
    payload = {
        "url": "https://x.com/test-fact",
        "platform": "x",
        "text": "Fact-checking cache hits.",
        "image_url": None,
        "video_url": None
    }
    
    # 1. First request -> Misses cache, returns queued job
    response = client.post("/api/v1/verify", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "Queued"
    verification_id = data["verification_id"]
    
    # Wait for the background task to complete (simulation sleep blocks are run concurrently)
    # Since we sleep for ~1-2s in text_engine, let's wait 3.5 seconds
    time.sleep(3.5)
    
    # 2. Check status via report endpoint -> Should be completed
    rep_res = client.get(f"/api/v1/report/{verification_id}")
    assert rep_res.status_code == 200
    rep_data = rep_res.json()
    assert rep_data["status"] == "Completed"
    assert rep_data["result"]["evidence_quality"] == "High" # Tavily mock returns 2 Tier 1 sources
    
    # 3. Second request -> Cache hit, returns completed job immediately
    cache_res = client.post("/api/v1/verify", json=payload)
    assert cache_res.status_code == 200
    cache_data = cache_res.json()
    assert cache_data["status"] == "Completed"
    assert cache_data["progress"] == "Report retrieved from cache."
    assert cache_data["verification_id"] == verification_id
