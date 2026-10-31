"""
Tests for Autonomous Red-Team Agentic Loop
"""

import pytest
import uuid
from agent.orchestrator import orchestrator
from tools.memory import save_agent, get_agent, get_previous_findings, get_evaluations

def test_full_audit_vulnerable_agent():
    agent_id = f"test_vuln_{uuid.uuid4().hex[:6]}"
    save_agent({
        "id": agent_id,
        "name": "ShopBot-Vulnerable",
        "description": "Unprotected retail customer bot",
        "target_type": "local_vulnerable",
        "status": "SUBMITTED"
    })

    events = []
    def callback(phase, payload):
        events.append((phase, payload))

    agent_config = get_agent(agent_id)
    result = orchestrator.run_audit(agent_config, on_step_callback=callback)

    assert result["summary"]["recommendation"] == "BLOCK"
    assert result["final_status"] == "BLOCKED"
    assert result["summary"]["risk_score"] < 60 or result["summary"]["findings_by_severity"]["CRITICAL"] > 0
    assert len(result["execution_history"]) >= 12

    # Check that events from all phases occurred
    phases_observed = set(e[0] for e in events)
    assert "PLAN" in phases_observed
    assert "ACT" in phases_observed
    assert "OBSERVE" in phases_observed
    assert "RE-PLAN" in phases_observed
    assert "EVALUATE" in phases_observed
    assert "DECIDE" in phases_observed

    # Verify persistent memory
    findings = get_previous_findings(agent_id, session_id=result["session_id"])
    assert len(findings) > 0
    evals = get_evaluations(result["session_id"])
    assert len(evals) >= 12

def test_full_audit_secure_agent():
    agent_id = f"test_sec_{uuid.uuid4().hex[:6]}"
    save_agent({
        "id": agent_id,
        "name": "ShopShield-Secure",
        "description": "Hardened enterprise retail bot",
        "target_type": "local_secure",
        "status": "SUBMITTED"
    })

    agent_config = get_agent(agent_id)
    result = orchestrator.run_audit(agent_config)

    assert result["summary"]["recommendation"] == "APPROVE"
    assert result["final_status"] == "PENDING_HUMAN_APPROVAL"
    assert result["summary"]["risk_score"] >= 80.0
    assert result["summary"]["findings_by_severity"]["CRITICAL"] == 0
    assert result["summary"]["findings_by_severity"]["HIGH"] == 0

