import time
from datetime import datetime
import asyncio
from typing import Dict, Any, Tuple

from backend.schemas.verify import VerificationRequest
from backend.core.redis_client import redis_client
from backend.core.queue_manager import queue_manager
from backend.core.logger import log_verification
from backend.trust.source_registry import source_registry

# Import engines
from backend.engines.text_engine import text_engine
from backend.engines.image_engine import image_engine
from backend.engines.video_engine import video_engine

class VerificationOrchestrator:
    def __init__(self):
        pass

    async def initiate_verification(self, request: VerificationRequest, background_tasks) -> dict:
        """
        Main entry point for verify requests. Checks cache, and launches background job if needed.
        """
        start_time = time.time()
        
        # 1. Generate fingerprint of payload
        fingerprint = redis_client.get_content_hash(request.model_dump())
        
        # 2. Check Redis cache
        cached_report = redis_client.get_cached_report(fingerprint)
        if cached_report:
            log_verification(
                verification_id=cached_report.get("verification_id", "cached"),
                processing_time_ms=(time.time() - start_time) * 1000,
                engine=self._determine_engine_name(request),
                cache_hit=True
            )
            return {
                "verification_id": cached_report.get("verification_id"),
                "status": "Completed",
                "progress": "Report retrieved from cache.",
                "result": cached_report
            }

        # 3. Cache miss: Create job
        verification_id = queue_manager.create_job()
        
        # 4. Dispatch background task to run engine
        background_tasks.add_task(
            self._run_verification_pipeline,
            verification_id=verification_id,
            request=request,
            fingerprint=fingerprint,
            start_time=start_time
        )

        return {
            "verification_id": verification_id,
            "status": "Queued",
            "progress": "Request received and queued for processing."
        }

    async def _run_verification_pipeline(
        self,
        verification_id: str,
        request: VerificationRequest,
        fingerprint: str,
        start_time: float
    ) -> None:
        engine_name = self._determine_engine_name(request)
        try:
            # Step A: Validate and start content extraction
            queue_manager.update_progress(verification_id, "Processing", "Extracting content and metadata...")
            await asyncio.sleep(1.0) # Yield control/simulate pipeline overhead

            # Step B: Identify targets and route to correct engine
            if engine_name == "video":
                queue_manager.update_progress(verification_id, "Processing", "Extracting speech tracks...")
                await asyncio.sleep(1.5)
                queue_manager.update_progress(verification_id, "Processing", "Analyzing key video frames...")
                await asyncio.sleep(1.5)
                queue_manager.update_progress(verification_id, "Processing", "Retrieving web references...")
                engine_result = await video_engine.verify(request.video_url, request.text)
            elif engine_name == "image":
                queue_manager.update_progress(verification_id, "Processing", "Performing context matching...")
                await asyncio.sleep(1.0)
                queue_manager.update_progress(verification_id, "Processing", "Scanning reverse visual indices...")
                await asyncio.sleep(1.0)
                engine_result = await image_engine.verify(request.image_url, request.text)
            else:
                queue_manager.update_progress(verification_id, "Processing", "Analyzing text claim syntax...")
                await asyncio.sleep(0.5)
                queue_manager.update_progress(verification_id, "Processing", "Searching trusted facts registries...")
                await asyncio.sleep(1.0)
                engine_result = await text_engine.verify(request.text)

            # Step C: Evaluate evidence credibility via Source Trust Layer
            queue_manager.update_progress(verification_id, "Processing", "Evaluating evidence source tiers...")
            await asyncio.sleep(0.5)
            
            sources = engine_result.get("trusted_sources", [])
            trust_quality, trust_reason = source_registry.evaluate_evidence(sources)

            # Step D: Compile final unified report
            from datetime import timezone
            report = {
                "verification_id": verification_id,
                "status": engine_result.get("status"),
                "summary": engine_result.get("summary"),
                "evidence": engine_result.get("evidence"),
                "trusted_sources": sources,
                "related_articles": engine_result.get("related_articles", []),
                "media_origin": engine_result.get("media_origin"),
                "evidence_quality": trust_quality,
                "evidence_quality_reason": trust_reason,
                "verification_timestamp": datetime.now(timezone.utc).isoformat()
            }

            # Step E: Save to Database (Mock/Supabase) and Cache in Redis
            from backend.database.supabase_client import supabase_db
            supabase_db.save_report(report)
            redis_client.cache_report(fingerprint, report)
            queue_manager.complete_job(verification_id, report)

            # Log execution stats
            log_verification(
                verification_id=verification_id,
                processing_time_ms=(time.time() - start_time) * 1000,
                engine=engine_name,
                cache_hit=False
            )

        except Exception as e:
            print(f"Error in verification pipeline: {str(e)}")
            queue_manager.fail_job(verification_id, str(e))
            log_verification(
                verification_id=verification_id,
                processing_time_ms=(time.time() - start_time) * 1000,
                engine=engine_name,
                cache_hit=False,
                errors=str(e)
            )

    def _determine_engine_name(self, request: VerificationRequest) -> str:
        content_type = request.content_type
        if content_type:
            return content_type.lower()
        if request.video_url:
            return "video"
        if request.image_url:
            return "image"
        return "text"

orchestrator = VerificationOrchestrator()
