"""Core functions for CTC Chatbot to get Worksets from the Revit API"""
# Depricated

import os
from datetime import datetime
from typing import List, Dict, Any
from dotenv import load_dotenv
import aiohttp

from core.tool_models import chat_memory
from ctc.data_models.families import RevitFamily, RevitFamilyType
from ctc.data_models.categories import RevitCategory
from ctc.data_models.sessions import RevitSession

# Load environment variables from .env file in this directory


# Revit Tool Implementations
async def get_worksets(
    *,
    session: RevitSession,
    category: RevitCategory,
) -> RevitCategory:
    """Get the worksets in the project"""
    load_dotenv()
    revit_port = os.getenv("REVIT_PORT")
    api_key = os.getenv("CTC_API_KEY")
    if not api_key:
        raise ValueError("CTC_API_KEY not found in environment variables")

    async with aiohttp.ClientSession() as session:
        url = f"http://localhost:{revit_port}/api/v1/worksets"
        params = {"apiKey": api_key}

        try:
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    worksets = await response.json()

                    # Enter View Templates into Category
                    for workset in worksets:
                        workset = RevitFamily.model_validate(workset)
                        category.Families.append(workset)

                    return {"success": True, "result": category}
                else:
                    return {
                        "success": False,
                        "result": category,
                        "error": f"Failed to fetch view templates. Status code: {response.status}",
                    }
        except Exception as e:
            return {
                "success": False,
                "result": category,
                "error": f"Error fetching view templates: {str(e)}",
            }


# Prevent running from this file
if __name__ == "__main__":
    pass
