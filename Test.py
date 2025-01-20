# from core.main_entry import main

# asyncio.run(main())
from ctc.sessions import (
    get_sessions,
    get_active_session,
    set_active_session,
    RevitSessions,
)

if __name__ == "__main__":
    import asyncio

    sessions: RevitSessions = asyncio.run(get_sessions())
    print(sessions)
    port = sessions["Sessions"][0]["Port"]
    asyncio.run(set_active_session(Port=port))
    session_active = asyncio.run(get_active_session())
    print(session_active)
