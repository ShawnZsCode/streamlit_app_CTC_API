"""Streamlit app for the Revit Project Assistant."""

import asyncio
import logging
import json
import streamlit as st

# from typing import List, Dict, Any
from dotenv import load_dotenv

from core.tool_models import (
    ToolCall,
    chat_memory,
)
from core.openai_functions import (
    ChatMessage,
    ChatRole,
    ChatCompletion,
)
from core.main_entry import main


# Set up logging
logging.basicConfig(level=logging.INFO)

# Load environment variables
load_dotenv()


def update_suggested_actions(response: ChatMessage):
    """
    Update suggested actions based on chat context.
    For example, if the user asked about views, we suggest creating views.
    """
    logging.info(f"Updating suggested actions based on response: {response.content}")
    # For demonstration: If the response mentions "view", we show the "Create New Views" form.
    if response.content and "view" in response.content.lower():
        logging.info("View mentioned in response, adding view creation form")
        st.session_state.suggested_actions = [
            {
                "name": "Create New Views",
                "type": "form",
                "fields": [
                    {
                        "name": "level",
                        "type": "select",
                        "options": [
                            level["name"]
                            for level in chat_memory.get_levels()
                            if "name" in level
                        ],
                    },
                    {
                        "name": "template",
                        "type": "select",
                        "options": [
                            template["name"]
                            for template in chat_memory.get_view_templates()
                            if "name" in template
                        ],
                    },
                    {"name": "name", "type": "text", "description": "View name"},
                ],
            }
        ]
    elif response.content and "session" in response.content.lower():
        logging.info("Session mentioned in response, setting active session form")
        st.session_state.suggested_actions = [
            {
                "name": "Set Current Session",
                "type": "form",
                "fields": [
                    {
                        "name": "port",
                        "type": "select",
                        "options": [
                            session["port"]
                            for session in chat_memory.get_sessions()
                            if "Port" in session
                        ],
                    },
                    {
                        "name": "revit project",
                        "type": "select",
                        "options": [
                            session["ActiveProject"]
                            for session in chat_memory.get_sessions()
                            if "ActiveProject" in session
                        ],
                    },
                ],
            }
        ]
    else:
        logging.info("No suggested actions found, clearing suggested actions")
        st.session_state.suggested_actions = []


# Configure Streamlit page
st.set_page_config(
    page_title="Revit Project Assistant",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Initialize UI state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "suggested_actions" not in st.session_state:
    st.session_state.suggested_actions = []
if "processing" not in st.session_state:
    st.session_state.processing = False

# Initialize backend components
if "openai_client" not in st.session_state or "tool_manager" not in st.session_state:
    logging.info("Initiate Backend...")
    backend = asyncio.run(main(initialize_only=True))
    st.session_state.openai_client = backend["openai_client"]
    st.session_state.tool_manager = backend["tool_manager"]

# Sidebar with project context
with st.sidebar:
    st.header("Project Context")
    # Active Sessions
    if session := chat_memory.get_active_session():
        st.subheader("Active Session")
        with st.expander("Session", expanded=True):
            st.write(f"**Version:** {session['RevitVersion']}")
            st.write(f"**Port:** {session['Port']}")
            st.write(f"**Active Model:** {session['ActiveProject']}")

    # Session Summary
    if sessions := chat_memory.get_sessions():
        st.subheader("Active Revit Sessions")
        with st.expander("Sessions", expanded=True):
            # Separate sessions by Revit version
            versions = {}
            for session in sessions:
                revit_version = session.get("RevitVersion", "Unknown Version")
                if revit_version not in versions.keys():
                    versions[revit_version] = []
                versions[revit_version].append(
                    {
                        "port": session.get("Port", "Unnamed"),
                        "model": session.get("ActiveProject", None),
                    }
                )
                logging.info(f"Versions: {versions}")

            # Display sessions grouped by version
            for version, version_sessions in versions.items():
                st.write(f"**{version}**")
                for session in version_sessions:
                    st.write(f"- Port: {session['port']}, Model: {session['model']}")

    # Project Summary
    if project := chat_memory.get_active_project():
        st.subheader("Active Project")
        if "title" in project:
            st.write(f"📋 **Name:** {project['title']}")
        if "Number" in project:
            st.write(f"🔢 **Number:** {project['Number']}")

    # Views organized by type
    if views := chat_memory.get_views():
        with st.expander("📐 Views"):
            # Separate views by type
            view_types = {}
            for view in views:
                view_type = view.get("viewTypeName", "Other")
                if view_type not in view_types:
                    view_types[view_type] = []
                view_types[view_type].append(
                    {"name": view.get("name", "Unnamed"), "id": view.get("id", None)}
                )

            # Display views grouped by type
            for view_type, type_views in view_types.items():
                st.write(f"**{view_type}**")
                for view in type_views:
                    st.write(f"- {view['name']}")

    # Categories - simplified display
    if categories := chat_memory.get_categories():
        with st.expander("📊 Categories"):
            for category in categories:
                if "name" in category and "id" in category:
                    st.write(f"- {category['name']}")

    # Elements - simplified display
    if elements := chat_memory.get_elements():
        with st.expander("🧱 Elements"):
            for element in elements:
                if "name" in element and "id" in element:
                    st.write(f"- {element['name']}")

    # Levels - simplified display
    if levels := chat_memory.get_levels():
        with st.expander("📊 Levels"):
            for level in levels:
                if "name" in level and "id" in level:
                    st.write(f"- {level['name']}")

    # View Templates - simplified display
    if templates := chat_memory.get_view_templates():
        with st.expander("🎨 View Templates"):
            for template in templates:
                if "name" in template:
                    st.write(f"- {template['name']}")

    # Hidden technical info container
    if st.session_state.get("show_technical_info", False):
        with st.expander("🔧 Technical Information", expanded=False):
            st.write("View Creation Requirements:")
            st.json(
                {
                    "name": "string",
                    "levelId": "integer_elementId",
                    "viewTemplateId": "integer_elementId",
                    "scopeBoxId": "null (not implemented)",
                }
            )

# Main chat interface
st.title("BIM Automation Assistant")

# Display chat messages first
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input and processing
if prompt := st.chat_input(
    "How can I help you with your Revit project?", disabled=st.session_state.processing
):
    logging.info(f"Received new prompt: {prompt}")
    # Add user message immediately
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.session_state.processing = True
    logging.info("Set processing state to True")
    st.rerun()

# Process the last message if we're in processing state
if st.session_state.processing and st.session_state.messages:
    logging.info("Processing last message")
    with st.chat_message("assistant"):
        with st.spinner("Processing your request..."):
            try:
                # Get the last user message
                last_message = st.session_state.messages[-1]["content"]
                logging.info(f"Processing user message: {last_message}")

                system_message = """You are a BIM Automation Assistant that helps users with Revit tasks.
You can understand natural language requests and convert them into appropriate actions.
When users mention names of levels, templates, or views, you can look up their IDs automatically.

When asked to create a floor plan:
1. Use the create_floor_plan function directly
2. Convert names to IDs using the stored mappings
3. Do not check prerequisites - assume they are met
4. For no scope box, use ScopeBoxId = 0

Focus on understanding user intent and executing requested actions efficiently."""
                logging.info(f"System message: {system_message}")

                # Create initial chat completion request
                request = ChatCompletion(
                    messages=[
                        ChatMessage(role=ChatRole.SYSTEM, content=system_message),
                        ChatMessage(role=ChatRole.USER, content=last_message),
                    ]
                )

                # Get initial response
                logging.info("Sending request to OpenAI")
                initial_response = asyncio.run(
                    st.session_state.openai_client.create_chat_completion(request)
                )
                logging.info(f"Received initial response: {initial_response}")
                response = initial_response

                if response.function_call:
                    while response.function_call:
                        logging.info(
                            f"Function call detected: {response.function_call.name}"
                        )
                        # Execute the tool
                        tool_call = ToolCall(
                            name=response.function_call.name,
                            parameters=json.loads(response.function_call.arguments),
                        )
                        logging.info(
                            f"Executing tool: {tool_call.name} with parameters: {tool_call.parameters}"
                        )
                        tool_response = asyncio.run(
                            st.session_state.tool_manager.execute_tool(tool_call)
                        )
                        logging.info(f"Tool response: {tool_response}")

                        # Add tool response to messages and get LLM interpretation
                        follow_up_request = ChatCompletion(
                            messages=[
                                *request.messages,
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
                        logging.info("Getting final response from OpenAI")
                        last_response = asyncio.run(
                            st.session_state.openai_client.create_chat_completion(
                                follow_up_request
                            )
                        )
                        logging.info(f"Final response: {last_response}")

                        # Update suggested actions based on context
                        update_suggested_actions(last_response)
                        response = last_response

                    # Add final response to chat
                    st.session_state.messages.append(
                        {"role": "assistant", "content": last_response.content}
                    )

                else:
                    logging.info("No function call needed, using initial response")
                    # If no function call, just add the initial response to chat
                    st.session_state.messages.append(
                        {"role": "assistant", "content": response.content}
                    )

                    # Update suggested actions based on context
                    update_suggested_actions(initial_response)

            except Exception as e:
                logging.error(f"Error processing request: {str(e)}", exc_info=True)
                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": f"An error occurred while processing your request: {str(e)}",
                    }
                )

            finally:
                logging.info("Processing complete, resetting processing state")
                st.session_state.processing = False
                st.rerun()

# Display suggested actions
if st.session_state.suggested_actions:
    st.divider()
    st.subheader("Suggested Actions")

    for action in st.session_state.suggested_actions:
        if action["name"] == "Create New Views":
            with st.expander(action["name"]):
                with st.form(f"form_{action['name']}"):
                    values = {}
                    for field in action["fields"]:
                        if field["type"] == "select":
                            values[field["name"]] = st.selectbox(
                                field["name"].title(), options=field["options"]
                            )
                        elif field["type"] == "text":
                            values[field["name"]] = st.text_input(
                                field["name"].title(), help=field.get("description", "")
                            )
                        elif field["type"] == "number":
                            values[field["name"]] = st.number_input(
                                field["name"].title(), min_value=field.get("min", 0)
                            )

                    if st.form_submit_button("Execute"):
                        with st.spinner("Executing action..."):
                            # Get the level and template IDs based on their names
                            level_id = next(
                                (
                                    level["id"]
                                    for level in chat_memory.get_levels()
                                    if level["name"] == values["level"]
                                ),
                                None,
                            )
                            template_id = next(
                                (
                                    template["id"]
                                    for template in chat_memory.get_view_templates()
                                    if template["name"] == values["template"]
                                ),
                                None,
                            )

                            if level_id and template_id:
                                # Create the floor plan
                                result = asyncio.run(
                                    st.session_state.tool_manager.execute_tool(
                                        ToolCall(
                                            name="create_floor_plan",
                                            parameters={
                                                "Name": values["name"],
                                                "LevelId": level_id,
                                                "ViewTemplateId": template_id,
                                                "ScopeBoxId": 0,
                                            },
                                        )
                                    )
                                )

                                if result.success:
                                    st.success(
                                        f"Successfully created view: {values['name']}"
                                    )
                                    # Force refresh of views in sidebar
                                    asyncio.run(
                                        st.session_state.tool_manager.execute_tool(
                                            ToolCall(name="getViews", parameters={})
                                        )
                                    )
                                    st.rerun()
                                else:
                                    st.error(f"Failed to create view: {result.error}")
                            else:
                                st.error("Could not find level or template IDs")
        elif action["name"] == "Set Current Session":
            with st.expander(action["name"]):
                with st.form(f"form_{action['name']}"):
                    values = {}
                    for field in action["fields"]:
                        if field["type"] == "select":
                            values[field["name"]] = st.selectbox(
                                field["name"].title(), options=field["options"]
                            )

                    if st.form_submit_button("Execute"):
                        with st.spinner("Setting active session..."):
                            # Set the active session in the .env file
                            result = asyncio.run(
                                st.session_state.set_active_session(
                                    Port=values["port"],
                                    ActiveProject=values["revit project"],
                                )
                            )

                            if result:
                                st.success(
                                    f"Successfully set active session to port: {values['port']}"
                                )
                                # Force refresh of sessions in sidebar
                                asyncio.run(
                                    st.session_state.tool_manager.execute_tool(
                                        ToolCall(
                                            name="get_active_session", parameters={}
                                        )
                                    )
                                )
                                st.rerun()
                            else:
                                st.error("Failed to set active session")


# Prevent running from this file
if __name__ == "__main__":
    pass
