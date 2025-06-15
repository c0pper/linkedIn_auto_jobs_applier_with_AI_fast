from fastapi import APIRouter, HTTPException
from pathlib import Path
from core.session_manager import SessionManager
from src.models.schemas import ActiveSession, ActiveSessionsResponse, BotConfig, BotResponse, BotStatus, BotStatusResponse

router = APIRouter()
manager = SessionManager()

@router.post("/start", response_model=BotResponse)
async def start_bot(config: BotConfig):
    """Start a new bot session with given configuration"""
    try:
        result = manager.start_bot(
            session_id=config.session_id,
            config_path=Path(config.config_path),
            secrets_path=Path(config.secrets_path),
            resume_path=Path(config.resume_path) if config.resume_path else None
        )
        return BotResponse(
            status=BotStatus.RUNNING if result['status'] == 'success' else BotStatus.ERROR,
            message=result['message'],
            session_id=config.session_id
        )
    except Exception as e:
        return BotResponse(
            status=BotStatus.ERROR,
            message=str(e)
        )

@router.get("/status/{session_id}", response_model=BotStatusResponse)
async def get_status(session_id: str):
    """Get current status of a bot session"""
    result = manager.get_status(session_id)
    return BotStatusResponse(
        status=BotStatus.RUNNING if result.get('is_running', False) else BotStatus.STOPPED,
        message=result['message'],
        session_id=session_id,
        is_running=result.get('is_running', False)
    )

@router.post("/stop", response_model=BotResponse)
async def stop_bot(session_id: str):
    """
    Stop a running bot session
    
    Args:
        session_id: ID of the session to stop (from /start response)
        
    Returns:
        BotResponse with operation status:
        - status: "stopped" on success, "error" if session not found
        - message: Detailed status message
        - session_id: The stopped session ID
    """
    result = manager.stop_bot(session_id)
    
    return BotResponse(
        status=BotStatus.STOPPED if result['status'] == 'success' else BotStatus.ERROR,
        message=result['message'],
        session_id=session_id,
        details={
            'force_terminated': result.get('force_terminated', False),
            'active_time': result.get('active_time')
        }
    )

@router.get("/sessions/active", response_model=ActiveSessionsResponse)
async def get_active_sessions():
    """
    Get list of all currently active bot sessions
    
    Returns:
        - List of active sessions with their stats
        - Total number of jobs applied across all sessions
        - Total count of active sessions
    """
    result = manager.get_active_sessions()
    return ActiveSessionsResponse(
        active_sessions=[
            ActiveSession(**session) for session in result['active_sessions']
        ],
        # total_jobs_applied=result['total_jobs_applied'],
        total_active_sessions=result['total_active_sessions']
    )