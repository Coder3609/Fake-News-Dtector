import uuid
from backend.core.redis_client import redis_client

class QueueManager:
    def create_job(self) -> str:
        """
        Create a new verification job in Redis and return its ID.
        """
        verification_id = str(uuid.uuid4())
        redis_client.set_job_state(
            verification_id=verification_id,
            status="Queued",
            progress="Job added to verification queue."
        )
        return verification_id

    def update_progress(self, verification_id: str, status: str, progress: str) -> None:
        """
        Update the current progress string and status.
        """
        # Maintain current result if any
        current = redis_client.get_job_state(verification_id)
        result = current.get("result") if current else None
        
        redis_client.set_job_state(
            verification_id=verification_id,
            status=status,
            progress=progress,
            result=result
        )

    def complete_job(self, verification_id: str, result: dict) -> None:
        """
        Store the final result and mark job as completed.
        """
        redis_client.set_job_state(
            verification_id=verification_id,
            status="Completed",
            progress="Verification completed successfully.",
            result=result
        )

    def fail_job(self, verification_id: str, error_msg: str) -> None:
        """
        Mark the job as failed with details.
        """
        redis_client.set_job_state(
            verification_id=verification_id,
            status="Failed",
            progress=f"Verification failed: {error_msg}"
        )

    def get_status(self, verification_id: str) -> dict:
        """
        Query the current job status and progress.
        """
        state = redis_client.get_job_state(verification_id)
        if not state:
            return {
                "verification_id": verification_id,
                "status": "Failed",
                "progress": "Job not found in queue cache.",
                "result": None
            }
        return state

    def clean_job(self, verification_id: str) -> None:
        """
        Remove the temporary job state from Redis.
        """
        redis_client.delete_job_state(verification_id)

queue_manager = QueueManager()
