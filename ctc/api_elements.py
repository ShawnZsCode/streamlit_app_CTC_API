"""Core functions for CTC Chatbot to get Elements from the Revit API"""

import os
from typing import Dict, Any
from dotenv import load_dotenv
import aiohttp

from core.tool_models import chat_memory
from ctc.data_models.sessions import RevitSession
from ctc.data_models.categories import RevitCategory
from ctc.data_models.elements import RevitElement
from ctc.data_models.families import RevitFamily
from ctc.data_models.family_types import RevitFamilyType


# Load environment variables from .env file in this directory


# Revit Tool Implementations
async def get_elements(
    *,
    session: RevitSession,
    category: RevitCategory,
    # IncludeParameters: str = "false",
) -> RevitCategory:
    """API call to get the elements in the project"""
    load_dotenv()
    revit_port = os.getenv("REVIT_PORT")
    api_key = os.getenv("CTC_API_KEY")
    if not api_key:
        raise ValueError("CTC_API_KEY not found in environment variables")

    async with aiohttp.ClientSession() as session:
        url = f"http://localhost:{revit_port}/api/v1/elements"
        params = {
            "apiKey": api_key,
            "categoryId": category.Id,
            # "includeParameters": IncludeParameters,
            # "includeFamily": "false",
            # "includeType": "false",
        }
        print(f"Getting Elements for Category: {category.Name}")

        try:
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    elements = await response.json()

                    for element in elements:
                        # Build the each element model part
                        try:
                            element_family_model = RevitFamily.model_validate(
                                element["type"]["family"]
                            )
                        except Exception:
                            default_family = {
                                "id": -1,
                                "name": category.Name,
                            }
                            element_family_model = RevitFamily.model_validate(
                                default_family
                            )
                        element_type_model = RevitFamilyType.model_validate(
                            element["type"]
                        )
                        element_model = RevitElement.model_validate(element)

                        # Validate the existence of each part in the category
                        # Add the family to the category
                        if not category.has_family(element_family_model):
                            category.Families.append(element_family_model)

                        # Get the index of the family in the category
                        fam_i = category.get_family_index(element_family_model)

                        if not (category.has_type(element_type_model)):
                            category.Families[fam_i].Types.append(element_type_model)

                        fam_i, type_i = category.get_fam_type_index(element_type_model)
                        if (
                            not category.Families[fam_i]
                            .Types[type_i]
                            .has_instance(element_model)
                        ):
                            category.Families[fam_i].Types[type_i].Instances.append(
                                element_model
                            )
                        elem_i = (
                            category.Families[fam_i]
                            .Types[type_i]
                            .get_instance_index(element_model)
                        )
                        # Update instance to match the latest data
                        category.Families[fam_i].Types[type_i].Instances[elem_i] = (
                            element_model
                        )

                    # Store name to ID mappings
                    # chat_memory.store_elements(elements)

                    return {"success": True, "result": category}
                else:
                    return {
                        "success": False,
                        "result": category,
                        "error": f"Failed to fetch elements. Status code: {response.status}",
                    }
        except Exception as e:
            return {
                "success": False,
                "result": category,
                "error": f"Error fetching elements: {str(e)}",
            }


async def get_element_details(ElementId: int) -> Dict[str, Any]:
    """API call to get the elements in the project"""
    load_dotenv()
    revit_port = os.getenv("REVIT_PORT")
    api_key = os.getenv("CTC_API_KEY")
    if not api_key:
        raise ValueError("CTC_API_KEY not found in environment variables")

    async with aiohttp.ClientSession() as session:
        url = f"http://localhost:{revit_port}/api/v1/elements/{ElementId}"
        params = {"apiKey": api_key}
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


async def update_element(
    element_id: int, parameter_id: int, value: Any
) -> Dict[str, Any]:
    """API call to update a new element in the project"""
    load_dotenv()
    revit_port = os.getenv("REVIT_PORT")
    api_key = os.getenv("CTC_API_KEY")
    if not api_key:
        raise ValueError("CTC_API_KEY not found in environment variables")

    async with aiohttp.ClientSession() as session:
        url = f"http://localhost:{revit_port}/api/v1/elements/{element_id}"
        params = {"apiKey": api_key}


# Prevent running from this file
if __name__ == "__main__":
    pass
