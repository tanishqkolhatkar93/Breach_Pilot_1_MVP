"""
AgentShield AI - Evaluation Agent (Module E)
Evaluates complete test case executions, computes metrics (ASR, Refusal Rate, Pass Rate),
calculates the final risk score, and determines publishing gatekeeper recommendations.
"""

from typing import Dict, Any, List
from tools.memory import save_evaluation, get_previous_findings, save_agent_session
from tools.evaluation import calculate_metrics, calculate_risk_score, generate_evaluation_summary

class EvaluatorAgent:
    """Computes final audit metrics, scores, and publishing recommendations."""

    def compile_session_evaluation(
        self,
        session_id: str,
        agent_id: str,
        execution_records: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Processes all executed test cases, persists evaluation rows,
        and computes global session statistics and recommendations.
        """
        stored_evaluations: List[Dict[str, Any]] = []

        for item in execution_records:
            test_case = item["test_case"]
            target_res = item["target_response"]
            eval_result = item["eval_result"]

            eval_row = {
                "session_id": session_id,
                "agent_id": agent_id,
                "test_id": test_case.get("test_id"),
                "category": test_case.get("category"),
                "prompt": test_case.get("prompt"),
                "expected_safe_behavior": test_case.get("expected_safe_behavior"),
                "target_response": target_res.get("response", ""),
                "actual_result": eval_result.get("actual_result", ""),
                "passed": eval_result.get("passed", False),
                "is_safe_refusal": eval_result.get("is_safe_refusal", False),
                "is_legitimate_pass": eval_result.get("is_legitimate_pass", False),
                "severity": eval_result.get("severity", "MEDIUM"),
                "evidence": eval_result.get("evidence", "")
            }
            save_evaluation(eval_row)
            stored_evaluations.append(eval_row)

        findings = get_previous_findings(agent_id, session_id=session_id)
        summary = generate_evaluation_summary(session_id, agent_id, stored_evaluations, findings)

        # Update session with completed score and recommendation
        save_agent_session({
            "id": session_id,
            "agent_id": agent_id,
            "status": "COMPLETED",
            "risk_score": summary["risk_score"],
            "recommendation": summary["recommendation"]
        })

        return summary

