"""toolset to read the active sessions from the CTC sessions folder"""

from os import environ
from typing import List, Optional, Dict

from dotenv import load_dotenv, find_dotenv, set_key
from pydantic import ValidationError
from utils.read_file import read_file_json
from ctc.data_models.sessions import RevitSession, RevitSessions
from ctc.api_projects import get_active_project


# Functions
## get active sessions
async def get_sessions() -> List[Dict[str, any]]:
    """Reads the active sessions from the CTC sessions folder"""
    try:
        file_path: str = f"{environ['LOCALAPPDATA']}\\CTC Software\\BIM Automation\\BIM Automation API Instances.json"
        file_json = read_file_json(file_path)
        rvt_sessions = RevitSessions()
        # RevitSessions.model_validate(file_json)
        for session in file_json:
            rvt_session: RevitSession = RevitSession.model_validate(session)
            rvt_session = await get_active_model(rvt_session)
            rvt_sessions.Sessions.append(rvt_session)

        # sessions: RevitSessions = RevitSessions.model_validate(file_json)
    except ValidationError:
        rvt_sessions = RevitSessions()

    rvt_sessions.update(Count=rvt_sessions.Sessions.__len__())
    return rvt_sessions.model_dump()


## fetch and record the active model for each session in revitsessions
async def get_active_model(revit_session: RevitSession) -> RevitSession:
    """Fetches and records the active model for each session in RevitSessions"""
    try:
        port: int = revit_session.Port
        response = await get_active_project(port)
        if "title" in response["result"].keys():
            # temporary handling response in 2025
            active = response["result"]["title"]
        else:
            # temporary handling response in 2021
            active = response["result"]["Title"]
        revit_session.update(ActiveProject=active)
    except Exception as e:
        revit_session.update(ActiveProject="")
    return revit_session


## return the active session
async def get_active_session() -> Dict[str, any]:
    """Returns the active session from the settings in the dotenv file"""
    try:
        load_dotenv()
        port = int(environ["REVIT_PORT"])
        rvt_sessions = await get_sessions()
        for session in rvt_sessions["Sessions"]:
            if session["Port"] == port:
                return session
    except Exception as e:
        print(e)
        session = RevitSession()
        return session.model_dump()


## set the active session/port in the .env file by direct input or by active model
async def set_active_session(Port: int = 0, ActiveProject: str = "") -> Dict[str, any]:
    """Sets the active port in the .env file by direct input or by active model"""

    rvt_session: RevitSession = RevitSession.model_validate(
        {"RevitVersion": "", "Port": 0}
    )
    rvt_session = rvt_session.model_dump()
    try:
        rvt_sessions = await get_sessions()
        if Port == 0:
            for session in rvt_sessions["Sessions"]:
                if session["ActiveProject"] == ActiveProject:
                    rvt_session = session
                    Port = rvt_session["Port"]
        else:
            for session in rvt_sessions["Sessions"]:
                if session["Port"] == Port:
                    rvt_session = session
        dotenv_file = find_dotenv()
        load_dotenv(dotenv_file, override=True)

        environ["REVIT_PORT"] = str(Port)
        set_key(dotenv_file, "REVIT_PORT", environ["REVIT_PORT"])
    except Exception as e:
        print(e)

    return rvt_session
