"""Multi-Turn Session Manager."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class TurnRecord:
    turn_index: int
    user_prompt: str
    compressed_prompt: str
    response: str
    embedding: list[float] = field(default_factory=list)


@dataclass
class Session:
    session_id: str
    turns: list[TurnRecord] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


class SessionManager:
    def __init__(self) -> None:
        self._sessions: dict[str, Session] = {}

    def get_or_create(self, session_id: str) -> Session:
        if session_id not in self._sessions:
            self._sessions[session_id] = Session(session_id=session_id)
        return self._sessions[session_id]

    def add_turn(self, session_id: str, turn: TurnRecord) -> None:
        session = self.get_or_create(session_id)
        session.turns.append(turn)

    def get_previous_turns(self, session_id: str) -> list[TurnRecord]:
        session = self._sessions.get(session_id)
        if session is None:
            return []
        return session.turns

    def clear_session(self, session_id: str) -> None:
        self._sessions.pop(session_id, None)
