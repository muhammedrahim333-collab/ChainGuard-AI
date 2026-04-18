# Contributing

Thanks for contributing to ChainGuard AI.

## Development Setup

1. Create a Python 3.12+ environment.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Create `.env` from `.env.example`.
4. Run the app:

```bash
streamlit run app.py
```

## Project Standards

- Keep the architecture modular
- Prefer small, well-named functions
- Document new agents, tools, and flows in `AGENTS.md` or `README.md`
- Do not commit secrets or `.env`
- Keep supplier demo data clearly labeled as demo assumptions when values are simulated

## Pull Request Checklist

- Code runs locally
- README stays accurate
- New environment variables are documented
- Agent behavior changes are reflected in `AGENTS.md`
- Screenshots or demo notes are updated when the UI changes
