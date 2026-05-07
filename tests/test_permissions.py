from __future__ import annotations

from pigenus.core.permissions import PermissionEngine


def test_permission_engine_allows_memory_write_in_developer_default_context():
    engine = PermissionEngine()

    decision = engine.check(context="developer/default", action="memory_write")

    assert decision.allowed is True
    assert decision.reason == "default_context_allow"


def test_permission_engine_blocks_unknown_critical_actions():
    engine = PermissionEngine()

    decision = engine.check(context="developer/default", action="unknown_critical_action")

    assert decision.allowed is False
    assert decision.reason == "action_not_allowed"
