# streamlit_app.py
import streamlit as st
from typing import List, Dict, Any
import asyncio
import os
import logging
from dotenv import load_dotenv
import json
from ctc_chat_functions import (
    ChatMemory, 
    ChatMessage, 
    ChatRole, 
    ChatCompletion,
    ToolCall,
    chat_memory,
    main  # Import the main function that initializes everything
)

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
        st.session_state.suggested_actions = [{
            "name": "Create New Views",
            "type": "form",
            "fields": [
                {
                    "name": "level",
                    "type": "select",
                    "options": [level["Name"] for level in chat_memory.get_levels() if "Name" in level]
                },
                {
                    "name": "template",
                    "type": "select",
                    "options": [template["Name"] for template in chat_memory.get_view_templates() if "Name" in template]
                },
                {
                    "name": "name",
                    "type": "text",
                    "description": "View name"
                }
            ]
        }]
    else:
        logging.info("No view-related content found, clearing suggested actions")
        st.session_state.suggested_actions = []

# Configure Streamlit page
st.set_page_config(
    page_title="Revit Project Assistant",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded"
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
    logging.info(f"Initiate Backend...")
    backend = asyncio.run(main(initialize_only=True))
    st.session_state.openai_client = backend['openai_client']
    st.session_state.tool_manager = backend['tool_manager']

# Sidebar with project context
with st.sidebar:
    st.header("Project Context")
    
    # Project Summary
    if project := chat_memory.get_active_project():
        st.subheader("Active Project")
        if "Title" in project:
            st.write(f"📋 **Name:** {project['Title']}")
        if "Number" in project:
            st.write(f"🔢 **Number:** {project['Number']}")
    
    # Views organized by type
    if views := chat_memory.get_views():
        with st.expander("📐 Views"):
            # Separate views by type
            view_types = {}
            for view in views:
                view_type = view.get('ViewType', 'Other')
                if view_type not in view_types:
                    view_types[view_type] = []
                view_types[view_type].append({
                    'Name': view.get('Name', 'Unnamed'),
                    'Id': view.get('Id', None)
                })
            
            # Display views grouped by type
            for view_type, type_views in view_types.items():
                st.write(f"**{view_type}**")
                for view in type_views:
                    st.write(f"- {view['Name']}")
    
    # Levels - simplified display
    if levels := chat_memory.get_levels():
        with st.expander("📊 Levels"):
            for level in levels:
                if 'Name' in level and 'Id' in level:
                    st.write(f"- {level['Name']}")
    
    # View Templates - simplified display
    if templates := chat_memory.get_view_templates():
        with st.expander("🎨 View Templates"):
            for template in templates:
                if 'Name' in template:
                    st.write(f"- {template['Name']}")
    
    # Hidden technical info container
    if st.session_state.get('show_technical_info', False):
        with st.expander("🔧 Technical Information", expanded=False):
            st.write("View Creation Requirements:")
            st.json({
                "Name": "string",
                "LevelId": "integer_elementId",
                "ViewTemplateId": "integer_elementId",
                "ScopeBoxId": "null (not implemented)"
            })

# Main chat interface
st.title("BIM Automation Assistant")

# Display chat messages first
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input and processing
if prompt := st.chat_input("How can I help you with your Revit project?", disabled=st.session_state.processing):
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
                        ChatMessage(
                            role=ChatRole.SYSTEM,
                            content=system_message
                        ),
                        ChatMessage(role=ChatRole.USER, content=last_message)
                    ]
                )
                
                # Get initial response
                logging.info("Sending request to OpenAI")
                initial_response = asyncio.run(st.session_state.openai_client.create_chat_completion(request))
                logging.info(f"Received initial response: {initial_response}")
                
                if initial_response.function_call:
                    logging.info(f"Function call detected: {initial_response.function_call.name}")
                    # Execute the tool
                    tool_call = ToolCall(
                        name=initial_response.function_call.name,
                        parameters=json.loads(initial_response.function_call.arguments)
                    )
                    logging.info(f"Executing tool: {tool_call.name} with parameters: {tool_call.parameters}")
                    tool_response = asyncio.run(st.session_state.tool_manager.execute_tool(tool_call))
                    logging.info(f"Tool response: {tool_response}")
                    
                    # Add tool response to messages and get LLM interpretation
                    follow_up_request = ChatCompletion(
                        messages=[
                            *request.messages,
                            ChatMessage(
                                role=ChatRole.ASSISTANT,
                                content=None,
                                function_call=initial_response.function_call
                            ),
                            ChatMessage(
                                role=ChatRole.FUNCTION,
                                name=tool_call.name,
                                content=tool_response.json()
                            )
                        ],
                        model=request.model,
                        temperature=request.temperature
                    )
                    
                    # Get LLM's interpretation of the tool response
                    logging.info("Getting final response from OpenAI")
                    final_response = asyncio.run(st.session_state.openai_client.create_chat_completion(follow_up_request))
                    logging.info(f"Final response: {final_response}")
                    
                    # Add final response to chat
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": final_response.content
                    })
                    
                    # Update suggested actions based on context
                    update_suggested_actions(final_response)
                    
                else:
                    logging.info("No function call needed, using initial response")
                    # If no function call, just add the initial response to chat
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": initial_response.content
                    })
                    
                    # Update suggested actions based on context
                    update_suggested_actions(initial_response)
                
            except Exception as e:
                logging.error(f"Error processing request: {str(e)}", exc_info=True)
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": f"An error occurred while processing your request: {str(e)}"
                })
            
            finally:
                logging.info("Processing complete, resetting processing state")
                st.session_state.processing = False
                st.rerun()

# Display suggested actions
if st.session_state.suggested_actions:
    st.divider()
    st.subheader("Suggested Actions")
    
    for action in st.session_state.suggested_actions:
        if action["type"] == "form":
            with st.expander(action["name"]):
                with st.form(f"form_{action['name']}"):
                    values = {}
                    for field in action["fields"]:
                        if field["type"] == "select":
                            values[field["name"]] = st.selectbox(
                                field["name"].title(),
                                options=field["options"]
                            )
                        elif field["type"] == "text":
                            values[field["name"]] = st.text_input(
                                field["name"].title(),
                                help=field.get("description", "")
                            )
                        elif field["type"] == "number":
                            values[field["name"]] = st.number_input(
                                field["name"].title(),
                                min_value=field.get("min", 0)
                            )
                    
                    if st.form_submit_button("Execute"):
                        with st.spinner("Executing action..."):
                            # Get the level and template IDs based on their names
                            level_id = next((level["Id"] for level in chat_memory.get_levels() 
                                           if level["Name"] == values["level"]), None)
                            template_id = next((template["Id"] for template in chat_memory.get_view_templates() 
                                              if template["Name"] == values["template"]), None)
                            
                            if level_id and template_id:
                                # Create the floor plan
                                result = asyncio.run(st.session_state.tool_manager.execute_tool(
                                    ToolCall(
                                        name="create_floor_plan",
                                        parameters={
                                            "Name": values["name"],
                                            "LevelId": level_id,
                                            "ViewTemplateId": template_id,
                                            "ScopeBoxId": 0
                                        }
                                    )
                                ))
                                
                                if result.success:
                                    st.success(f"Successfully created view: {values['name']}")
                                    # Force refresh of views in sidebar
                                    asyncio.run(st.session_state.tool_manager.execute_tool(
                                        ToolCall(name="getViews", parameters={})
                                    ))
                                    st.rerun()
                                else:
                                    st.error(f"Failed to create view: {result.error}")
                            else:
                                st.error("Could not find level or template IDs")