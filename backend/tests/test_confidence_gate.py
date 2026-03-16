"""Tests for the Confidence Gate module."""

import pytest

from app.pipeline.confidence_gate import (
    ConfidenceGate,
    GateDecision,
    GateMode,
)


def test_auto_mode_accept():
    gate = ConfidenceGate(mode=GateMode.AUTO, auto_threshold=0.95)
    verdict = gate.evaluate(0.97, "s3_rewriter", "원본", "변환")
    assert verdict.decision == GateDecision.ACCEPT


def test_auto_mode_reject():
    gate = ConfidenceGate(mode=GateMode.AUTO, auto_threshold=0.95)
    verdict = gate.evaluate(0.80, "s3_rewriter", "원본", "변환")
    assert verdict.decision == GateDecision.REJECT


def test_semi_mode_accept():
    gate = ConfidenceGate(mode=GateMode.SEMI, semi_lower=0.70, semi_upper=0.95)
    verdict = gate.evaluate(0.97, "s3_rewriter", "원본", "변환")
    assert verdict.decision == GateDecision.ACCEPT


def test_semi_mode_ask_user():
    gate = ConfidenceGate(mode=GateMode.SEMI, semi_lower=0.70, semi_upper=0.95)
    verdict = gate.evaluate(0.85, "s3_rewriter", "원본", "변환")
    assert verdict.decision == GateDecision.ASK_USER
    assert len(gate.pending_verdicts) == 1


def test_semi_mode_reject():
    gate = ConfidenceGate(mode=GateMode.SEMI, semi_lower=0.70, semi_upper=0.95)
    verdict = gate.evaluate(0.50, "s3_rewriter", "원본", "변환")
    assert verdict.decision == GateDecision.REJECT


def test_manual_mode_always_asks():
    gate = ConfidenceGate(mode=GateMode.MANUAL)
    verdict = gate.evaluate(0.99, "s3_rewriter", "원본", "변환")
    assert verdict.decision == GateDecision.ASK_USER
