# ChainGuard AI Submission Checklist

## Repository

- Source code pushed to GitHub
- `README.md` updated with setup, architecture, and demo flow
- `AGENTS.md` explains every agent role
- `.env` is not committed
- Screenshots or screen recording thumbnails added if needed

## Demo Video

- 3 to 5 minute recording
- Start with the problem statement
- Show the Streamlit dashboard
- Run `Strike in Ludhiana`
- Show risk score, mitigation, action center, and profit impact
- Mention Hindsight memory explicitly

## Live Demo

- Local Streamlit app starts successfully
- Core `.env` values added
- At least Hindsight and Groq are configured
- Optional APIs can be missing because the app has safe fallbacks

## Content Deliverables

- Article draft adapted from `docs/CONTENT_PACK.md`
- Social post draft adapted from `docs/CONTENT_PACK.md`
- Video narration adapted from `docs/CONTENT_PACK.md`

## Judge FAQ

- Why multi-agent?
  Different operational responsibilities are easier to reason about and demo clearly.

- Why Hindsight?
  Supply-chain decisions are history-dependent, so memory improves decisions over time.

- Why Punjab?
  Punjab has strong textile, food, manufacturing, and export clusters that match the problem well.
