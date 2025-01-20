"""OpenAI Chat Engine Functions"""

import os
import logging
from enum import Enum
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
import openai

from core.tool_models import (
    ToolManager,
    FunctionCall,
)

# Classes for Open AI chat engine


class ChatRole(str, Enum):
    """Chat role enum"""

    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    FUNCTION = "function"


class ChatMessage(BaseModel):
    """Chat message model"""

    role: ChatRole
    content: Optional[str] = None
    name: Optional[str] = None
    function_call: Optional[FunctionCall] = None


class ChatCompletion(BaseModel):
    """Chat completion model"""

    messages: List[ChatMessage]
    functions: Optional[List[Dict[str, Any]]] = None
    function_call: Optional[str] = "auto"
    model: str = "gpt-4o-mini"
    temperature: float = 0.7
    max_tokens: Optional[int] = None


# OpenAI Client Wrapper
class OpenAIClient:
    """OpenAI client wrapper"""

    def __init__(self, api_key: str, tool_manager: ToolManager):
        self.client = openai.AsyncOpenAI(api_key=api_key)
        self.tool_manager = tool_manager

    async def create_chat_completion(self, request: ChatCompletion) -> ChatMessage:
        """Create a chat completion with function calling capability"""
        functions = self.tool_manager.get_tool_schemas()

        response = await self.client.chat.completions.create(
            model=request.model,
            messages=[msg.model_dump(exclude_none=True) for msg in request.messages],
            functions=functions,
            function_call=request.function_call,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
        )

        message = response.choices[0].message

        logging.info(f"Revit Port: {os.environ.get('REVIT_PORT')}")
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
