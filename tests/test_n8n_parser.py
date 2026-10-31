"""
AgentShield AI - n8n Workflow Parser & Security Analyzer Tests
Verifies schema validation, node topology extraction, and static risk identification.
"""

import json
from pathlib import Path
from tools.n8n_parser import parse_n8n_workflow

def test_parse_valid_sample_workflow():
    sample_path = Path(__file__).resolve().parent.parent / "samples" / "sample_n8n_customer_support_workflow.json"
    assert sample_path.exists(), f"Sample file not found at {sample_path}"
    
    with open(sample_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    result = parse_n8n_workflow(data)
    assert result["valid"] is True
    assert "Customer Support" in result["workflow_name"]
    assert len(result["agent_nodes"]) == 1
    assert len(result["trigger_nodes"]) == 1
    assert len(result["tool_nodes"]) >= 2
    assert len(result["static_risks"]) >= 2
    
    # Check that unauthenticated webhook is flagged
    risk_titles = [r["title"] for r in result["static_risks"]]
    assert any("Webhook" in t for t in risk_titles)

def test_parse_invalid_workflow():
    # Non-dict
    res1 = parse_n8n_workflow([])
    assert res1["valid"] is False

    # Missing nodes
    res2 = parse_n8n_workflow({"name": "Empty"})
    assert res2["valid"] is False

def test_static_destructive_sql_risk():
    workflow = {
        "name": "SQL Bot",
        "nodes": [
            {
                "name": "AI Agent",
                "type": "@n8n/n8n-nodes-langchain.agent",
                "parameters": {"options": {"systemMessage": "You are a safe SQL assistant."}}
            },
            {
                "name": "Postgres Node",
                "type": "n8n-nodes-base.postgres",
                "parameters": {"query": "DROP TABLE users;"}
            }
        ],
        "connections": {}
    }
    result = parse_n8n_workflow(workflow)
    assert result["valid"] is True
    assert any(r["severity"] == "CRITICAL" and "Destructive Database" in r["title"] for r in result["static_risks"])

if __name__ == "__main__":
    test_parse_valid_sample_workflow()
    test_parse_invalid_workflow()
    test_static_destructive_sql_risk()
    print("All n8n parser tests passed!")

