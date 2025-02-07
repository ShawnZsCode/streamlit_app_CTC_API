"""Core functions for CTC Chatbot to get Families from the Revit API"""

# Imports
import os
from typing import Dict, Any
from dotenv import load_dotenv
import aiohttp

from core.tool_models import chat_memory
from ctc.data_models.families import RevitFamily, RevitFamilyType
from ctc.data_models.categories import RevitCategory
from ctc.data_models.sessions import RevitSession

# Load environment variables from .env file in this directory


# Revit Tool Implementations
async def get_families(
    *,
    session: RevitSession,
    category: RevitCategory,
) -> RevitCategory:
    """API call to get the families in the project"""
    load_dotenv()
    api_key = os.getenv("CTC_API_KEY")
    revit_port = session.Port
    if not api_key:
        raise ValueError("CTC_API_KEY not found in environment variables")

    async with aiohttp.ClientSession() as session:
        url = f"http://localhost:{revit_port}/api/v1/families"
        params = {
            "apiKey": api_key,
            "categoryId": category.Id,
        }
        print(f"Parameters: {params}")

        try:
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    families = await response.json()

                    # Enter families into RevitCategory
                    for family in families:
                        family = RevitFamily.model_validate(family)
                        category.Families.append(family)

                    return {"success": True, "result": category}
                else:
                    return {
                        "success": False,
                        "result": category,
                        "error": f"Failed to fetch families. Status code: {response.status}",
                    }
        except Exception as e:
            return {"success": False, "error": f"Error fetching families: {str(e)}"}


# Prevent running from this file
if __name__ == "__main__":
    pass
