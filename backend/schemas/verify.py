from pydantic import BaseModel
from typing import List, Optional, Dict, Any

class VerificationRequest(BaseModel):
    url: str
    platform: str
    content_type: Optional[str] = None
    text: Optional[str] = None
    image_url: Optional[str] = None
    video_url: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class VerificationResponse(BaseModel):
    verification_id: str
    status: str
    summary: str
    evidence: str
    trusted_sources: List[str]
    related_articles: List[str]
    media_origin: Optional[str] = None
    evidence_quality: str
    evidence_quality_reason: str
    verification_timestamp: str
