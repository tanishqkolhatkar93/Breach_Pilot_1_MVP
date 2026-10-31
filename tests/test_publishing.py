"""
Tests for Publishing Gatekeeper and State Machine Invariants
"""

import pytest
import uuid
from tools.memory import save_agent, get_agent, update_agent_status
from security.publishing_gate import publishing_gatekeeper

def test_blocked_agent_cannot_be_published():
    agent_id = save_agent({
        "id": f"test_blocked_{uuid.uuid4().hex[:6]}",
        "name": "Dangerous Agent",
        "target_type": "local_vulnerable",
        "status": "BLOCKED"
    })

    # Attempt to approve
    ok, msg, _ = publishing_gatekeeper.submit_human_approval(agent_id, "sess_1", "Security Officer", "Approved")
    assert ok is False
    assert "Cannot approve a BLOCKED agent" in msg

    # Attempt to publish directly
    ok, msg = publishing_gatekeeper.publish_to_marketplace(agent_id, "Admin")
    assert ok is False
    assert "SECURITY POLICY VIOLATION" in msg

def test_happy_path_publishing_workflow():
    agent_id = save_agent({
        "id": f"test_clean_{uuid.uuid4().hex[:6]}",
        "name": "Hardened Agent",
        "target_type": "local_secure",
        "status": "PENDING_HUMAN_APPROVAL"
    })

    # Step 1: Human Approval
    ok, msg, sig_data = publishing_gatekeeper.submit_human_approval(
        agent_id, "sess_clean", "Lead Judge", "Full security audit passed."
    )
    assert ok is True
    assert "signature" in sig_data

    # Verify status changed to APPROVED
    agent = get_agent(agent_id)
    assert agent["status"] == "APPROVED"

    # Step 2: Publish to Marketplace
    pub_ok, pub_msg = publishing_gatekeeper.publish_to_marketplace(agent_id, "Lead Judge")
    assert pub_ok is True
    assert "is now live on the Agent Marketplace" in pub_msg

    # Verify final status PUBLISHED
    agent = get_agent(agent_id)
    assert agent["status"] == "PUBLISHED"

