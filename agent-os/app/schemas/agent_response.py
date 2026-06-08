"""
app/schemas/agent_response.py
Pydantic schemas for chat and agent tool-execution responses.
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class ChatRequest(BaseModel):
    message: str = Field(..., description="Message input to the agent")
    domain: str = Field("personal-os", description="Domain context namespace")
    allow_writes: bool = Field(False, description="Whether the request allows write actions")
    approval_token: Optional[str] = Field(None, description="Approval token if a destructive action was proposed")

class AgentResponse(BaseModel):
    request_id: str = Field(..., description="Unique request identifier")
    answer: str = Field(..., description="Structured text answer from the agent")
    actions_taken: List[Dict[str, Any]] = Field(default_factory=list, description="List of actions executed during this invocation")
    actions_requiring_approval: List[Dict[str, Any]] = Field(default_factory=list, description="List of actions requiring explicit human approval")
    files_read: List[str] = Field(default_factory=list, description="List of absolute or relative file paths read")
    files_written: List[str] = Field(default_factory=list, description="List of absolute or relative file paths written")