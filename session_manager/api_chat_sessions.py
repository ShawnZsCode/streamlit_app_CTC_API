"""Tools to manage sessions."""

from session_manager.api_chat_sessions import ChatSession, ChatSessions
from utils.file_utils import read_file_json, write_file_json

BASE_PATH = read_file_json("session_manager\\Settings.json")["files"]["chatSessions"]


# Primary Functions
def create_session() -> ChatSession:
    """Create a new session."""
    return ChatSession()


def get_sessions() -> ChatSessions:
    """Get all sessions."""
    try:
        sessions: ChatSessions = read_file_json(f"{BASE_PATH}\\Sessions_List.json")
    except Exception:
        sessions = ChatSessions()
    return sessions


def save_session(session: ChatSession) -> None:
    """Save a session."""
    sessions = get_sessions()
    sessions.Sessions.append(session)
    write_file_json(
        stream=sessions.model_dump_json(),
        file_name="Sessions_List",
        folder="",
    )


# Prevent running from this file
if __name__ == "__main__":
    pass
