from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException, BackgroundTasks
from backend.schemas.verify import VerificationRequest
from backend.core.orchestrator import orchestrator
from backend.core.queue_manager import queue_manager

router = APIRouter()

@router.post("/verify")
async def verify_content(request: VerificationRequest, background_tasks: BackgroundTasks):
    try:
        # Check cache or kick off background verification pipeline
        response = await orchestrator.initiate_verification(request, background_tasks)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/report/{verification_id}")
async def get_report(verification_id: str):
    try:
        # Retrieve active status, progress logs, or final result
        status_info = queue_manager.get_status(verification_id)
        return status_info
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/report/save")
async def save_report(payload: dict):
    from backend.database.supabase_client import supabase_db
    report = payload.get("report")
    if not report:
        raise HTTPException(status_code=400, detail="Missing report payload")
    
    success = supabase_db.save_report(report)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to save report to Supabase")
        
    return {
        "status": "success",
        "message": "Report successfully persisted in Supabase"
    }

@router.post("/auth/login")
async def login(payload: dict):
    # Placeholder for Supabase JWT verification
    return {
        "status": "success",
        "token": "mock-session-token-from-supabase"
    }

@router.get("/history")
async def get_history():
    from backend.database.supabase_client import supabase_db
    history = supabase_db.get_user_history()
    return {
        "status": "success",
        "history": history
    }
