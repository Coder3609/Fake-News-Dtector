import json
import hashlib
from typing import Optional, Any
from upstash_redis import Redis as UpstashRedis
from backend.core.config import settings

class RedisClient:
    def __init__(self):
        self.url = settings.UPSTASH_REDIS_REST_URL
        self.token = settings.UPSTASH_REDIS_REST_TOKEN
        
        self.client = None
        self.fallback_db = {}  # In-memory database fallback for development resilience
        self.is_fallback = False

        try:
            if not self.url or not self.token:
                raise ValueError("Missing Upstash Redis credentials")
            self.client = UpstashRedis(url=self.url, token=self.token)
            # Test connection
            self.client.ping()
            print(f"[TruthLens Redis] Connected to Upstash Redis server via REST.")
        except Exception as e:
            self.is_fallback = True
            print(f"[TruthLens Redis] Redis connection failed ({str(e)}). Falling back to in-memory store.")

    def get_content_hash(self, payload: dict) -> str:
        """
        Generate a unique MD5 fingerprint representing the verification request payload.
        """
        # Filter payload for significant fields only to prevent timestamp mismatches from invalidating cache
        hash_keys = ["url", "platform", "text", "image_url", "video_url"]
        filtered = {k: payload.get(k) for k in hash_keys if payload.get(k) is not None}
        
        # Serialize sorted keys
        serialized = json.dumps(filtered, sort_keys=True)
        return hashlib.md5(serialized.encode("utf-8")).hexdigest()

    def get_cached_report(self, fingerprint: str) -> Optional[dict]:
        key = f"truthlens:cache:{fingerprint}"
        if self.is_fallback:
            return self.fallback_db.get(key)
        try:
            val = self.client.get(key)
            return json.loads(val) if val else None
        except Exception as e:
            print(f"Redis cache read error: {e}")
            return self.fallback_db.get(key)

    def cache_report(self, fingerprint: str, report: dict, ttl: int = 3600) -> None:
        key = f"truthlens:cache:{fingerprint}"
        if self.is_fallback:
            self.fallback_db[key] = report
            return
        try:
            self.client.setex(key, ttl, json.dumps(report))
        except Exception as e:
            print(f"Redis cache write error: {e}")
            self.fallback_db[key] = report

    def set_job_state(self, verification_id: str, status: str, progress: str = "", result: dict = None, ttl: int = 600) -> None:
        key = f"truthlens:job:{verification_id}"
        job_data = {
            "verification_id": verification_id,
            "status": status,
            "progress": progress,
            "result": result
        }
        if self.is_fallback:
            self.fallback_db[key] = job_data
            return
        try:
            self.client.setex(key, ttl, json.dumps(job_data))
        except Exception as e:
            print(f"Redis job write error: {e}")
            self.fallback_db[key] = job_data

    def get_job_state(self, verification_id: str) -> Optional[dict]:
        key = f"truthlens:job:{verification_id}"
        if self.is_fallback:
            return self.fallback_db.get(key)
        try:
            val = self.client.get(key)
            return json.loads(val) if val else None
        except Exception as e:
            print(f"Redis job read error: {e}")
            return self.fallback_db.get(key)

    def delete_job_state(self, verification_id: str) -> None:
        key = f"truthlens:job:{verification_id}"
        if self.is_fallback:
            if key in self.fallback_db:
                del self.fallback_db[key]
            return
        try:
            self.client.delete(key)
        except Exception as e:
            print(f"Redis job delete error: {e}")
            if key in self.fallback_db:
                del self.fallback_db[key]

redis_client = RedisClient()
