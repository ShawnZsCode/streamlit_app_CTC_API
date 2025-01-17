"""toolset to read the active sessions from the CTC sessions folder"""

from typing import List, Optional
from pydantic import BaseModel, ValidationError, Field
from utils.read_file import read_file

from ctc.api_projects import get_active_project


# Class Definitions
class LocalBaseModel(BaseModel):
    """Local Base model defines a function for easy updating of fields"""

    def update(self, **kwargs):
        for field, value in kwargs.items():
            if hasattr(self, field):
                setattr(self, field, value)


class RevitSession(LocalBaseModel):
    """Revit session model"""

    RevitVersion: str
    Port: int
    ActiveProject: Optional[str] = ""


class RevitSessions(LocalBaseModel):
    """Revit sessions model"""

    Count: int = 0
    Sessions: List[RevitSession] = []


# Functions
## get active sessions
async def get_sessions() -> RevitSessions:
    """Reads the active sessions from the CTC sessions folder"""
    try:
        file_path: str = "C:\\Users\\shawnz\\AppData\\Local\\CTC Software\\BIM Automation\\BIM Automation API Instances.json"
        file_json = read_file(file_path)
        rvt_sessions = RevitSessions()
        # RevitSessions.model_validate(file_json)
        for session in file_json:
            session: RevitSession = RevitSession.model_validate(session)
            await get_active_model(session)
            rvt_sessions.Sessions.append(session)

        # sessions: RevitSessions = RevitSessions.model_validate(file_json)
    except ValidationError:
        rvt_sessions = RevitSessions()

    rvt_sessions.update(Count=rvt_sessions.Sessions.__len__())
    return rvt_sessions


## fetch and record the active model for each session in revitsessions
async def get_active_model(revit_session: RevitSession) -> RevitSession:
    """Fetches and records the active model for each session in RevitSessions"""
    try:
        port: int = revit_session.Port
        response = await get_active_project(port)
        if "title" in response["result"].keys():
            active = response["result"]["title"]
        else:
            active = response["result"]["Title"]
        revit_session.update(ActiveProject=active)
    except Exception as e:
        revit_session.update(ActiveProject="")
    return revit_session
