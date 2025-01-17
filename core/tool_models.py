"""Pydantic models for tool definitions and calls"""

from datetime import datetime
from typing import List, Dict, Any, Optional, Callable
from pydantic import BaseModel


# Pydantic Models for Tool Definitions
class ToolParameter(BaseModel):
    """Model for a tool parameter definition"""

    name: str
    description: str
    type: str
    required: bool = False


class Tool(BaseModel):
    """Model for a tool definition"""

    name: str
    description: str
    parameters: List[ToolParameter]


class ToolCall(BaseModel):
    """Model for the call of a tool"""

    name: str
    parameters: Dict[str, Any]


class ToolResponse(BaseModel):
    """Model for the response of a tool call"""

    success: bool
    result: Any
    error: Optional[str] = None


class FunctionCall(BaseModel):
    """Model for a function call"""

    name: str
    arguments: str


class ChatMemory:
    """In-memory storage for chat context data"""

    def __init__(self):
        self.conversations: Dict[str, List[Dict[str, Any]]] = {}
        self.context_data: Dict[str, Any] = {
            "name_to_id_mappings": {
                "sessions": {},  # session_name -> session_id
                "levels": {},  # level_name -> level_id
                "templates": {},  # template_name -> template_id
                "views": {},  # view_name -> view_id
                "categories": {},  # category_name -> category_id
                "elements": {},  # element_name -> element_id
            }
        }

    def store_sessions(self, sessions: List[Dict[str, Any]]):
        """Store only name to ID mappings for sessions"""
        # Store the full session data for reference
        self.context_data["sessions"] = sessions

        # Store the version to Port mappings
        self.context_data["name_to_id_mappings"]["sessions"] = {
            session["version"]: session["port"]
            for session in sessions
            if "name" in session and "port" in session
        }
        self.context_data["sessions_last_updated"] = datetime.now()

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

    def store_elements(self, elements: List[Dict[str, Any]]):
        """Store only name to ID mappings for revit elements"""
        # Store the full level data for reference
        self.context_data["elements"] = elements

        # Store the name to ID mappings
        self.context_data["name_to_id_mappings"]["elements"] = {
            element["name"]: element["id"]
            for element in elements
            if "name" in element and "id" in element
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

    def get_sessions(self) -> List[Dict[str, Any]]:
        """Get the stored active revit sessions"""
        return self.context_data.get("sessions", {})

    def get_active_project(self) -> Dict[str, Any]:
        """Get the stored active project data"""
        return self.context_data.get("active_project", {})

    def get_categories(self) -> List[Dict[str, Any]]:
        """Get the stored project categories"""
        return self.context_data.get("categories", [])

    def get_levels(self) -> List[Dict[str, Any]]:
        """Get the stored project levels"""
        return self.context_data.get("levels", [])

    def get_elements(self) -> List[Dict[str, Any]]:
        """Get the stored project elements"""
        return self.context_data.get("elements", [])

    def get_view_templates(self) -> List[Dict[str, Any]]:
        """Get the stored view templates"""
        return self.context_data.get("view_templates", [])

    def get_views(self) -> List[Dict[str, Any]]:
        """Get the stored views"""
        return self.context_data.get("views", [])


# Tool Manager with enhanced registration capabilities
class ToolManager:
    """Manager for tools and their implementations"""

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


# Example usage
chat_memory = ChatMemory()
