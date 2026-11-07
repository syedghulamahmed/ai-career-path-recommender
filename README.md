# Pathfinder AI — AI Career Path Recommender

A career recommendation tool for interns. Enter skills, interests, experience level, career goal and weekly learning time to receive three ranked career directions, relevant job roles and practical learning roadmaps.

## Features
- Matching across AI/ML, Generative AI, data analytics, software engineering, cybersecurity and cloud/DevOps.
- Three career recommendations with heuristic match indicators.
- Five-step learning roadmap for each recommendation.
- Interactive milestone checklists; progress persists in browser localStorage.
- Optional OpenAI-powered personalization; built-in matching works without an API key.
- Flask REST API and responsive interface.

## Run locally
```bash
python -m venv .venv
# Windows: .venv\\Scripts\\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
python -m flask --app api.index run --debug
```
Open http://127.0.0.1:5000.

## Environment
Copy `.env.example` to `.env` and set `OPENAI_API_KEY`. Optional `OPENAI_MODEL` defaults to `gpt-4.1-mini`. Never commit real keys. Without a key, the local matching engine is used.

## API
- `GET /api/health` — health check.
- `POST /api/recommend` — JSON body: `skills`, `interests`, `level`, `goal`, `hours_per_week`.

## Deployment
Configured for Vercel Python Functions. Add `OPENAI_API_KEY` to the Vercel project's environment variables and redeploy to enable the optional AI layer.

## Limitations
Progress is stored in the current browser and is not synced across devices. Match scores are heuristic indicators, not statistically validated probabilities or employment guarantees. The career catalog is a starter knowledge base, not a live labor-market feed.
