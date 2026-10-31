"""
AgentShield AI - Publishing Gatekeeper (Section 9)
Enforces strict gatekeeping policies before an agent can be published to a public marketplace.
Maintains state machine:
  SUBMITTED -> TESTING -> (BLOCKED | PENDING_HUMAN_APPROVAL) -> APPROVED -> PUBLISHED
Guarantees:
  - Blocked agents can never be published.
  - Review-state agents require manual override.
  - Approved agents require explicit human sign-off with audit signature.
"""

from typing import Dict, Any, Tuple, Optional
import datetime
import uuid
from tools.memory import (
    get_agent, update_agent_status, save_publishing_decision,
    save_audit_event, get_previous_findings
)
from tools.evaluation import calculate_risk_score

VALID_STATES = [
    "SUBMITTED",
    "TESTING",
    "BLOCKED",
    "PENDING_HUMAN_APPROVAL",
    "APPROVED",
    "PUBLISHED"
]

class PublishingGatekeeper:
    """Gatekeeper engine enforcing marketplace publishing security invariants."""

    @staticmethod
    def evaluate_publishing_eligibility(agent_id: str, session_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Assesses if an agent is eligible to enter the human approval queue or be published.
        Returns detailed eligibility status, score, decision, and reasons.
        """
        agent = get_agent(agent_id)
        if not agent:
            return {"allowed": False, "reason": f"Agent {agent_id} not found."}

        findings = get_previous_findings(agent_id, session_id=session_id)
        score, reasons, recommendation = calculate_risk_score(findings)

        can_enter_approval = (recommendation == "APPROVE")
        is_blocked = (recommendation == "BLOCK")
        needs_review = (recommendation == "REVIEW")

        return {
            "agent_id": agent_id,
            "current_status": agent.get("status", "SUBMITTED"),
            "risk_score": score,
            "recommendation": recommendation,
            "is_blocked": is_blocked,
            "needs_review": needs_review,
            "can_enter_approval": can_enter_approval,
            "reasons": reasons,
            "findings_count": len(findings)
        }

    @staticmethod
    def apply_security_verdict(agent_id: str, session_id: str, recommendation: str, risk_score: float) -> str:
        """
        Updates agent state based on autonomous red-team evaluation verdict.
        """
        if recommendation == "BLOCK":
            new_status = "BLOCKED"
        elif recommendation == "APPROVE":
            new_status = "PENDING_HUMAN_APPROVAL"
        else: # REVIEW
            new_status = "BLOCKED" # Fails safe until human review
            
        update_agent_status(agent_id, new_status)
        save_audit_event(
            event_type="GATEKEEPER_VERDICT",
            actor="AgentShield_Gatekeeper",
            details=f"Status set to {new_status}. Recommendation: {recommendation}, Score: {risk_score}",
            agent_id=agent_id,
            session_id=session_id
        )
        return new_status

    @staticmethod
    def submit_human_approval(
        agent_id: str,
        session_id: str,
        reviewer_name: str,
        rationale: str
    ) -> Tuple[bool, str, Dict[str, Any]]:
        """
        Performs explicit human sign-off on an eligible agent.
        Only agents in PENDING_HUMAN_APPROVAL can be approved.
        """
        agent = get_agent(agent_id)
        if not agent:
            return False, f"Agent '{agent_id}' does not exist.", {}

        curr_status = agent.get("status")
        if curr_status == "BLOCKED":
            save_audit_event(
                "UNAUTHORIZED_PUBLISH_ATTEMPT",
                reviewer_name,
                "Attempted to approve a BLOCKED agent. Action rejected.",
                agent_id=agent_id,
                session_id=session_id
            )
            return False, "GATEKEEPER REJECTION: Cannot approve a BLOCKED agent with unresolved critical vulnerabilities.", {}

        if curr_status != "PENDING_HUMAN_APPROVAL":
            return False, f"Invalid state transition: Agent is in '{curr_status}', must be 'PENDING_HUMAN_APPROVAL'.", {}

        signature = f"AUTH-SEC-{uuid.uuid4().hex[:8].upper()}"
        save_publishing_decision({
            "agent_id": agent_id,
            "session_id": session_id,
            "decision": "APPROVED",
            "risk_score": 100.0,
            "reviewer_name": reviewer_name,
            "rationale": rationale,
            "signature": signature
        })

        update_agent_status(agent_id, "APPROVED")
        save_audit_event(
            "HUMAN_APPROVAL_GRANTED",
            reviewer_name,
            f"Human approval granted. Signature: {signature}. Rationale: {rationale}",
            agent_id=agent_id,
            session_id=session_id
        )
        return True, "Agent successfully approved for marketplace publication.", {"signature": signature}

    @staticmethod
    def publish_to_marketplace(
        agent_id: str,
        publisher_name: str
    ) -> Tuple[bool, str]:
        """
        Final publishing step. Requires status == 'APPROVED'.
        """
        agent = get_agent(agent_id)
        if not agent:
            return False, f"Agent '{agent_id}' not found."

        curr_status = agent.get("status")
        if curr_status != "APPROVED":
            save_audit_event(
                "UNAUTHORIZED_PUBLISH_ATTEMPT",
                publisher_name,
                f"Attempted to publish agent in '{curr_status}' state. Rejected.",
                agent_id=agent_id
            )
            return False, f"SECURITY POLICY VIOLATION: Cannot publish agent in '{curr_status}' status. Requires prior human security approval."

        update_agent_status(agent_id, "PUBLISHED")
        save_audit_event(
            "AGENT_PUBLISHED",
            publisher_name,
            f"Agent successfully deployed and published to Marketplace.",
            agent_id=agent_id
        )
        return True, f"Success: Agent '{agent.get('name')}' is now live on the Agent Marketplace!"

publishing_gatekeeper = PublishingGatekeeper()

