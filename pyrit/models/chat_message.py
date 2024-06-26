# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.

from typing import Literal, Optional
from pydantic import BaseModel, ConfigDict


ChatMessageRole = Literal["system", "user", "assistant"]


class ToolCall(BaseModel):
    model_config = ConfigDict(extra="forbid")
    id: str
    type: str
    function: str


class ChatMessage(BaseModel):
    model_config = ConfigDict(extra="forbid")
    role: ChatMessageRole
    content: str
    name: Optional[str] = None
    tool_calls: Optional[list[ToolCall]] = None
    tool_call_id: Optional[str] = None


class ChatMessageListContent(BaseModel):
    model_config = ConfigDict(extra="forbid")
    role: ChatMessageRole
    content: list[dict[str, str]]
    name: Optional[str] = None
    tool_calls: Optional[list[ToolCall]] = None
    tool_call_id: Optional[str] = None
