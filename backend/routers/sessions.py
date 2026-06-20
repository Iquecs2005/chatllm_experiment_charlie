from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models import ChatMessage, Session
from backend.schemas.chat import (
    SessionCreateOut,
    SessionGenerateTitleRequest,
    SessionListOut,
    SessionOut,
)

router = APIRouter(prefix="/api/sessions", tags=["sessions"])


def _generate_title_from_context(message: str, reply: str) -> str:
    """Generate a short title from the first user message and assistant reply."""
    # Take first ~50 chars of the user message, or first line
    title = (message or "").strip().split("\n")[0][:50]
    if title:
        return title
    # Fallback: use first ~50 chars of reply
    title = (reply or "").strip().split("\n")[0][:50]
    return title if title else "Novo Chat"


@router.get("", response_model=SessionListOut)
def list_sessions(db: Session = Depends(get_db)):
    """List all sessions ordered by most recently updated."""
    sessions = (
        db.query(Session)
        .order_by(Session.updated_at.desc())
        .all()
    )
    return SessionListOut(
        sessions=[
            SessionOut(
                id=s.id,
                title=s.title,
                created_at=s.created_at,
                updated_at=s.updated_at,
            )
            for s in sessions
        ]
    )


@router.post("", response_model=SessionCreateOut, status_code=201)
def create_session(db: Session = Depends(get_db)):
    """Create a new empty session."""
    session_id = str(uuid.uuid4())
    session = Session(id=session_id, title="Novo Chat")
    db.add(session)
    db.commit()
    db.refresh(session)
    return SessionCreateOut(id=session.id, title=session.title)


@router.delete("/{session_id}", status_code=204)
def delete_session(session_id: str, db: Session = Depends(get_db)):
    """Delete a session and all its messages."""
    session = db.query(Session).filter(Session.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    # Delete all messages belonging to this session
    db.query(ChatMessage).filter(ChatMessage.session_key == session_id).delete()
    db.delete(session)
    db.commit()


@router.get("/{session_id}/messages")
def get_session_messages(session_id: str, db: Session = Depends(get_db)):
    """Get all messages for a given session."""
    session = db.query(Session).filter(Session.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    messages = (
        db.query(ChatMessage)
        .filter(ChatMessage.session_key == session_id)
        .order_by(ChatMessage.created_at.asc())
        .all()
    )
    return [
        {
            "id": msg.id,
            "role": msg.role,
            "content": msg.content,
            "model": msg.model,
            "created_at": msg.created_at.isoformat(),
        }
        for msg in messages
    ]


@router.post("/generate-title")
def generate_title(payload: SessionGenerateTitleRequest, db: Session = Depends(get_db)):
    """Generate and update the title for a session based on first message context.
    
    Only sets the title if the session still has the default title ('Novo Chat').
    Once a custom title is generated, subsequent calls are ignored.
    """
    session = db.query(Session).filter(Session.id == payload.session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    if session.title != "Novo Chat":
        # Title already customized — return current title unchanged
        return {"id": session.id, "title": session.title}

    new_title = _generate_title_from_context(payload.message, payload.reply)
    session.title = new_title
    db.commit()
    return {"id": session.id, "title": session.title}