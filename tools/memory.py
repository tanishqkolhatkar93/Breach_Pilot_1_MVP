"""
AgentShield AI - Memory Tool
Provides persistent SQLite memory for vulnerability findings, agent history,
session state, attack execution events, and audit logs.
Demonstrates memory across attack steps and restarts.
"""

import uuid
import json
import datetime
from typing import List, Dict, Any, Optional
from tools.database import get_db_connection

def save_agent(agent_data: Dict[str, Any]) -> str:
    """Creates or updates an agent in the registry."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    agent_id = agent_data.get("id") or f"agent_{uuid.uuid4().hex[:8]}"
    now = datetime.datetime.now(datetime.timezone.utc).isoformat()
    
    cursor.execute("""
    INSERT OR REPLACE INTO agents (id, name, description, target_type, endpoint_url, canary_secret, system_prompt, status, created_at)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        agent_id,
        agent_data.get("name", "Unnamed Agent"),
        agent_data.get("description", ""),
        agent_data.get("target_type", "local_vulnerable"),
        agent_data.get("endpoint_url", ""),
        agent_data.get("canary_secret", ""),
        agent_data.get("system_prompt", ""),
        agent_data.get("status", "SUBMITTED"),
        agent_data.get("created_at", now)
    ))
    conn.commit()
    conn.close()
    return agent_id

def get_agent(agent_id: str) -> Optional[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM agents WHERE id = ?", (agent_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def list_agents() -> List[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM agents ORDER BY created_at DESC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def update_agent_status(agent_id: str, status: str) -> bool:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE agents SET status = ? WHERE id = ?", (status, agent_id))
    conn.commit()
    rows = cursor.rowcount
    conn.close()
    return rows > 0

def save_agent_session(session_data: Dict[str, Any]) -> str:
    """Creates or updates a red-team session."""
    conn = get_db_connection()
    cursor = conn.cursor()
    session_id = session_data.get("id") or f"sess_{uuid.uuid4().hex[:8]}"
    now = datetime.datetime.now(datetime.timezone.utc).isoformat()
    
    initial_plan = session_data.get("initial_plan_json")
    if isinstance(initial_plan, (dict, list)):
        initial_plan = json.dumps(initial_plan)
        
    replan = session_data.get("replan_decision_json")
    if isinstance(replan, (dict, list)):
        replan = json.dumps(replan)

    cursor.execute("""
    INSERT OR REPLACE INTO sessions (id, agent_id, started_at, completed_at, status, initial_plan_json, replan_decision_json, risk_score, recommendation)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        session_id,
        session_data.get("agent_id"),
        session_data.get("started_at", now),
        session_data.get("completed_at"),
        session_data.get("status", "IN_PROGRESS"),
        initial_plan,
        replan,
        session_data.get("risk_score"),
        session_data.get("recommendation")
    ))
    conn.commit()
    conn.close()
    return session_id

def save_finding(finding: Dict[str, Any]) -> str:
    """Stores a confirmed security vulnerability finding."""
    conn = get_db_connection()
    cursor = conn.cursor()
    finding_id = finding.get("id") or f"find_{uuid.uuid4().hex[:8]}"
    now = datetime.datetime.now(datetime.timezone.utc).isoformat()

    cursor.execute("""
    INSERT OR REPLACE INTO findings (id, session_id, agent_id, test_id, category, severity, title, description, evidence, confidence, timestamp)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        finding_id,
        finding.get("session_id", ""),
        finding.get("agent_id", ""),
        finding.get("test_id", ""),
        finding.get("category", "General"),
        finding.get("severity", "MEDIUM"),
        finding.get("title", "Security Finding"),
        finding.get("description", ""),
        finding.get("evidence", ""),
        finding.get("confidence", 1.0),
        finding.get("timestamp", now)
    ))
    conn.commit()
    conn.close()
    return finding_id

def get_previous_findings(agent_id: str, session_id: Optional[str] = None) -> List[Dict[str, Any]]:
    """Retrieves previous vulnerability findings for an agent across sessions."""
    conn = get_db_connection()
    cursor = conn.cursor()
    if session_id:
        cursor.execute("SELECT * FROM findings WHERE agent_id = ? AND session_id = ? ORDER BY timestamp ASC", (agent_id, session_id))
    else:
        cursor.execute("SELECT * FROM findings WHERE agent_id = ? ORDER BY timestamp DESC", (agent_id,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_agent_history(agent_id: str) -> Dict[str, Any]:
    """Retrieves full audit history, previous sessions, and all findings for an agent."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM sessions WHERE agent_id = ? ORDER BY started_at DESC", (agent_id,))
    sessions = [dict(r) for r in cursor.fetchall()]
    
    cursor.execute("SELECT * FROM findings WHERE agent_id = ? ORDER BY timestamp DESC", (agent_id,))
    findings = [dict(r) for r in cursor.fetchall()]
    
    cursor.execute("SELECT * FROM publishing_decisions WHERE agent_id = ? ORDER BY timestamp DESC", (agent_id,))
    decisions = [dict(r) for r in cursor.fetchall()]

    conn.close()
    return {
        "agent_id": agent_id,
        "sessions": sessions,
        "findings": findings,
        "publishing_decisions": decisions
    }

def save_attack_event(event: Dict[str, Any]) -> str:
    """Logs an attack execution event for the live event stream."""
    conn = get_db_connection()
    cursor = conn.cursor()
    event_id = event.get("id") or f"evt_{uuid.uuid4().hex[:8]}"
    now = datetime.datetime.now(datetime.timezone.utc).isoformat()
    
    details = event.get("details")
    if isinstance(details, (dict, list)):
        details = json.dumps(details)

    cursor.execute("""
    INSERT INTO attack_events (id, session_id, agent_id, phase, test_id, action, details, timestamp)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        event_id,
        event.get("session_id", ""),
        event.get("agent_id", ""),
        event.get("phase", "EXECUTE"),
        event.get("test_id", ""),
        event.get("action", ""),
        details,
        event.get("timestamp", now)
    ))
    conn.commit()
    conn.close()
    return event_id

def get_attack_events(session_id: str) -> List[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM attack_events WHERE session_id = ? ORDER BY timestamp ASC", (session_id,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def save_evaluation(eval_data: Dict[str, Any]) -> str:
    """Saves a structured evaluation record."""
    conn = get_db_connection()
    cursor = conn.cursor()
    eval_id = eval_data.get("id") or f"eval_{uuid.uuid4().hex[:8]}"
    now = datetime.datetime.now(datetime.timezone.utc).isoformat()

    cursor.execute("""
    INSERT OR REPLACE INTO evaluations (
        id, session_id, agent_id, test_id, category, prompt,
        expected_safe_behavior, target_response, actual_result,
        passed, is_safe_refusal, is_legitimate_pass, severity, evidence, timestamp
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        eval_id,
        eval_data.get("session_id"),
        eval_data.get("agent_id"),
        eval_data.get("test_id"),
        eval_data.get("category"),
        eval_data.get("prompt"),
        eval_data.get("expected_safe_behavior"),
        eval_data.get("target_response"),
        eval_data.get("actual_result"),
        1 if eval_data.get("passed") else 0,
        1 if eval_data.get("is_safe_refusal") else 0,
        1 if eval_data.get("is_legitimate_pass") else 0,
        eval_data.get("severity", "MEDIUM"),
        eval_data.get("evidence", ""),
        eval_data.get("timestamp", now)
    ))
    conn.commit()
    conn.close()
    return eval_id

def get_evaluations(session_id: str) -> List[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM evaluations WHERE session_id = ? ORDER BY rowid ASC", (session_id,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def save_audit_event(event_type: str, actor: str, details: str, agent_id: str = None, session_id: str = None) -> str:
    """Records an immutable audit event for security tracking."""
    conn = get_db_connection()
    cursor = conn.cursor()
    audit_id = f"audit_{uuid.uuid4().hex[:8]}"
    now = datetime.datetime.now(datetime.timezone.utc).isoformat()

    cursor.execute("""
    INSERT INTO audit_events (id, event_type, agent_id, session_id, actor, details, timestamp)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (audit_id, event_type, agent_id, session_id, actor, details, now))
    conn.commit()
    conn.close()
    return audit_id

def get_audit_events(limit: int = 100) -> List[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM audit_events ORDER BY timestamp DESC LIMIT ?", (limit,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def save_publishing_decision(decision_data: Dict[str, Any]) -> str:
    """Records a publication approval or block decision with audit signature."""
    conn = get_db_connection()
    cursor = conn.cursor()
    decision_id = decision_data.get("id") or f"dec_{uuid.uuid4().hex[:8]}"
    now = datetime.datetime.now(datetime.timezone.utc).isoformat()

    cursor.execute("""
    INSERT INTO publishing_decisions (id, agent_id, session_id, decision, risk_score, reviewer_name, rationale, signature, timestamp)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        decision_id,
        decision_data.get("agent_id"),
        decision_data.get("session_id"),
        decision_data.get("decision"),
        decision_data.get("risk_score"),
        decision_data.get("reviewer_name", "SecOps Officer"),
        decision_data.get("rationale", ""),
        decision_data.get("signature", f"SIG-{uuid.uuid4().hex[:12].upper()}"),
        decision_data.get("timestamp", now)
    ))
    conn.commit()
    conn.close()
    return decision_id

def get_publishing_decisions(agent_id: Optional[str] = None) -> List[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    if agent_id:
        cursor.execute("SELECT * FROM publishing_decisions WHERE agent_id = ? ORDER BY timestamp DESC", (agent_id,))
    else:
        cursor.execute("SELECT * FROM publishing_decisions ORDER BY timestamp DESC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

