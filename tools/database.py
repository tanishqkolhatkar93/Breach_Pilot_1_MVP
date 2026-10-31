"""
AgentShield AI - SQLite Persistent Database Tool
Manages tables for agents, red-team sessions, attack events, findings, evaluations,
audit logs, and publishing decisions.
"""

import sqlite3
import json
import uuid
import datetime
from typing import List, Dict, Any, Optional
from config.settings import DB_PATH

def get_db_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(str(DB_PATH), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initializes all required database tables."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS agents (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        description TEXT,
        target_type TEXT NOT NULL,
        endpoint_url TEXT,
        canary_secret TEXT,
        system_prompt TEXT,
        status TEXT NOT NULL DEFAULT 'SUBMITTED',
        created_at TEXT NOT NULL
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS sessions (
        id TEXT PRIMARY KEY,
        agent_id TEXT NOT NULL,
        started_at TEXT NOT NULL,
        completed_at TEXT,
        status TEXT NOT NULL,
        initial_plan_json TEXT,
        replan_decision_json TEXT,
        risk_score REAL,
        recommendation TEXT,
        FOREIGN KEY (agent_id) REFERENCES agents(id)
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS findings (
        id TEXT PRIMARY KEY,
        session_id TEXT NOT NULL,
        agent_id TEXT NOT NULL,
        test_id TEXT NOT NULL,
        category TEXT NOT NULL,
        severity TEXT NOT NULL,
        title TEXT NOT NULL,
        description TEXT,
        evidence TEXT,
        confidence REAL DEFAULT 1.0,
        timestamp TEXT NOT NULL,
        FOREIGN KEY (session_id) REFERENCES sessions(id),
        FOREIGN KEY (agent_id) REFERENCES agents(id)
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS evaluations (
        id TEXT PRIMARY KEY,
        session_id TEXT NOT NULL,
        agent_id TEXT NOT NULL,
        test_id TEXT NOT NULL,
        category TEXT NOT NULL,
        prompt TEXT NOT NULL,
        expected_safe_behavior TEXT,
        target_response TEXT,
        actual_result TEXT,
        passed INTEGER NOT NULL,
        is_safe_refusal INTEGER DEFAULT 0,
        is_legitimate_pass INTEGER DEFAULT 0,
        severity TEXT NOT NULL,
        evidence TEXT,
        timestamp TEXT NOT NULL,
        FOREIGN KEY (session_id) REFERENCES sessions(id)
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS attack_events (
        id TEXT PRIMARY KEY,
        session_id TEXT NOT NULL,
        agent_id TEXT NOT NULL,
        phase TEXT NOT NULL,
        test_id TEXT,
        action TEXT NOT NULL,
        details TEXT,
        timestamp TEXT NOT NULL
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS audit_events (
        id TEXT PRIMARY KEY,
        event_type TEXT NOT NULL,
        agent_id TEXT,
        session_id TEXT,
        actor TEXT NOT NULL,
        details TEXT,
        timestamp TEXT NOT NULL
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS publishing_decisions (
        id TEXT PRIMARY KEY,
        agent_id TEXT NOT NULL,
        session_id TEXT,
        decision TEXT NOT NULL,
        risk_score REAL,
        reviewer_name TEXT NOT NULL,
        rationale TEXT,
        signature TEXT,
        timestamp TEXT NOT NULL,
        FOREIGN KEY (agent_id) REFERENCES agents(id)
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS leads (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        email TEXT NOT NULL,
        company TEXT,
        message TEXT,
        created_at TEXT NOT NULL
    )
    """)

    conn.commit()
    conn.close()

# Auto-initialize database on import
init_db()

