"""Core functions for CTC Chatbot to get Families from the Revit API"""

# Imports
import os
from typing import Dict, Any
from dotenv import load_dotenv
import aiohttp
import asyncio

from core.tool_models import chat_memory
from ctc.data_models.families import RevitFamily, RevitFamilyType
from ctc.data_models.categories import RevitCategory
from ctc.data_models.sessions import RevitSession
from ctc.api_views import get_view_templates
from ctc.api_worksets import get_worksets

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

    print(f"Getting Families and Types for Category: {category.Name}")
    match category.Id:
        case "-2006000":  ## Scope Boxes
            try:
                scope_box_model = {"name": "Scope Box", "id": "-2006000"}
                scope_box_family = RevitFamily.model_validate(scope_box_model)
                scope_box_family.Types.append(
                    RevitFamilyType.model_validate(scope_box_model)
                )
                category.Families.append(scope_box_family)
                return {
                    "success": False,
                    "result": category,
                    "error": "Category not found",
                }
            except Exception as e:
                return {
                    "success": False,
                    "result": category,
                    "error": f"Error fetching scope boxes: {str(e)}",
                }
        case "2147483647":  ## View Templates
            try:
                view_template = await get_view_templates(
                    session=session,
                    category=category,
                )
                category = view_template["result"]
                return {
                    "success": True,
                    "result": category,
                }
            except Exception as e:
                return {
                    "success": False,
                    "result": category,
                    "error": f"Error fetching view templates: {str(e)}",
                }
        case "2147483648":  ## Worksets
            try:
                worksets = await get_worksets(
                    session=session,
                    category=category,
                )
                category = worksets["result"]
                return {
                    "success": True,
                    "result": category,
                }
            except Exception as e:
                return {
                    "success": False,
                    "result": category,
                    "error": f"Error fetching worksets: {str(e)}",
                }
        case "-2001352":  ## RVT Links
            return {
                "success": False,
                "result": category,
                "error": "Category not Implemented",
            }
        case _:
            async with aiohttp.ClientSession() as session:
                url = f"http://localhost:{revit_port}/api/v1/families"
                params = {
                    "apiKey": api_key,
                    "categoryId": category.Id,
                }

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
                    return {
                        "success": False,
                        "result": category,
                        "error": f"Error fetching families: {str(e)}",
                    }


# Prevent running from this file
if __name__ == "__main__":
    pass
