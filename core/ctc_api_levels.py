"""Core functions for CTC API Levels"""

import os
from typing import Dict, Any
from dotenv import load_dotenv
import aiohttp

from core.ctc_tool_models import chat_memory

# Load environment variables from .env file in this directory
load_dotenv()
revit_port = os.getenv("REVIT_PORT")


# Revit Tool Implementations
async def get_levels() -> Dict[str, Any]:
    """API call to get the levels in the project"""
    api_key = os.getenv("CTC_API_KEY")
    if not api_key:
        raise ValueError("CTC_API_KEY not found in environment variables")

    async with aiohttp.ClientSession() as session:
        url = f"http://localhost:{revit_port}/api/v1/levels"
        params = {"apiKey": api_key}

        try:
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    levels = await response.json()

                    # Store name to ID mappings
                    chat_memory.store_levels(levels)

                    return {"success": True, "result": levels}
                else:
                    return {
                        "success": False,
                        "error": f"Failed to fetch levels. Status code: {response.status}",
                    }
        except Exception as e:
            return {"success": False, "error": f"Error fetching levels: {str(e)}"}

    # async def create_level()
    """API call to create a new level in the project"""
