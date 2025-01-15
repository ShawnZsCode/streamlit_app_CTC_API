from typing import List, Dict, Any, Optional, Union, Callable
from pydantic import BaseModel, Field
import openai
from enum import Enum
import json
from dotenv import load_dotenv
import os
from datetime import datetime
import aiohttp

# Load environment variables from .env file in this directory
load_dotenv()
revit_port = os.getenv("REVIT_PORT")


# Pydantic Models for Tool Definitions
class ToolParameter(BaseModel):
    name: str
    description: str
    type: str
    required: bool = False


class Tool(BaseModel):
    name: str
    description: str
    parameters: List[ToolParameter]


class ToolCall(BaseModel):
    name: str
    parameters: Dict[str, Any]


class ToolResponse(BaseModel):
    success: bool
    result: Any
    error: Optional[str] = None


class FunctionCall(BaseModel):
    name: str
    arguments: str


class ChatRole(str, Enum):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    FUNCTION = "function"


class ChatMessage(BaseModel):
    role: ChatRole
    content: Optional[str] = None
    name: Optional[str] = None
    function_call: Optional[FunctionCall] = None


class ChatCompletion(BaseModel):
    messages: List[ChatMessage]
    functions: Optional[List[Dict[str, Any]]] = None
    function_call: Optional[str] = "auto"
    model: str = "gpt-4o-mini"
    temperature: float = 0.7
    max_tokens: Optional[int] = None


class ChatMemory:
    def __init__(self):
        self.conversations: Dict[str, List[Dict[str, Any]]] = {}
        self.context_data: Dict[str, Any] = {
            "name_to_id_mappings": {
                "levels": {},  # level_name -> level_id
                "templates": {},  # template_name -> template_id
                "views": {},  # view_name -> view_id
                "categories": {},  # category_name -> category_id
            }
        }

    def store_views(self, views: List[Dict[str, Any]]):
        """Store only name to ID mappings for views"""
        # Store the full view data for reference
        self.context_data["views"] = views

        # Store the name to ID mappings
        self.context_data["name_to_id_mappings"]["views"] = {
            view["name"]: view["id"]
            for view in views
            if "name" in view and "id" in view
        }
        self.context_data["views_last_updated"] = datetime.now()

    def store_categories(self, categories: List[Dict[str, Any]]):
        """Store only name to ID mappings for revit categories"""
        # Store the full level data for reference
        self.context_data["categories"] = categories

        # Store the name to ID mappings
        self.context_data["name_to_id_mappings"]["categories"] = {
            category["name"]: category["id"]
            for category in categories
            if "name" in category and "id" in category
        }

    def store_levels(self, levels: List[Dict[str, Any]]):
        """Store only name to ID mappings for levels"""
        # Store the full level data for reference
        self.context_data["levels"] = levels

        # Store the name to ID mappings
        self.context_data["name_to_id_mappings"]["levels"] = {
            level["name"]: level["id"]
            for level in levels
            if "name" in level and "id" in level
        }

    def store_templates(self, templates: List[Dict[str, Any]]):
        """Store only name to ID mappings for templates"""
        # Store the full template data for reference
        self.context_data["view_templates"] = templates

        # Store the name to ID mappings
        self.context_data["name_to_id_mappings"]["templates"] = {
            template["name"]: template["id"]
            for template in templates
            if "name" in template and "id" in template
        }

    def get_id_by_name(self, item_type: str, name: str) -> Optional[int]:
        """Get ID by name for any stored mapping type"""
        return self.context_data["name_to_id_mappings"].get(item_type, {}).get(name)

    def get_active_project(self) -> Dict[str, Any]:
        """Get the stored active project data"""
        return self.context_data.get("active_project", {})

    def get_categories(self) -> List[Dict[str, Any]]:
        """Get the stored project categories"""
        return self.context_data.get("categories", [])

    def get_levels(self) -> List[Dict[str, Any]]:
        """Get the stored project levels"""
        return self.context_data.get("levels", [])

    def get_view_templates(self) -> List[Dict[str, Any]]:
        """Get the stored view templates"""
        return self.context_data.get("view_templates", [])

    def get_views(self) -> List[Dict[str, Any]]:
        """Get the stored views"""
        return self.context_data.get("views", [])


# Tool Manager with enhanced registration capabilities
class ToolManager:
    def __init__(self):
        self.tools: Dict[str, Tool] = {}
        self.implementations: Dict[str, callable] = {}

    def register_tool(self, tool: Tool, implementation: callable):
        """Register a new tool with its implementation"""
        self.tools[tool.name] = tool
        self.implementations[tool.name] = implementation

    def get_tool_schemas(self) -> List[Dict[str, Any]]:
        """Get all tool schemas in OpenAI function format"""
        schemas = []
        for tool in self.tools.values():
            schema = {
                "name": tool.name,
                "description": tool.description,
                "parameters": {"type": "object", "properties": {}, "required": []},
            }
            for param in tool.parameters:
                schema["parameters"]["properties"][param.name] = {
                    "type": param.type,
                    "description": param.description,
                }
                if param.required:
                    schema["parameters"]["required"].append(param.name)
            schemas.append(schema)
        return schemas

    def register_from_openai_schema(
        self, schema: Dict[str, Any], implementation: callable
    ) -> None:
        """Register a tool from OpenAI function schema format"""
        function_def = schema.get(
            "function", schema
        )  # Handle both wrapped and unwrapped schemas

        # Extract parameters
        params = []
        properties = function_def.get("parameters", {}).get("properties", {})
        required = function_def.get("parameters", {}).get("required", [])

        for param_name, param_info in properties.items():
            params.append(
                ToolParameter(
                    name=param_name,
                    description=param_info.get("description", ""),
                    type=param_info.get("type", "string"),
                    required=param_name in required,
                )
            )

        # Create and register tool
        tool = Tool(
            name=function_def["name"],
            description=function_def.get("description", ""),
            parameters=params,
        )
        self.register_tool(tool, implementation)

    def register_tools_from_schemas(
        self, tools_config: List[Dict[str, Any]], implementations: Dict[str, Callable]
    ) -> None:
        """Register multiple tools from a list of OpenAI function schemas"""
        for tool_schema in tools_config:
            function_name = tool_schema.get("function", tool_schema).get("name")
            if function_name in implementations:
                self.register_from_openai_schema(
                    tool_schema, implementations[function_name]
                )
            else:
                print(f"Warning: No implementation found for tool {function_name}")

    async def execute_tool(self, tool_call: ToolCall) -> ToolResponse:
        """Execute a tool call and return the response"""
        if tool_call.name not in self.implementations:
            return ToolResponse(
                success=False, result=None, error=f"Tool {tool_call.name} not found"
            )

        try:
            result = await self.implementations[tool_call.name](**tool_call.parameters)
            return ToolResponse(success=True, result=result)
        except Exception as e:
            return ToolResponse(success=False, result=None, error=str(e))


# OpenAI Client Wrapper
class OpenAIClient:
    def __init__(self, api_key: str, tool_manager: ToolManager):
        self.client = openai.AsyncOpenAI(api_key=api_key)
        self.tool_manager = tool_manager

    async def create_chat_completion(self, request: ChatCompletion) -> ChatMessage:
        """Create a chat completion with function calling capability"""
        functions = self.tool_manager.get_tool_schemas()

        response = await self.client.chat.completions.create(
            model=request.model,
            messages=[msg.dict(exclude_none=True) for msg in request.messages],
            functions=functions,
            function_call=request.function_call,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
        )

        message = response.choices[0].message

        function_call = None
        if message.function_call:
            function_call = FunctionCall(
                name=message.function_call.name,
                arguments=message.function_call.arguments,
            )

        return ChatMessage(
            role=ChatRole.ASSISTANT,
            content=message.content,
            function_call=function_call,
        )


# Revit Tool Implementations
async def get_active_project() -> Dict[str, Any]:
    """Get active project open in Revit right now"""
    api_key = os.getenv("CTC_API_KEY")
    if not api_key:
        raise ValueError("CTC_API_KEY not found in environment variables")

    async with aiohttp.ClientSession() as session:
        url = f"http://localhost:{revit_port}/api/v1/projects/active"
        params = {"apiKey": api_key}

        try:
            async with session.get(url, params=params) as response:
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


async def get_categories() -> Dict[str, Any]:
    """Retrieves all the floor plans and 3D views in the project"""
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


async def get_views() -> Dict[str, Any]:
    """Retrieves all the floor plans and 3D views in the project"""
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


async def get_project_categories() -> Dict[str, Any]:
    """Get the categories in the project"""
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

                    # Store name to ID mappings
                    chat_memory.store_categories(categories)

                    return {"success": True, "result": categories}
                else:
                    return {
                        "success": False,
                        "error": f"Failed to fetch categories. Status code: {response.status}",
                    }
        except Exception as e:
            return {"success": False, "error": f"Error fetching categories: {str(e)}"}


async def get_project_levels() -> Dict[str, Any]:
    """Get the levels in the project"""
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


async def get_view_templates() -> List[Dict[str, Any]]:
    """Get the view templates in the project"""
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

                    # Store name to ID mappings
                    chat_memory.store_templates(templates)

                    return {"success": True, "result": templates}
                else:
                    return {
                        "success": False,
                        "error": f"Failed to fetch view templates. Status code: {response.status}",
                    }
        except Exception as e:
            return {
                "success": False,
                "error": f"Error fetching view templates: {str(e)}",
            }


async def create_floor_plan(
    Name: str, LevelId: int, ViewTemplateId: int, ScopeBoxId: int = 0
) -> Dict[str, Any]:
    """Create new floor plan in the project"""
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


# Example usage
chat_memory = ChatMemory()


async def main(initialize_only=False):
    # Initialize tool manager
    tool_manager = ToolManager()

    # Define your tools configuration
    tools_config = [
        {
            "type": "function",
            "function": {
                "name": "get_active_project",
                "description": "Get active project open in Revit right now",
                "parameters": {
                    "type": "object",
                    "required": [],
                    "properties": {},
                    "additionalProperties": False,
                },
                "strict": True,
            },
        },
        {
            "type": "function",
            "function": {
                "name": "getViews",
                "description": "Retrieves all the floor plans and 3D views in the project.",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "additionalProperties": False,
                    "required": [],
                },
                "strict": True,
            },
        },
        {
            "type": "function",
            "function": {
                "name": "get_project_categories",
                "description": "Get the categories in the project",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "additionalProperties": False,
                    "required": [],
                },
                "strict": True,
            },
        },
        {
            "type": "function",
            "function": {
                "name": "get_project_levels",
                "description": "Get the levels in the project",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "additionalProperties": False,
                    "required": [],
                },
                "strict": True,
            },
        },
        {
            "type": "function",
            "function": {
                "name": "get_view_templates",
                "description": "Get the view templates in the project",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "additionalProperties": False,
                    "required": [],
                },
                "strict": True,
            },
        },
        {
            "type": "function",
            "function": {
                "name": "create_floor_plan",
                "description": "Creates a new floor plan view in Revit. Use this function IMMEDIATELY when a user asks to create a floor plan - do not check other data first. All required IDs are already stored in memory.",
                "parameters": {
                    "type": "object",
                    "required": ["Name", "LevelId", "ViewTemplateId", "ScopeBoxId"],
                    "properties": {
                        "Name": {
                            "type": "string",
                            "description": "The name for the new floor plan view (use exactly as provided by user)",
                        },
                        "LevelId": {
                            "type": "number",
                            "description": "The level ID is already stored in memory - use chat_memory.get_id_by_name('levels', level_name) to get it",
                        },
                        "ViewTemplateId": {
                            "type": "number",
                            "description": "The template ID is already stored in memory - use chat_memory.get_id_by_name('templates', template_name) to get it",
                        },
                        "ScopeBoxId": {
                            "type": "number",
                            "description": "Use 0 when no scope box is specified",
                        },
                    },
                    "additionalProperties": False,
                },
                "strict": True,
            },
        },
    ]

    # Create implementations mapping
    implementations = {
        "get_active_project": get_active_project,
        "getViews": get_views,
        "get_project_categories": get_project_categories,
        "get_project_levels": get_project_levels,
        "get_view_templates": get_view_templates,
        "create_floor_plan": create_floor_plan,
    }

    # Register all tools at once
    tool_manager.register_tools_from_schemas(tools_config, implementations)

    # Initialize OpenAI client
    client = OpenAIClient(
        api_key=os.getenv("OPENAI_API_KEY"), tool_manager=tool_manager
    )

    if initialize_only:
        return {"tool_manager": tool_manager, "openai_client": client}

    if not initialize_only:
        # Example chat completion request
        request = ChatCompletion(
            messages=[
                ChatMessage(
                    role=ChatRole.USER,
                    # content="What is the active project in Revit?"
                    # content="What are all the views in the project?"
                    # content="Can you count and summarize the views in my project, and also list them by title one by one?"
                    # content="Can you get the Levels in the project?"
                    # content="Can you get the View Templates in the project?"
                    # content="Can you count and summarize the View Templates in my project, and also list them by Name one by one and categorize them by Discipline?"
                    # content="Using Level ID 30, and View Template 161376, a null Scope Box, can you create a View named KP_SAMPLE_LLM_01"
                )
            ]
        )

        # Get completion
        response = await client.create_chat_completion(request)
        print(f"Initial Response: {response}")
        print()

        # Handle function calls if present
        if response.function_call:
            # Execute the tool
            tool_call = ToolCall(
                name=response.function_call.name,
                parameters=json.loads(response.function_call.arguments),
            )
            tool_response = await tool_manager.execute_tool(tool_call)
            print(f"Tool response: {tool_response.json()}")

            # Add tool response to messages and get LLM interpretation
            follow_up_request = ChatCompletion(
                messages=[
                    *request.messages,  # Include original messages
                    ChatMessage(
                        role=ChatRole.ASSISTANT,
                        content=None,
                        function_call=response.function_call,
                    ),
                    ChatMessage(
                        role=ChatRole.FUNCTION,
                        name=tool_call.name,
                        content=tool_response.json(),
                    ),
                ],
                model=request.model,
                temperature=request.temperature,
            )

            # Get LLM's interpretation of the tool response
            final_response = await client.create_chat_completion(follow_up_request)
            print(f"\nFinal Response:")
            print(f"\n{final_response.content}")
        else:
            print(f"Assistant response: {response.content}")


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
