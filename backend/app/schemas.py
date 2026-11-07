"""
schemas.py

Pydantic models for validating API input and output.
"""

import datetime
from typing import Optional, Literal

from pydantic import BaseModel, EmailStr, Field


# ---------- User / Auth ----------

class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    id: str
    email: EmailStr
    created_at: datetime.datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


# ---------- Chat ----------

class ChatCreate(BaseModel):
    title: str = "New Chat"


class ChatRename(BaseModel):
    title: str = Field(min_length=1, max_length=255)


class ChatOut(BaseModel):
    id: str
    title: str
    created_at: datetime.datetime
    updated_at: datetime.datetime

    class Config:
        from_attributes = True


# ---------- Message ----------

class MessageCreate(BaseModel):
    content: str = Field(min_length=1)
    reply_to_id: Optional[str] = None  # If the user is replying to a previous message.


class MessageOut(BaseModel):
    id: str
    role: str
    content: str
    created_at: datetime.datetime
    feedback: Optional[str] = None
    reply_to_id: Optional[str] = None

    class Config:
        from_attributes = True


class MessageFeedbackUpdate(BaseModel):
    feedback: Optional[Literal["like", "dislike"]] = None  # None removes the previous feedback.