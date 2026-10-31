"""
AgentShield AI - HTTP Target Agent Client (TOOL 1)
Dispatches authorized security test prompts to target AI agents.
Supports both local simulated agents (Vulnerable / Secure) and external HTTP/REST endpoints.
Enforces timeouts, error handling, and latency instrumentation.
"""

from typing import Dict, Any, Optional
import time
import requests
from config.settings import TARGET_REQUEST_TIMEOUT
from targets.vulnerable_agent import VulnerableAgent
from targets.secure_agent import SecureAgent
from targets.imported_agent import ImportedSandboxAgent

# Singleton instances for local targets
_vulnerable_target = VulnerableAgent()
_secure_target = SecureAgent()
_imported_sandbox = ImportedSandboxAgent()

def call_target_agent(
    agent_config: Dict[str, Any],
    prompt: str,
    headers: Optional[Dict[str, str]] = None,
    timeout: float = TARGET_REQUEST_TIMEOUT
) -> Dict[str, Any]:
    """
    Executes a test prompt against the designated target agent.
    Returns:
        Dict containing response text, latency_ms, status_code, tool_calls, and error (if any).
    """
    target_type = agent_config.get("target_type", "local_vulnerable")
    endpoint_url = agent_config.get("endpoint_url", "")
    start_time = time.time()

    # Route 1: Local Vulnerable Agent Simulation
    if target_type == "local_vulnerable":
        try:
            res = _vulnerable_target.handle_request(prompt, headers=headers)
            return res
        except Exception as e:
            return {
                "status_code": 500,
                "response": f"Internal execution error: {str(e)}",
                "tool_calls": [],
                "latency_ms": round((time.time() - start_time) * 1000, 2),
                "error": str(e)
            }

    # Route 2: Local Secure Agent Simulation
    elif target_type == "local_secure":
        try:
            res = _secure_target.handle_request(prompt, headers=headers)
            return res
        except Exception as e:
            return {
                "status_code": 500,
                "response": f"Internal execution error: {str(e)}",
                "tool_calls": [],
                "latency_ms": round((time.time() - start_time) * 1000, 2),
                "error": str(e)
            }

    # Route 2b: Local Imported / n8n / LangGraph Sandbox Simulation
    elif target_type in ["local_n8n_sandbox", "local_imported", "local_langgraph_sandbox", "local_langchain_sandbox"] or "imported_sandbox" in endpoint_url or "langgraph_sandbox" in endpoint_url:
        try:
            res = _imported_sandbox.handle_request(prompt, agent_config=agent_config, headers=headers)
            return res
        except Exception as e:
            return {
                "status_code": 500,
                "response": f"Internal execution error: {str(e)}",
                "tool_calls": [],
                "latency_ms": round((time.time() - start_time) * 1000, 2),
                "error": str(e)
            }

    # Route 3: Remote HTTP REST Agent Endpoint (FastAPI, LangServe, Express, Custom)
    elif target_type in ["remote_http", "custom", "langchain_http", "langgraph_http"]:
        if not endpoint_url:
            return {
                "status_code": 400,
                "response": "Error: Missing target endpoint URL for remote agent.",
                "tool_calls": [],
                "latency_ms": 0.0,
                "error": "MissingEndpointURL"
            }
        try:
            req_headers = {"Content-Type": "application/json"}
            if headers:
                req_headers.update(headers)
            
            # Universal payload compatible with LangServe (/invoke), FastAPI, and custom chat webhooks
            payload = {
                "prompt": prompt,
                "input": prompt,
                "message": prompt,
                "messages": [{"role": "user", "content": prompt}],
                "agent_id": agent_config.get("id", "")
            }
            response = requests.post(endpoint_url, json=payload, headers=req_headers, timeout=timeout)
            latency_ms = round((time.time() - start_time) * 1000, 2)
            
            try:
                res_json = response.json()
                if isinstance(res_json, dict):
                    out_val = res_json.get("output") or res_json.get("response") or res_json.get("text")
                    if isinstance(out_val, dict):
                        resp_text = out_val.get("content") or out_val.get("response") or str(out_val)
                    elif isinstance(out_val, str):
                        resp_text = out_val
                    else:
                        resp_text = str(res_json)
                    
                    tool_calls = res_json.get("tool_calls", [])
                    if not tool_calls and "intermediate_steps" in res_json:
                        for step in res_json.get("intermediate_steps", []):
                            if isinstance(step, (list, tuple)) and len(step) > 0:
                                t_action = step[0]
                                tool_name = getattr(t_action, "tool", None) or (t_action.get("tool") if isinstance(t_action, dict) else str(t_action))
                                tool_calls.append({"tool": str(tool_name)})
                else:
                    resp_text = str(res_json)
                    tool_calls = []
            except Exception:
                resp_text = response.text
                tool_calls = []

            return {
                "status_code": response.status_code,
                "response": resp_text,
                "tool_calls": tool_calls,
                "latency_ms": latency_ms,
                "agent_name": agent_config.get("name", "Remote Agent")
            }
        except requests.Timeout:
            latency_ms = round((time.time() - start_time) * 1000, 2)
            return {
                "status_code": 408,
                "response": "RequestTimeout: Target agent failed to respond within time threshold.",
                "tool_calls": [],
                "latency_ms": latency_ms,
                "error": "Timeout"
            }
        except Exception as e:
            latency_ms = round((time.time() - start_time) * 1000, 2)
            return {
                "status_code": 502,
                "response": f"BadGateway: Failed connecting to target endpoint: {str(e)}",
                "tool_calls": [],
                "latency_ms": latency_ms,
                "error": str(e)
            }

    else:
        return {
            "status_code": 400,
            "response": f"Unknown target_type: {target_type}",
            "tool_calls": [],
            "latency_ms": 0.0,
            "error": "InvalidTargetType"
        }

