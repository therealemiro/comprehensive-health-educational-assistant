"""
chats/routes.py

Complete CRUD operations for chats, the main messaging endpoint with reply support,
and the feedback endpoint for liking or disliking assistant responses.
"""

import time
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app import models, schemas
from app.auth.dependencies import get_current_user
from app.rag.hybrid_retriever import HybridRetriever
from app.rag.reranker import Reranker
from app.rag.llm_client import LLMClient
from app.rag.prompt_builder import PromptBuilder
from app.rag.logging_utils import log_production_interaction

router = APIRouter(prefix="/chats", tags=["Chats"])

llm_client = LLMClient()


def _get_owned_chat_or_404(
    chat_id: str,
    user: models.User,
    db: Session,
) -> models.Chat:
    chat = (
        db.query(models.Chat)
        .filter(
            models.Chat.id == chat_id,
            models.Chat.user_id == user.id,
        )
        .first()
    )

    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found.")

    return chat


def _get_message_in_chat_or_404(
    message_id: str,
    chat_id: str,
    db: Session,
) -> models.Message:
    message = (
        db.query(models.Message)
        .filter(
            models.Message.id == message_id,
            models.Message.chat_id == chat_id,
        )
        .first()
    )

    if not message:
        raise HTTPException(status_code=404, detail="Message not found.")

    return message


@router.post(
    "/",
    response_model=schemas.ChatOut,
    status_code=status.HTTP_201_CREATED,
)
def create_chat(
    chat_in: schemas.ChatCreate,
    user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    chat = models.Chat(user_id=user.id, title=chat_in.title)
    db.add(chat)
    db.commit()
    db.refresh(chat)

    return chat


@router.get("/", response_model=List[schemas.ChatOut])
def list_chats(
    user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return (
        db.query(models.Chat)
        .filter(models.Chat.user_id == user.id)
        .order_by(models.Chat.updated_at.desc())
        .all()
    )


@router.patch("/{chat_id}", response_model=schemas.ChatOut)
def rename_chat(
    chat_id: str,
    rename_in: schemas.ChatRename,
    user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    chat = _get_owned_chat_or_404(chat_id, user, db)
    chat.title = rename_in.title
    db.commit()
    db.refresh(chat)

    return chat


@router.delete("/{chat_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_chat(
    chat_id: str,
    user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    chat = _get_owned_chat_or_404(chat_id, user, db)
    db.delete(chat)
    db.commit()


@router.get("/{chat_id}/messages", response_model=List[schemas.MessageOut])
def list_messages(
    chat_id: str,
    user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    chat = _get_owned_chat_or_404(chat_id, user, db)

    return (
        db.query(models.Message)
        .filter(models.Message.chat_id == chat.id)
        .order_by(models.Message.created_at.asc())
        .all()
    )


@router.post(
    "/{chat_id}/messages",
    response_model=schemas.MessageOut,
    status_code=status.HTTP_201_CREATED,
)
def add_user_message(
    chat_id: str,
    message_in: schemas.MessageCreate,
    user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    chat = _get_owned_chat_or_404(chat_id, user, db)

    replied_message: Optional[models.Message] = None

    if message_in.reply_to_id:
        replied_message = _get_message_in_chat_or_404(
            message_in.reply_to_id,
            chat.id,
            db,
        )

    # 1. Save the user's message.
    user_message = models.Message(
        chat_id=chat.id,
        role="user",
        content=message_in.content,
        reply_to_id=message_in.reply_to_id,
    )

    db.add(user_message)
    db.commit()
    db.refresh(user_message)

    # If this is a reply, include the referenced message as additional context.
    effective_query = message_in.content

    if replied_message:
        effective_query = (
            f'(The user is replying to this previous message: '
            f'"{replied_message.content}")\n'
            f"New question: {message_in.content}"
        )

    # 2. Perform hybrid retrieval and reranking.
    t0 = time.time()

    hybrid_retriever = HybridRetriever.get_instance()
    candidate_chunks = hybrid_retriever.retrieve(
        effective_query,
        dense_k=15,
        sparse_k=15,
    )

    reranker = Reranker.get_instance()
    final_chunks = reranker.rerank(
        effective_query,
        candidate_chunks,
        top_k=5,
    )

    retrieval_latency = time.time() - t0

    # 3. Build the final prompt.
    final_prompt = PromptBuilder.build(
        effective_query,
        final_chunks,
    )

    # 4. Generate the response using Qwen.
    t1 = time.time()

    try:
        assistant_reply = llm_client.generate(final_prompt)
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))

    generation_latency = time.time() - t1

    if not assistant_reply:
        assistant_reply = (
            "Sorry, I was unable to generate an appropriate response at the moment. "
            "Please try again."
        )

    # 5. Save the assistant's response.
    assistant_message = models.Message(
        chat_id=chat.id,
        role="assistant",
        content=assistant_reply,
    )

    db.add(assistant_message)
    db.commit()
    db.refresh(assistant_message)

    # 6. Log the production interaction and performance metrics.
    log_production_interaction(
        user_email=user.email,
        chat_id=chat.id,
        query=message_in.content,
        answer=assistant_reply,
        retrieval_latency=retrieval_latency,
        generation_latency=generation_latency,
        final_chunks=final_chunks,
    )

    return assistant_message


@router.patch(
    "/{chat_id}/messages/{message_id}/feedback",
    response_model=schemas.MessageOut,
)
def set_message_feedback(
    chat_id: str,
    message_id: str,
    feedback_in: schemas.MessageFeedbackUpdate,
    user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Set or remove the user's like/dislike feedback on an assistant response."""
    _get_owned_chat_or_404(chat_id, user, db)
    message = _get_message_in_chat_or_404(message_id, chat_id, db)

    if message.role != "assistant":
        raise HTTPException(
            status_code=400,
            detail="Feedback can only be provided for assistant responses.",
        )

    message.feedback = feedback_in.feedback
    db.commit()
    db.refresh(message)

    return message