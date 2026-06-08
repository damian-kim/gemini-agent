"""
app/schemas/brief.py
Pydantic schemas for the morning brief workflow state.
"""

from pydantic import BaseModel, Field
from typing import List

class BriefState(BaseModel):
    schema_version: str = Field("1.0", description="Schema version")
    last_brief_at: str = Field(..., description="ISO timestamp of last brief generation")
    last_brief_file: str = Field(..., description="Relative file path to the generated archive brief")
    summary: str = Field(..., description="Focus and summary of today's brief")
    top_priorities: List[str] = Field(default_factory=list, description="Top action priorities")
    open_questions: List[str] = Field(default_factory=list, description="Open questions or threads to track")