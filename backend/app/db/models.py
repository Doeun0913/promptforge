"""SQLAlchemy models for persistent storage (feedback, presets, history)."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import Column, DateTime, Float, Integer, String, Text, JSON
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


class CompressionHistory(Base):
    __tablename__ = "compression_history"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String(64), index=True)
    original_prompt = Column(Text, nullable=False)
    compressed_prompt = Column(Text, nullable=False)
    domain = Column(String(32))
    original_tokens = Column(Integer)
    compressed_tokens = Column(Integer)
    savings_ratio = Column(Float)
    quality_score = Column(Float)
    filter_config = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)


class UserFeedback(Base):
    __tablename__ = "user_feedback"

    id = Column(Integer, primary_key=True, autoincrement=True)
    history_id = Column(Integer, index=True)
    rating = Column(Integer)  # 1-5
    comment = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)


class CustomPreset(Base):
    __tablename__ = "custom_presets"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(128), unique=True, nullable=False)
    config = Column(JSON, nullable=False)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
