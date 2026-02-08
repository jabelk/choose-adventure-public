import uuid
from typing import Optional

from app.models import StorySession

# In-memory session store: session_id -> StorySession
_sessions: dict[str, StorySession] = {}


def create_session(story_session: StorySession) -> str:
    """Create a new session and return the session ID."""
    session_id = str(uuid.uuid4())
    _sessions[session_id] = story_session
    return session_id


def get_session(session_id: str) -> Optional[StorySession]:
    """Retrieve a session by ID, or None if not found."""
    return _sessions.get(session_id)


def update_session(session_id: str, story_session: StorySession) -> None:
    """Update an existing session."""
    _sessions[session_id] = story_session


def delete_session(session_id: str) -> None:
    """Delete a session."""
    _sessions.pop(session_id, None)
