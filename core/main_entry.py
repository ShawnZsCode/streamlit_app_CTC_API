import os
import json

from utils.file_utils import read_file_json

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
    tools_config = read_file_json("core\\function_tools.json")

    # Create implementations mapping
    implementations = {
        "get_sessions": get_sessions,
        "get_active_session": get_active_session,
        "set_active_session": set_active_session,
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


# Prevent running from this file
if __name__ == "__main__":
    pass
