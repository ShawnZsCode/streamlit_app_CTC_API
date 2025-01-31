"""Pydantic Models for Chat Session Logging and Management."""

from pydantic import BaseModel, Field
from uuid import UUID, uuid4
from datetime import datetime
from typing import List, Optional


# Definition of Class Models
class ChatSession(BaseModel):
    """Model for a chat session."""

    Id: UUID = Field(
        default=uuid4, description="Unique identifier for the chat session."
    )
    Start_Time: str = Field(
        default=datetime.now().strftime("%Y-%m-%d_%H-%M"),
        description="Start time of the chat session.",
    )
    SessionOpen: Optional[bool] = Field(
        default=True, description="Indicates if the session is open."
    )
    RevitPort: Optional[int] = Field(description="Port number for the Revit API.")
    RevitVersion: Optional[str] = Field(
        description="Version of the Revit software used in the session."
    )


class ChatSessions(BaseModel):
    """Model for managing multiple chat sessions."""

    Sessions: List[ChatSession] = Field(
        default=[], description="List of active chat sessions."
    )


# Prevent running from this file
if __name__ == "__main__":
    pass
