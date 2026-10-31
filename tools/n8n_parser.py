"""
AgentShield AI - n8n Workflow Security Analyzer
Parses uploaded n8n workflow JSON files, extracts node topology and AI agent components,
performs static security risk analysis (credential exposure, excessive tool agency,
unauthenticated triggers), and configures the workflow for dynamic red-team evaluation.
"""

from typing import Dict, Any, List
import json
import re

def parse_n8n_workflow(workflow_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Parses and audits an n8n workflow JSON object.
    Returns structured topology and static security assessment findings.
    """
    if not isinstance(workflow_data, dict):
        return {
            "valid": False,
            "error": "Invalid format: Workflow JSON root must be an object."
        }

    nodes = workflow_data.get("nodes", [])
    if not isinstance(nodes, list) or len(nodes) == 0:
        return {
            "valid": False,
            "error": "Invalid n8n schema: 'nodes' array is missing or empty."
        }

    workflow_name = workflow_data.get("name", "Untitled n8n Workflow")
    connections = workflow_data.get("connections", {})

    agent_nodes = []
    trigger_nodes = []
    tool_nodes = []
    other_nodes = []

    # Static Risk Audit Findings
    static_risks: List[Dict[str, Any]] = []

    for node in nodes:
        node_name = node.get("name", "Unnamed Node")
        node_type = (node.get("type") or "").lower()
        parameters = node.get("parameters", {})
        param_str = json.dumps(parameters).lower()

        # Categorize node
        if any(marker in node_type for marker in ["agent", "langchain", "openai", "anthropic", "llm"]):
            agent_nodes.append({
                "name": node_name,
                "type": node.get("type"),
                "model": parameters.get("model") or parameters.get("modelName") or "Custom LLM",
                "system_message": parameters.get("options", {}).get("systemMessage") or parameters.get("systemMessage", "")
            })
        elif any(marker in node_type for marker in ["webhook", "trigger", "cron", "poll", "chattrigger"]):
            trigger_nodes.append({
                "name": node_name,
                "type": node.get("type"),
                "http_method": parameters.get("httpMethod", "POST"),
                "path": parameters.get("path", "")
            })
        elif any(marker in node_type for marker in ["tool", "http", "postgres", "sql", "gmail", "slack", "code", "database"]):
            tool_nodes.append({
                "name": node_name,
                "type": node.get("type")
            })
        else:
            other_nodes.append({
                "name": node_name,
                "type": node.get("type")
            })

        # Static Security Check 1: Embedded Hardcoded Secrets / Credentials
        secret_patterns = [r"api[_-]?key", r"secret", r"password", r"bearer\s+[a-z0-9_\-\.]+", r"token", r"canary"]
        for pattern in secret_patterns:
            matches = re.findall(pattern, param_str)
            if matches and any(sensitive in param_str for sensitive in ["sk-", "ghp_", "bearer", "password=", "secret_"]):
                static_risks.append({
                    "severity": "HIGH",
                    "title": f"Hardcoded Credential in Node '{node_name}'",
                    "category": "Credential Exposure",
                    "description": f"Node parameters appear to contain hardcoded authentication tokens or keys matching '{pattern}'.",
                    "remediation": "Move secrets to n8n Environment Variables or Credential Store ($env.SECRET_NAME)."
                })
                break

        # Static Security Check 2: Excessive Database / Financial Agency
        if any(t in node_type for t in ["postgres", "mysql", "sql"]):
            query = (parameters.get("query") or parameters.get("sql") or "").upper()
            if any(kw in query for kw in ["DROP", "DELETE", "TRUNCATE", "UPDATE"]):
                static_risks.append({
                    "severity": "CRITICAL",
                    "title": f"Destructive Database Agency in Node '{node_name}'",
                    "category": "Excessive Agency",
                    "description": f"Database node contains destructive SQL capabilities ({query[:40]}...). An AI agent with access could trigger irreversible data loss.",
                    "remediation": "Restrict database role permissions to Read-Only (SELECT) for agent tool calls."
                })

        # Static Security Check 3: Unauthenticated Webhook Triggers
        if "webhook" in node_type:
            auth_type = parameters.get("authentication", "none")
            if auth_type == "none":
                static_risks.append({
                    "severity": "MEDIUM",
                    "title": f"Unauthenticated Webhook Trigger '{node_name}'",
                    "category": "Access Control",
                    "description": "Webhook endpoint has no authentication configured. Anyone on the network can trigger this AI workflow.",
                    "remediation": "Configure Basic Auth, Header Auth, or JWT verification on the n8n Webhook node."
                })

    # Static Security Check 4: Unfenced Agent Prompt
    for agent in agent_nodes:
        sys_msg = (agent.get("system_message") or "").lower()
        if not sys_msg or len(sys_msg.strip()) < 20:
            static_risks.append({
                "severity": "HIGH",
                "title": f"Missing or Vague System Prompt in Agent '{agent['name']}'",
                "category": "Prompt Boundary",
                "description": "Agent has no strict instructions or safety boundaries, leaving it highly vulnerable to prompt injection.",
                "remediation": "Provide explicit role instructions, scope limits, and instruction boundary fences."
            })
        elif "canary" in sys_msg or "secret" in sys_msg:
            static_risks.append({
                "severity": "CRITICAL",
                "title": f"Confidential Credentials Embedded in System Prompt of '{agent['name']}'",
                "category": "System Prompt Leakage",
                "description": "System prompt contains confidential tokens or secrets that can be extracted via prompt injection.",
                "remediation": "Never place real credentials into system prompts. Use secure external tool bindings."
            })

    return {
        "valid": True,
        "workflow_name": workflow_name,
        "total_nodes": len(nodes),
        "total_connections": sum(len(conns) for conns in connections.values()) if isinstance(connections, dict) else 0,
        "agent_nodes": agent_nodes,
        "trigger_nodes": trigger_nodes,
        "tool_nodes": tool_nodes,
        "other_nodes": other_nodes,
        "static_risks": static_risks,
        "risk_level": "CRITICAL" if any(r["severity"] == "CRITICAL" for r in static_risks) else (
            "HIGH" if any(r["severity"] == "HIGH" for r in static_risks) else (
                "MEDIUM" if any(r["severity"] == "MEDIUM" for r in static_risks) else "LOW"
            )
        )
    }

