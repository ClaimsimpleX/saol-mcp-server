from pydantic import BaseModel, Field
from typing import Dict, Optional
from enum import Enum
from datetime import datetime

class MissionStatus(str, Enum):
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    BLOCKED = "BLOCKED"

class MissionReceipt(BaseModel):
    """
    The Final Packet: A receipt of the Spoke's execution.
    """
    ticket_id: str
    spoke_id: str
    profile: str
    start_time: datetime
    end_time: datetime
    tokens_input: int = 0
    tokens_output: int = 0
    tool_usage: Dict[str, int] = Field(default_factory=dict)
    status: MissionStatus
    outcome_summary: Optional[str] = None
