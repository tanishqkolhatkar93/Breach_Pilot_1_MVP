"""
AgentShield AI - Executor Agent (Module B)
Executes scheduled attack prompts against the target agent using the Target Client.
Captures target responses, latency, tool calls, and logs real-time attack events.
"""

from typing import Dict, Any, List
import datetime
from tools.target_client import call_target_agent
from tools.memory import save_attack_event

class ExecutorAgent:
    """Dispatches attack payloads and monitors execution telemetry."""

    def execute_test(
        self,
        agent_config: Dict[str, Any],
        session_id: str,
        test_case: Dict[str, Any],
        phase: str = "EXECUTE"
    ) -> Dict[str, Any]:
        """
        Executes a single test case against the target agent and records audit telemetry.
        """
        test_id = test_case.get("test_id", "UNK")
        prompt = test_case.get("prompt", "")
        agent_id = agent_config.get("id", "")

        # Log initiation event
        save_attack_event({
            "session_id": session_id,
            "agent_id": agent_id,
            "phase": phase,
            "test_id": test_id,
            "action": f"DISPATCH_ATTACK: {test_case.get('name', test_id)}",
            "details": {"category": test_case.get("category"), "prompt_preview": prompt[:80]},
            "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat()
        })

        # Send test prompt to target agent
        target_res = call_target_agent(agent_config, prompt)

        # Log completion event
        save_attack_event({
            "session_id": session_id,
            "agent_id": agent_id,
            "phase": phase,
            "test_id": test_id,
            "action": f"RESPONSE_RECEIVED: Status {target_res.get('status_code')} in {target_res.get('latency_ms')}ms",
            "details": {
                "response_preview": target_res.get("response", "")[:100],
                "tool_calls_count": len(target_res.get("tool_calls", []))
            },
            "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat()
        })

        return {
            "test_case": test_case,
            "target_response": target_res
        }

