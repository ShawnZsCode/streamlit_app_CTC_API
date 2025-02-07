"""Core functions for CTC Chatbot to get Cateogies from a constants list"""

import os
from datetime import datetime
from typing import List, Dict, Any
from dotenv import load_dotenv
import aiohttp

from core.tool_models import chat_memory
from ctc.data_models.categories import RevitCategories, RevitCategory


# Revit Tool Implementations
async def get_categories() -> RevitCategories:
    """Retrieves all Revit Categories from a constants list"""
    import csv

    file_path = "ctc/constants/Category_2025.csv"
    with open(file_path, "r") as open_file:
        open_file = csv.DictReader(open_file)
        categories: RevitCategories = RevitCategories()
        for row in open_file:
            if row["IsObsolete"] == "FALSE" and row["ForLLM"] == "TRUE":
                category = RevitCategory.model_validate(row)
                categories.Categories.append(category)
    return categories


async def get_categories_depricated() -> Dict[str, Any]:
    """Retrieves all the floor plans and 3D views in the project"""
    load_dotenv()
    revit_port = os.getenv("REVIT_PORT")
    api_key = os.getenv("CTC_API_KEY")
    if not api_key:
        raise ValueError("CTC_API_KEY not found in environment variables")

    async with aiohttp.ClientSession() as session:
        url = f"http://localhost:{revit_port}/api/v1/revit-categories"
        params = {"apiKey": api_key}

        try:
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    categories = await response.json()

                    # Store raw data in memory
                    chat_memory.store_categories(categories)

                    return {"success": True, "result": categories}
                else:
                    return {
                        "success": False,
                        "error": f"Failed to fetch categories. Status code: {response.status}",
                    }
        except Exception as e:
            return {"success": False, "error": f"Error fetching categories: {str(e)}"}


# Prevent running from this file
if __name__ == "__main__":
    pass
