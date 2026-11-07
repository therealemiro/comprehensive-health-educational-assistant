"""
models.py

Database ORM models: User, Chat, Message, and RevokedToken.
"""

import uuid
import datetime

from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship

from app.database import Base


def generate_uuid():
    return str(uuid.uuid4())


class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    chats = relationship(
        "Chat",
        back_populates="owner",
        cascade="all, delete-orphan",
    )


class Chat(Base):
    __tablename__ = "chats"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    title = Column(String(255), default="New Chat")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(
        DateTime,
        default=datetime.datetime.utcnow,
        onupdate=datetime.datetime.utcnow,
    )

    owner = relationship("User", back_populates="chats")
    messages = relationship(
        "Message",
        back_populates="chat",
        cascade="all, delete-orphan",
    )


class Message(Base):
    __tablename__ = "messages"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    chat_id = Column(String(36), ForeignKey("chats.id"), nullable=False, index=True)
    role = Column(
        Enum("user", "assistant", name="message_role"),
        nullable=False,
    )
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # User feedback on the assistant's response (only populated for role="assistant").
    feedback = Column(
        Enum("like", "dislike", name="message_feedback"),
        nullable=True,
    )

    # If this message was sent as a reply to another message.
    reply_to_id = Column(
        String(36),
        ForeignKey("messages.id"),
        nullable=True,
    )

    chat = relationship("Chat", back_populates="messages")
    reply_to = relationship("Message", remote_side=[id])


class RevokedToken(Base):
    """
    Stores the JTI (unique identifier) of tokens revoked by the user after logout.
    """

    __tablename__ = "revoked_tokens"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    jti = Column(String(36), unique=True, index=True, nullable=False)
    revoked_at = Column(DateTime, default=datetime.datetime.utcnow)