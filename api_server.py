"""
AgentShield AI - REST API Bridge for Next.js Frontend
Exposes the core agentic orchestrator, risk scoring engine, and publishing gatekeeper
over REST endpoints for the modern Next.js React frontend.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import uvicorn
import uuid

from tools.memory import (
    list_agents, get_agent, save_agent, update_agent_status,
    get_previous_findings, get_evaluations, get_audit_events, get_publishing_decisions
)
from agent.orchestrator import orchestrator
from security.publishing_gate import publishing_gatekeeper
from reports.report_generator import generate_json_report, generate_html_report
from config.settings import DEFAULT_CANARY_SECRET

app = FastAPI(
    title="AgentShield AI Security API",
    version="2.4.0",
    description="Autonomous Red-Team Safety Judge API for Agent Marketplaces"
)

# Enable CORS for Next.js frontend development server (localhost:3000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class AgentSubmission(BaseModel):
    name: str
    description: str
    target_type: str = "local_vulnerable"
    endpoint_url: str = ""
    canary_secret: str = DEFAULT_CANARY_SECRET
    system_prompt: str = ""

class AuditRequest(BaseModel):
    agent_id: str
    max_budget: Optional[int] = 12

class ApprovalRequest(BaseModel):
    agent_id: str
    session_id: str
    reviewer_name: str
    rationale: str

class PublishRequest(BaseModel):
    agent_id: str
    publisher_name: str

@app.get("/api/health")
def health():
    return {"status": "online", "engine": "AgentShield Autonomous Judge v2.4", "latency_ms": 14.2}

@app.get("/api/agents")
def get_agents():
    return list_agents()

@app.post("/api/agents")
def create_agent(agent_data: AgentSubmission):
    new_id = save_agent(agent_data.dict())
    return {"success": True, "agent_id": new_id}

@app.post("/api/audit")
def run_audit_endpoint(req: AuditRequest):
    agent = get_agent(req.agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail=f"Agent '{req.agent_id}' not found.")
    
    result = orchestrator.run_audit(agent)
    return result

@app.get("/api/gatekeeper/eligibility/{agent_id}")
def check_gatekeeper(agent_id: str):
    return publishing_gatekeeper.evaluate_publishing_eligibility(agent_id)

@app.post("/api/gatekeeper/approve")
def approve_agent(req: ApprovalRequest):
    ok, msg, sig_data = publishing_gatekeeper.submit_human_approval(
        agent_id=req.agent_id,
        session_id=req.session_id,
        reviewer_name=req.reviewer_name,
        rationale=req.rationale
    )
    if not ok:
        raise HTTPException(status_code=403, detail=msg)
    return {"success": True, "message": msg, "signature": sig_data.get("signature")}

@app.post("/api/gatekeeper/publish")
def publish_agent(req: PublishRequest):
    ok, msg = publishing_gatekeeper.publish_to_marketplace(req.agent_id, req.publisher_name)
    if not ok:
        raise HTTPException(status_code=403, detail=msg)
    return {"success": True, "message": msg}

if __name__ == "__main__":
    uvicorn.run("api_server:app", host="0.0.0.0", port=8000, reload=True)

