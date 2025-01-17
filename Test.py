# from core.main_entry import main

# asyncio.run(main())
from ctc.sessions import (
    get_sessions,
    RevitSessions,
)

if __name__ == "__main__":
    import asyncio

    test: RevitSessions = asyncio.run(get_sessions())
    print(test.model_dump())
