"""Core functions for CTC Chatbot to get Views from the Revit API"""
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
async def get_views() -> Dict[str, Any]:
    """Retrieves all the floor plans and 3D views in the project"""
    load_dotenv()
    revit_port = os.getenv("REVIT_PORT")
    api_key = os.getenv("CTC_API_KEY")
    if not api_key:
        raise ValueError("CTC_API_KEY not found in environment variables")

    async with aiohttp.ClientSession() as session:
        url = f"http://localhost:{revit_port}/api/v1/views"
        params = {"apiKey": api_key}

        try:
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    views = await response.json()

                    # Store raw data in memory
                    chat_memory.store_views(views)

                    return {"success": True, "result": views}
                else:
                    return {
                        "success": False,
                        "error": f"Failed to fetch views. Status code: {response.status}",
                    }
        except Exception as e:
            return {"success": False, "error": f"Error fetching views: {str(e)}"}


async def get_view_templates(
    *,
    session: RevitSession,
    category: RevitCategory,
) -> RevitCategory:
    """Get the view templates in the project"""
    load_dotenv()
    revit_port = os.getenv("REVIT_PORT")
    api_key = os.getenv("CTC_API_KEY")
    if not api_key:
        raise ValueError("CTC_API_KEY not found in environment variables")

    async with aiohttp.ClientSession() as session:
        url = f"http://localhost:{revit_port}/api/v1/views/templates"
        params = {"apiKey": api_key}

        try:
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    templates = await response.json()

                    # Enter View Templates into Category
                    for template in templates:
                        template = RevitFamily.model_validate(template)
                        category.Families.append(template)

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


async def create_floor_plan(
    Name: str,
    LevelId: int,
    ViewTemplateId: int,
    ScopeBoxId: int = 0,
) -> Dict[str, Any]:
    """Create new floor plan in the project"""
    load_dotenv()
    revit_port = os.getenv("REVIT_PORT")
    api_key = os.getenv("CTC_API_KEY")
    if not api_key:
        raise ValueError("CTC_API_KEY not found in environment variables")

    async with aiohttp.ClientSession() as session:
        url = f"http://localhost:{revit_port}/api/v1/views/floor-plan"
        params = {"apiKey": api_key}

        # Prepare request body
        data = {
            "Name": Name,
            "LevelId": LevelId,
            "ViewTemplateId": ViewTemplateId,
            "ScopeBoxId": ScopeBoxId,
        }

        try:
            async with session.post(url, params=params, json=data) as response:
                if response.status == 200:
                    new_view = await response.json()

                    # Store in memory with existing views
                    existing_views = chat_memory.get_views()
                    if existing_views:
                        existing_views.append(new_view)
                        chat_memory.store_views(existing_views)

                    return {"success": True, "result": new_view}
                else:
                    return {
                        "success": False,
                        "error": f"Failed to create floor plan. Status code: {response.status}",
                    }
        except Exception as e:
            return {"success": False, "error": f"Error creating floor plan: {str(e)}"}


# Prevent running from this file
if __name__ == "__main__":
    pass
