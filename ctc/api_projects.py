"""Core functions for CTC Chatbot to get Projects from the Revit API"""

import os
from datetime import datetime
from typing import Dict, Any
from dotenv import load_dotenv
import aiohttp

from core.tool_models import chat_memory

# Load environment variables from .env file in this directory


# Revit Tool Implementations
async def get_active_project(port: int = -1) -> Dict[str, Any]:
    """Get active project open in Revit right now"""
    load_dotenv()
    if port == -1:
        revit_port = os.getenv("REVIT_PORT")
    else:
        revit_port = port
    api_key = os.getenv("CTC_API_KEY")
    if not api_key:
        raise ValueError("CTC_API_KEY not found in environment variables")

    async with aiohttp.ClientSession() as session:
        url = f"http://localhost:{revit_port}/api/v1/projects/active"
        params = {"apiKey": api_key}

        try:
            async with session.get(url=url, params=params) as response:
                if response.status == 200:
                    project_data = await response.json()

                    # Store in memory
                    chat_memory.context_data["active_project"] = project_data
                    chat_memory.context_data["active_project_last_updated"] = (
                        datetime.now()
                    )

                    return {"success": True, "result": project_data}
                else:
                    return {
                        "success": False,
                        "error": f"Failed to fetch active project. Status code: {response.status}",
                    }
        except Exception as e:
            return {
                "success": False,
                "error": f"Error fetching active project: {str(e)}",
            }


# Prevent running from this file
if __name__ == "__main__":
    pass
