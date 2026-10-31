# 🛡️ AgentShield AI — Complete Documentation Suite

> **Grand Finale — National Level Agentic AI Hackathon 2026**  
> **Problem 01:** AI Agent Safety Red-Team Judge  
> **Tagline:** *"Attack. Evaluate. Protect. Before You Publish."*

---

## ⚡ Quick Start: Need to Explain This Fast?
If you are explaining this project to a judge, recruiter, or friend, read the **Easy Explainer & Pitch Guide**:
👉 **[00. Easy Explainer & 2-Minute Pitch Guide (Start Here!)](./00_EASY_EXPLAINER_AND_PITCH.md)**  
*(Includes 30-second elevator pitch, simple Airport Security analogy, word-for-word demo script, and quick answers to jury questions.)*

---

## 📚 Complete Documentation Suite Overview

```
docs/
├── 00_EASY_EXPLAINER_AND_PITCH.md        # ⚡ Plain-English Guide, Analogy, & Word-for-Word Pitch Script
├── 01_PROBLEM_STATEMENT_AND_MARKET.md    # Problem Statement, Market Metrics, Personas, References
├── 02_OUR_SOLUTION_AND_INNOVATION.md     # Multi-Agent Red-Team Solution, Core Innovations & Flow
├── 03_TECHNICAL_ARCHITECTURE.md          # System Topography, Sequence Flows, Gatekeeper & State Machine
├── 04_TECH_STACK_AND_COMPARISON.md       # Tech Stack Rationale, Trade-offs & Deep Comparisons
└── 05_HACKATHON_JURY_FAQ.md              # 16 In-Depth Technical & Business Questions for Hackathon Jury
```

---

### 0. [00. Easy Explainer & 2-Minute Pitch Guide](./00_EASY_EXPLAINER_AND_PITCH.md)
- **The Airport TSA Analogy:** How AgentShield scans AI agents just like airport scanners scan luggage.
- **The 5 Attacks Explained in Plain English:** No heavy jargon.
- **2-Minute Demo Presentation Script:** Exactly what to say during the hackathon judging turn.
- **Top 5 Jury Questions Answered in 1 Sentence:** Short, crisp, and confident answers.

---

### 1. [01. Problem Statement & Market Analysis](./01_PROBLEM_STATEMENT_AND_MARKET.md)
- **The Shift to Agentic Vulnerabilities:** Why single-turn chatbot filters fail on tool-augmented agents.
- **The 6 Core Failure Modes:** Prompt injection, system prompt & canary leakage, PII exfiltration, tool abuse & excessive privileges, scope drift, and lack of pre-deployment testing.
- **Market Sizing & Economic Impact:** Real-world data from IBM Cost of a Data Breach 2025/2026:
  - **13% to 20%** of organizations reporting AI model/application breaches.
  - **97%** of breached organizations lacking AI-level access controls.
  - **$5.89 Million** average financial loss per enterprise prompt-injection breach.
  - **₹22 Crore** average data breach cost in India.
  - **80%+** of enterprise software embedding autonomous agents by 2027 (Gartner).
- **Target Audience:** Enterprise SecOps teams, agent marketplace operators, autonomous agent startups, and CISOs.
- **Detailed User Personas:** Maya Chen (Principal AI Red-Team Architect), Vikram Patel (VP of Trust & Safety), Alex Rivera (Lead Autonomous Agent Engineer).
- **Industry References:** IBM Security, OWASP Top 10 for LLMs, NIST AI RMF, Gartner.

---

### 2. [02. Our Solution & Technological Innovations](./02_OUR_SOLUTION_AND_INNOVATION.md)
- **Autonomous Red-Team SOC:** Operating a collaborative team of specialized autonomous agents.
- **The 6-Stage Autonomous Agentic Cycle:**
  $$\text{PLAN} \longrightarrow \text{ACT} \longrightarrow \text{OBSERVE} \longrightarrow \text{RE-PLAN} \longrightarrow \text{ACT (Adaptive)} \longrightarrow \text{EVALUATE} \longrightarrow \text{DECIDE}$$
- **The 5 Core Threat Categories:** Prompt injection, secret & canary extraction, PII harvesting, off-topic misuse, tool abuse.
- **Core Technological Innovations:**
  1. Synthetic Tool Sandbox (`mock_tools.py` for SQL, refunds, email).
  2. Cryptographic canary token injection & tracing (`CANARY-9981-ALPHA`).
  3. Long-term persistent SQLite memory tool (`memory.py`).
  4. Deterministic risk scoring penalty matrix (Base 100 - Severity Deductions).
  5. Enforceable marketplace publishing gatekeeper state machine.
- **Dual Demonstration Targets:** `ShopBot-Vulnerable v1.0` (Score: 0/100 $\rightarrow$ `BLOCKED`) vs. `ShopShield-Secure v2.4` (Score: 100/100 $\rightarrow$ `APPROVED`).
- **Dual Mode Operation:** Cloud-connected Google Gemini 2.5 Flash + 100% offline deterministic fallback.

---

### 3. [03. Technical Architecture & System Design](./03_TECHNICAL_ARCHITECTURE.md)
- **High-Level System Topography:** Streamlit Enterprise SOC UI (`app.py`), Central Multi-Agent Orchestrator, Sandboxed Mock Tools, and SQLite persistent memory.
- **Visual Mermaid Diagrams:** System architecture, end-to-end agentic sequence diagram, and gatekeeper state machine.
- **Agent Module Breakdown:** Planner, Executor, Observer, Adaptive Re-Planner, Evaluator, Central Orchestrator.
- **Mathematical Scoring Formulas:** Formulas for Attack Success Rate ($ASR$), Refusal Rate ($RR$), Pass Rate ($PR$), and Severity-Weighted Risk Score.
- **Database Schema (ER Diagram):** Full relational schema for `agents`, `sessions`, `attack_events`, `findings`, `evaluations`, and `audit_ledger`.
- **Publishing Gatekeeper Invariants:** Formal state transitions and cryptographic SHA-256 signature generation.

---

### 4. [04. Tech Stack Selection & Architectural Justification](./04_TECH_STACK_AND_COMPARISON.md)
- **Complete Tech Stack Breakdown:** Streamlit 1.30+ (`app.py`), Custom Cyber Dark CSS (`assets/styles.css`), Plus Jakarta Sans, Google Gemini 2.5 Flash (`google-genai`), SQLite 3 (WAL mode), PyTest (18 tests), and optional decoupled FastAPI REST bridge.
- **In-Depth Architectural Justification ("Why This Instead of Others?"):**
  - **Primary Frontend:** Streamlit with Custom Enterprise Cyber CSS vs. Standard Streamlit vs. Standalone React / Angular.
  - **Direct Python Binding:** Why zero-serialization Python memory binding outperforms fragile Node/npm build pipelines.
  - **AI / LLM:** Google Gemini 2.5 Flash via official `google-genai` SDK vs. GPT-4o / Claude 3.5 Sonnet vs. LangChain / CrewAI abstractions.
  - **Storage:** SQLite 3 with WAL Mode vs. PostgreSQL vs. MongoDB vs. Vector DBs.
  - **Evaluation Engine:** Hybrid Deterministic Evaluator (Canaries + Heuristics + LLM) vs. Pure LLM-as-a-Judge.
- **Comprehensive Benchmark & Trade-off Matrix.**

---

### 5. [05. Hackathon Jury & Technical Judge FAQ](./05_HACKATHON_JURY_FAQ.md)
- **16 In-Depth Technical & Business Q&As:**
  - Track & problem alignment with Problem 01.
  - True autonomous multi-agent behavior vs. hardcoded scripts.
  - Benchmark ground truth and evaluation reproducibility.
  - False positive vs. false negative handling.
  - Concrete walkthrough of adaptive re-planning in action.
  - Sandbox safety and accidental harm prevention.
  - Gatekeeper tamper-proofing and state machine guarantees.
  - Regulatory audit trails and cryptographic signatures.
  - Zero-dependency air-gapped and offline execution.
  - Cost (<$0.001/audit) and latency (<15s) metrics.
  - Differentiation from Garak, PyRIT, and Promptfoo.
  - Connecting custom developer agents (REST / Python callable).
  - Business alignment with ₹22 crore Indian data breach and $5.89M prompt injection loss metrics.
  - Future technical roadmap (multi-modal attacks, CI/CD GitHub Actions, swarm red-teaming).

---

## ⚡ Quick Start Command Reference

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run automated test suite (All 15 tests pass)
python run_tests.py

# 3. Launch Python Streamlit SOC Console
streamlit run app.py

# 4. (Optional) Launch FastAPI Backend & Next.js Frontend
python api_server.py
cd frontend && npm run dev
```
