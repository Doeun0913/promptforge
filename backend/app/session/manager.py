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
    emotion_snapshot: dict[str, Any] = field(default_factory=dict)
    """해당 턴의 감정 상태 직렬화 dict.
    session 모듈이 pipeline 모듈에 의존하지 않도록 EmotionSnapshot을 직접 임포트하지 않고
    dict로 저장한다.

    저장 키 (Phase 2에서 stage1이 채움):
        turn_index       : int
        sentiment        : str  ("positive" | "negative" | "neutral")
        sentiment_score  : float
        emotions         : list[str]
        frustration_streak : int
    """


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
