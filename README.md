# ChainGuard AI

ChainGuard AI is an autonomous multi-agent supply-chain risk guardian for Indian SMEs, especially Punjab-based manufacturing, textiles, food processing, and export businesses.

It uses LangGraph for orchestration, Groq for reasoning, Hindsight Cloud for persistent memory, and Streamlit for the dashboard.

## Problem

Indian SMEs often detect supplier disruption too late. A delayed truck, raw material spike, weather event, or export bottleneck can quickly become a production delay and margin loss.

ChainGuard AI acts like a virtual supply-chain manager that never sleeps:
- continuously watches supplier risk
- predicts disruption before it escalates
- recommends mitigations
- prepares alerts, reports, and operational updates
- learns from every incident through memory

## Why It Matters

- SMEs usually do not have a 24/7 control tower
- supply chains are regional, fragile, and highly context-dependent
- past incidents matter, so memory is critical
- owners need clear action, not just raw data

## Features

- Multi-agent workflow with an orchestrator, monitor, predictor, mitigation, and action agent
- Persistent memory with Hindsight Cloud using the official `retain / recall / reflect` pattern
- Punjab-focused live risk map and supplier risk table
- Disruption simulator for demo scenarios like strikes, floods, and export delays
- Google Sheets, WhatsApp, and email integration hooks
- English, Hindi, and Punjabi-style summaries
- Profit impact estimation so owners can see savings clearly

## Architecture

### Agents

- `Orchestrator Agent`: coordinates the entire cycle and maintains run context
- `Monitor Agent`: gathers supplier, weather, market, logistics, and news signals
- `Risk Predictor Agent`: scores each supplier from 0 to 100 with reasoning
- `Mitigation Agent`: suggests practical backup actions for SME owners
- `Action Agent`: prepares WhatsApp, email, Sheets, and report outputs

Detailed agent contracts live in `AGENTS.md`.

### Memory

ChainGuard AI uses Hindsight Cloud from the first step of the workflow.

- `retain`: supplier facts, monitoring events, risk decisions, outcomes
- `recall`: similar incidents, supplier history, prior mitigation context
- `reflect`: higher-level lessons about what patterns and actions work best

### Graph Flow

`orchestrator_start -> monitor -> predictor -> mitigation -> action -> finalize`

## Tech Stack

- Python 3.12+
- LangGraph
- LangChain
- Groq
- Hindsight Cloud
- Streamlit
- Pandas
- Plotly
- PyDeck

## Project Structure

```text
chainguard-ai/
  agents/
  data/
  docs/
  graph/
  memory/
  models/
  services/
  tools/
  utils/
  AGENTS.md
  app.py
  config.py
  requirements.txt
  .env.example
```

## Quick Start

1. Create and activate a Python 3.12+ virtual environment.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Copy `.env.example` to `.env`.
4. Add at minimum:

```env
GROQ_API_KEY=your_groq_key
HINDSIGHT_API_KEY=your_hindsight_key
HINDSIGHT_API_URL=https://api.hindsight.vectorize.io
HINDSIGHT_BANK_ID=chainguard-ai
```

5. Run the app:

```bash
streamlit run app.py
```

On this Windows machine, a verified working command is:

```powershell
powershell -ExecutionPolicy Bypass -File .\run_chainguard.ps1
```

## Demo Data

The bundled starter suppliers are internet-sourced demo examples based on public Punjab company websites.

Included examples span:
- Ludhiana textiles
- Amritsar food processing
- Jalandhar manufacturing and export businesses

Important:
- company identity, city, website, and public contact references were sourced from public websites
- quantities, unit costs, and lead times are simulation assumptions added for demo usability

## Required Environment Variables

### Core

- `GROQ_API_KEY`
- `HINDSIGHT_API_KEY`
- `HINDSIGHT_API_URL=https://api.hindsight.vectorize.io`
- `HINDSIGHT_BANK_ID=chainguard-ai`

### Optional integrations

- `TAVILY_API_KEY`
- `SERPER_API_KEY`
- `OPENWEATHER_API_KEY`
- `WHATSAPP_ACCESS_TOKEN`
- `WHATSAPP_PHONE_NUMBER_ID`
- `WHATSAPP_RECIPIENT_PHONE`
- `SMTP_HOST`
- `SMTP_PORT`
- `SMTP_USERNAME`
- `SMTP_PASSWORD`
- `ALERT_EMAIL_TO`
- `GOOGLE_SERVICE_ACCOUNT_JSON`
- `GOOGLE_SHEETS_ID`

## Hindsight Cloud Setup

ChainGuard AI is wired for Hindsight Cloud from the start.

1. Create an API key in Hindsight Cloud.
2. Create or reuse a bank ID, for example `chainguard-ai`.
3. Put these in your `.env`:

```env
HINDSIGHT_API_URL=https://api.hindsight.vectorize.io
HINDSIGHT_API_KEY=hsk_your_key
HINDSIGHT_BANK_ID=chainguard-ai
```

The app uses:
- `retain` to store supplier facts, monitoring results, decisions, and outcomes
- `recall` to fetch similar supplier incidents and historical context
- `reflect` to summarize learned patterns and smarter mitigations over time

## Demo Flow

1. Open the dashboard.
2. Start with the bundled Punjab demo suppliers or add your own suppliers.
3. Choose a disruption like `Strike in Ludhiana`.
4. Click `Run Autonomous Cycle`.
5. Watch the graph run:
   - monitor fresh signals
   - score suppliers
   - generate mitigations
   - prepare WhatsApp, email, sheet, and report actions
6. Review profit impact and summary.

For a judged walkthrough, use `docs/DEMO_SCRIPT.md`.

## Example Demo Scenario

Scenario:
- A Ludhiana yarn supplier faces a transport strike.

What ChainGuard AI does:
- detects strike-related logistics signals
- increases supplier risk score
- estimates cost of delay
- recommends alternate vendor and short-term stock buffer
- drafts alert in English/Hindi/Punjabi mix
- updates Google Sheet and incident report

Example value statement:
- `This disruption could have cost around Rs. 2.4 lakh. ChainGuard AI identified a backup sourcing path and reduced the projected impact.`

## Notes

- The app can run in demo mode without every external API key.
- When Hindsight is unavailable, a lightweight local fallback store keeps the UI usable, but production memory should use Hindsight Cloud.
- WhatsApp and Google Sheets actions are implemented as real connectors with safe fallbacks when credentials are missing.
- Internet access is used by configured tools such as Tavily, Serper, and weather APIs when keys are available.

## Submission Assets

- Demo script: `docs/DEMO_SCRIPT.md`
- Content pack: `docs/CONTENT_PACK.md`
- Submission checklist: `docs/SUBMISSION_CHECKLIST.md`

## Repository Notes

- License: `MIT`
- Contribution guide: `CONTRIBUTING.md`
- Suggested GitHub repo metadata: `REPO_INFO.md`

## Official References Used

- [Hindsight Cloud docs](https://docs.hindsight.vectorize.io/)
- [Hindsight LangGraph integration README](https://github.com/vectorize-io/hindsight/tree/main/hindsight-integrations/langgraph)
- [Hindsight Python SDK guide](https://hindsight.vectorize.io/sdks/python)
