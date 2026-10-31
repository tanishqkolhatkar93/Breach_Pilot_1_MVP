"""
AgentShield AI - Multi-Step Autonomous Red-Team Orchestrator
Drives the end-to-end agentic loop:
PLAN -> ACT -> OBSERVE -> RE-PLAN -> ACT -> EVALUATE -> DECIDE
Visibly demonstrates true multi-step autonomy with persistent SQLite memory,
live tool execution, adaptive follow-ups, and gatekeeper integration.
"""

from typing import Dict, Any, List, Generator, Callable, Optional
import uuid
import datetime
from agent.planner import PlannerAgent
from agent.executor import ExecutorAgent
from agent.observer import ObserverAgent
from agent.replanner import ReplannerAgent
from agent.evaluator_agent import EvaluatorAgent
from security.publishing_gate import publishing_gatekeeper
from tools.memory import save_agent_session, update_agent_status, save_audit_event

class RedTeamOrchestrator:
    """Coordinates autonomous security audits through the multi-agent workflow."""

    def __init__(self):
        self.planner = PlannerAgent()
        self.executor = ExecutorAgent()
        self.observer = ObserverAgent()
        self.replanner = ReplannerAgent()
        self.evaluator = EvaluatorAgent()

    def run_audit(
        self,
        agent_config: Dict[str, Any],
        on_step_callback: Optional[Callable[[str, Dict[str, Any]], None]] = None,
        api_key: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Executes a complete autonomous red-team audit across all phases.
        Calls on_step_callback(phase, payload) to stream live events to UI.
        """
        if api_key is not None:
            self.planner = PlannerAgent(api_key=api_key)
            self.observer = ObserverAgent(api_key=api_key)
            self.replanner = ReplannerAgent(api_key=api_key)
        agent_id = agent_config.get("id", f"agent_{uuid.uuid4().hex[:8]}")
        session_id = f"sess_{uuid.uuid4().hex[:8]}"
        now = datetime.datetime.now(datetime.timezone.utc).isoformat()

        # Update agent status to TESTING
        update_agent_status(agent_id, "TESTING")
        save_audit_event("AUDIT_STARTED", "Orchestrator", f"Red-team session {session_id} initiated", agent_id, session_id)

        save_agent_session({
            "id": session_id,
            "agent_id": agent_id,
            "started_at": now,
            "status": "TESTING"
        })

        execution_history: List[Dict[str, Any]] = []

        # ==========================================
        # PHASE 1: PLAN
        # ==========================================
        if on_step_callback:
            on_step_callback("PLAN", {"status": "STARTING", "agent_name": agent_config.get("name")})
            
        plan_result = self.planner.plan_security_audit(agent_config)
        save_agent_session({
            "id": session_id,
            "agent_id": agent_id,
            "initial_plan_json": plan_result
        })

        if on_step_callback:
            on_step_callback("PLAN", {"status": "COMPLETED", "plan": plan_result})

        # ==========================================
        # PHASE 2: ACT & OBSERVE (Initial Planned Suite)
        # ==========================================
        for idx, test_case in enumerate(plan_result["test_cases"], 1):
            if on_step_callback:
                on_step_callback("ACT", {
                    "step": idx,
                    "total": len(plan_result["test_cases"]),
                    "test_case": test_case,
                    "phase_label": "Executing Test"
                })

            # Act
            exec_res = self.executor.execute_test(agent_config, session_id, test_case, phase="ACT_INITIAL")

            # Observe
            obs_res = self.observer.observe_and_assess(
                session_id=session_id,
                agent_id=agent_id,
                test_case=test_case,
                target_res=exec_res["target_response"]
            )

            record = {
                "test_case": test_case,
                "target_response": exec_res["target_response"],
                "eval_result": obs_res["eval_result"],
                "finding": obs_res["finding"],
                "is_adaptive": False
            }
            execution_history.append(record)

            if on_step_callback:
                on_step_callback("OBSERVE", {
                    "step": idx,
                    "test_id": test_case.get("test_id"),
                    "vulnerability_detected": obs_res["vulnerability_detected"],
                    "eval_result": obs_res["eval_result"],
                    "finding": obs_res["finding"]
                })

        # ==========================================
        # PHASE 3: RE-PLAN
        # ==========================================
        if on_step_callback:
            on_step_callback("RE-PLAN", {"status": "ANALYZING_FINDINGS"})

        replan_result = self.replanner.evaluate_and_replan(
            agent_id=agent_id,
            session_id=session_id,
            current_iteration=1
        )
        save_agent_session({
            "id": session_id,
            "agent_id": agent_id,
            "replan_decision_json": replan_result
        })

        if on_step_callback:
            on_step_callback("RE-PLAN", {"status": "COMPLETED", "decision": replan_result})

        # ==========================================
        # PHASE 4: ACT & OBSERVE (Adaptive Escalation)
        # ==========================================
        if replan_result.get("continue_testing") and replan_result.get("adaptive_tests"):
            for idx, adaptive_test in enumerate(replan_result["adaptive_tests"], 1):
                if on_step_callback:
                    on_step_callback("ACT", {
                        "test_case": adaptive_test,
                        "phase_label": "Executing Adaptive Test",
                        "is_adaptive": True
                    })

                exec_res = self.executor.execute_test(agent_config, session_id, adaptive_test, phase="ACT_ADAPTIVE")

                obs_res = self.observer.observe_and_assess(
                    session_id=session_id,
                    agent_id=agent_id,
                    test_case=adaptive_test,
                    target_res=exec_res["target_response"]
                )

                record = {
                    "test_case": adaptive_test,
                    "target_response": exec_res["target_response"],
                    "eval_result": obs_res["eval_result"],
                    "finding": obs_res["finding"],
                    "is_adaptive": True
                }
                execution_history.append(record)

                if on_step_callback:
                    on_step_callback("OBSERVE", {
                        "test_id": adaptive_test.get("test_id"),
                        "vulnerability_detected": obs_res["vulnerability_detected"],
                        "eval_result": obs_res["eval_result"],
                        "is_adaptive": True
                    })

        # ==========================================
        # PHASE 5: EVALUATE
        # ==========================================
        if on_step_callback:
            on_step_callback("EVALUATE", {"status": "COMPUTING_METRICS"})

        summary = self.evaluator.compile_session_evaluation(
            session_id=session_id,
            agent_id=agent_id,
            execution_records=execution_history
        )

        if on_step_callback:
            on_step_callback("EVALUATE", {"status": "COMPLETED", "summary": summary})

        # ==========================================
        # PHASE 6: DECIDE (Gatekeeper Policy Application)
        # ==========================================
        final_status = publishing_gatekeeper.apply_security_verdict(
            agent_id=agent_id,
            session_id=session_id,
            recommendation=summary["recommendation"],
            risk_score=summary["risk_score"]
        )

        if on_step_callback:
            on_step_callback("DECIDE", {
                "final_status": final_status,
                "recommendation": summary["recommendation"],
                "risk_score": summary["risk_score"],
                "reasons": summary["decision_rationale"]
            })

        save_audit_event(
            "AUDIT_COMPLETED",
            "Orchestrator",
            f"Session {session_id} finished. Score: {summary['risk_score']}, Verdict: {summary['recommendation']}, Status: {final_status}",
            agent_id,
            session_id
        )

        return {
            "session_id": session_id,
            "agent_id": agent_id,
            "plan": plan_result,
            "replan": replan_result,
            "execution_history": execution_history,
            "summary": summary,
            "final_status": final_status
        }

orchestrator = RedTeamOrchestrator()

