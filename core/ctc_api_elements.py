"""Core functions for CTC API Elements"""

import os
from typing import Dict, Any
from dotenv import load_dotenv
import aiohttp

from core.ctc_tool_models import chat_memory

# Load environment variables from .env file in this directory
load_dotenv()
revit_port = os.getenv("REVIT_PORT")


# Revit Tool Implementations
async def get_elements(CategoryId: int) -> Dict[str, Any]:
    """API call to get the elements in the project"""
    api_key = os.getenv("CTC_API_KEY")
    if not api_key:
        raise ValueError("CTC_API_KEY not found in environment variables")

    async with aiohttp.ClientSession() as session:
        url = f"http://localhost:{revit_port}/api/v1/elements"
        params = {"apiKey": api_key, "categoryId": CategoryId}
        print(f"Parameters: {params}")

        try:
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    elements = await response.json()

                    # Store name to ID mappings
                    chat_memory.store_elements(elements)

                    return {"success": True, "result": elements}
                else:
                    return {
                        "success": False,
                        "error": f"Failed to fetch elements. Status code: {response.status}",
                    }
        except Exception as e:
            return {"success": False, "error": f"Error fetching elements: {str(e)}"}

    # async def create_element()
    """API call to create a new element in the project"""
