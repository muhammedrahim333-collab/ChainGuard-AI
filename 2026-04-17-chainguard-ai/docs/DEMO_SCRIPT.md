# ChainGuard AI Demo Script

This script is designed for a 3 to 5 minute hackathon demo.

## Demo Goal

Show that ChainGuard AI acts like a virtual supply-chain manager for Indian SMEs by:
- monitoring suppliers
- predicting disruptions
- suggesting mitigations
- drafting actions
- learning over time with Hindsight memory

## 30-Second Opening

Use this intro:

> Indian SMEs often discover supply chain disruption too late, after margins are already hit. ChainGuard AI is a 24/7 autonomous multi-agent system built with LangGraph and Hindsight Cloud that watches suppliers continuously, predicts disruption early, recommends mitigations, and triggers business-ready actions before the loss happens.

## Suggested Demo Flow

### 1. Show the dashboard

Say:

> This is our Streamlit control center. We preload Punjab-focused supplier examples across textiles, food processing, manufacturing, and export businesses.

Show:
- supplier table
- Punjab risk heatmap
- Hindsight memory status in the sidebar

### 2. Explain the agents

Say:

> Behind the scenes, five LangGraph agents collaborate. The Monitor Agent scans external signals, the Risk Predictor scores suppliers, the Mitigation Agent proposes alternatives, the Action Agent drafts real-world responses, and the Orchestrator coordinates everything and writes back to memory.

Optional visual:
- open `AGENTS.md`

### 3. Simulate a disruption

Select:
- `Strike in Ludhiana`

Then click:
- `Run Autonomous Cycle`

Say:

> Now we simulate a logistics strike in Ludhiana. The system runs a full autonomous cycle, checking supplier context, generating risk scores, building mitigations, and preparing alert actions.

### 4. Show the result

Focus on:
- risk score table
- profit saved metric
- owner summary
- action center

Say:

> The system has elevated risk for the affected suppliers, estimated the business impact, and recommended fallback actions such as alternate sourcing, short-term buffer stock, and route adjustment. It also drafts the alert text and report automatically.

### 5. Highlight memory

Say:

> Every run stores supplier context, prior incidents, decisions, and outcomes into Hindsight memory using the retain, recall, and reflect pattern. Over time, ChainGuard AI gets smarter because it remembers what disruptions happened and which mitigation paths worked.

### 6. Close with business value

Say:

> This is not just a dashboard. It is an always-on operational guardian for SMEs that reduces chaos, protects profit, and helps owners act early instead of reacting late.

## One-Line Close

> ChainGuard AI turns supply-chain firefighting into proactive, memory-driven decision making.

## Demo Checklist

- Streamlit app opens cleanly
- Hindsight key is configured
- Disruption simulation is selected before recording
- Risk scores and profit impact are visible
- Action Center is expanded for at least one supplier
- README is open in a second tab for architecture proof if judges ask
