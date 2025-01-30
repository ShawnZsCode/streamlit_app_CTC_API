import os
import json

from core.tool_models import (
    ToolCall,
    ToolManager,
)
from ctc.api_sessions import (
    get_sessions,
    get_active_session,
    set_active_session,
)
from ctc.api_categories import (
    get_categories,
)
from ctc.api_elements import (
    get_elements,
    get_element_details,
)
from ctc.api_projects import (
    get_active_project,
)
from ctc.api_levels import (
    get_levels,
)
from ctc.api_views import (
    get_views,
    get_view_templates,
    create_floor_plan,
)
from core.openai_functions import (
    ChatMessage,
    ChatRole,
    ChatCompletion,
    OpenAIClient,
)


async def main(initialize_only=False):
    # Initialize tool manager
    tool_manager = ToolManager()

    # Define your tools configuration
    tools_config = [
        {
            "type": "function",
            "function": {
                "name": "get_sessions",
                "description": "Get all available Revit sessions",
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
                "name": "get_active_session",
                "description": "Gets current Revit session",
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
                "name": "set_active_session",
                "description": "set the port to target an available Revit session",
                "parameters": {
                    "type": "object",
                    "required": [],
                    "properties": {
                        "Port": {
                            "type": "integer",
                            "description": "The port number of the Revit session to connect to. If not specified, 0 will be used.",
                        },
                        "ActiveProject": {
                            "type": "string",
                            "description": "The name of the Revit project to connect to. If not specified, '' will be used.",
                        },
                    },
                    "additionalProperties": False,
                },
                "strict": True,
            },
        },
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
                "name": "get_views",
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
                "name": "get_categories",
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
                "name": "get_elements",
                "description": "Get the elements in the project",
                "parameters": {
                    "type": "object",
                    "required": ["CategoryId"],
                    "properties": {
                        "CategoryId": {
                            "type": "number",
                            "description": "The category ID is already stored in memory - use chat_memory.get_id_by_name('categories', category_name) to get it",
                        },
                        "IncludeParameters": {
                            "type": "boolean",
                            "description": "decide if all parameters and parameter values should be included in the response",
                        },
                    },
                    "additionalProperties": True,
                },
                "strict": True,
            },
        },
        {
            "type": "function",
            "function": {
                "name": "get_element_details",
                "description": "Get the details of a specific element in the project",
                "parameters": {
                    "type": "object",
                    "required": ["ElementId"],
                    "properties": {
                        "ElementId": {
                            "type": "number",
                            "description": "The element ID is already stored in memory - use chat_memory.get_id_by_name('elements', elementId) to get it",
                        }
                    },
                    "additionalProperties": True,
                },
                "strict": True,
            },
        },
        {
            "type": "function",
            "function": {
                "name": "get_levels",
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
        "get_sessions": get_sessions,
        "set_active_session": set_active_session,
        "get_active_session": get_active_session,
        "get_active_project": get_active_project,
        "get_views": get_views,
        "get_categories": get_categories,
        "get_levels": get_levels,
        "get_view_templates": get_view_templates,
        "create_floor_plan": create_floor_plan,
        "get_elements": get_elements,
        "get_element_details": get_element_details,
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
            while response.function_call:
                # Execute the tool
                print(f"Function call: {response.function_call.name}")
                tool_call = ToolCall(
                    name=response.function_call.name,
                    parameters=json.loads(response.function_call.arguments),
                )
                tool_response = await tool_manager.execute_tool(tool_call)
                print(f"Tool response: {tool_response.model_dump_json()}")

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
                            content=tool_response.model_dump_json(),
                        ),
                    ],
                    model=request.model,
                    temperature=request.temperature,
                )

                # Get LLM's interpretation of the tool response
                response = await client.create_chat_completion(follow_up_request)
                print("\nFollow-up Response:")
                print(f"\n{response.content}")
        else:
            print(f"Assistant response: {response.content}")


# if __name__ == "__main__":
#     import asyncio

#     asyncio.run(main())
