from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class ChatMessageIn(BaseModel):
    role: Literal["user", "assistant"]
    content: str = Field(min_length=1, max_length=8000)


class ChatRequest(BaseModel):
    session_id: str = Field(default="default", max_length=36)
    message: str = Field(min_length=1, max_length=8000)
    model: str | None = None
    history: list[ChatMessageIn] = Field(default_factory=list)


class ChatResponse(BaseModel):
    reply: str
    model: str


class SessionOut(BaseModel):
    id: str
    title: str
    created_at: datetime
    updated_at: datetime


class SessionListOut(BaseModel):
    sessions: list[SessionOut]


class SessionCreateOut(BaseModel):
    id: str
    title: str


class SessionGenerateTitleRequest(BaseModel):
    session_id: str = Field(max_length=36)
    message: str = Field(min_length=1, max_length=8000)
    reply: str = Field(min_length=1, max_length=8000)
