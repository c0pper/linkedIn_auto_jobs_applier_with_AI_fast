from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum

class ActiveSession(BaseModel):
    session_id: str
    start_time: str
    jobs_applied: Optional[int] = 0
    current_position: Optional[str] = None
    current_company: Optional[str] = None

class ActiveSessionsResponse(BaseModel):
    active_sessions: List[ActiveSession]
    total_jobs_applied: Optional[int] = 0
    total_active_sessions: int

class BotStatus(str, Enum):
    RUNNING = "running"
    STOPPED = "stopped"
    ERROR = "error"

class BotConfig(BaseModel):
    """
    Configuration for starting the LinkedIn bot
    """
    session_id: str = Field(
        ...,
        description="Unique identifier for this bot session",
        example="session_123"
    )
    config_path: str = Field(
        ...,
        description="Path to config.yaml file",
        example="data_folder/config.yaml"
    )
    secrets_path: str = Field(
        ...,
        description="Path to secrets.yaml file",
        example="data_folder/secrets.yaml"
    )
    resume_path: Optional[str] = Field(
        None,
        description="Optional path to resume PDF file",
        example="data_folder/resume.pdf"
    )

class BotResponse(BaseModel):
    """
    Standard response format for bot operations
    """
    status: BotStatus
    message: str
    session_id: Optional[str] = None
    details: Optional[dict] = None

class BotStatusResponse(BotResponse):
    """
    Extended response for status checks
    """
    is_running: bool = Field(
        ...,
        description="Whether the bot is currently running"
    )
    jobs_applied: Optional[int] = Field(
        None,
        description="Number of jobs applied to in this session"
    )
    last_activity: Optional[str] = Field(
        None,
        description="Timestamp of last activity",
        example="2023-07-15T14:30:00Z"
    )
