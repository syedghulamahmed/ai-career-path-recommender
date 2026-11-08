# Pathfinder AI — AI Career Path Recommender

A career-direction tool for interns. Enter skills, interests, experience level, career goal, and weekly learning time to receive three career matches, relevant roles, and practical roadmaps.

## Features
- Career catalog spanning AI/ML, Generative AI, data analytics, software engineering, cybersecurity, and cloud/DevOps.
- AI-personalized ranking, explanations, job-role ideas, and learning roadmaps.
- Validated outputs constrained to the app's known career catalog.
- Interactive roadmap checklists stored in browser localStorage.
- Rules-based matching fallback when live AI inference is unavailable.

## Stack
Python, Flask, BlockRun Chat Completions API, HTML, CSS, JavaScript, Vercel.

## AI provider
Uses BlockRun's OpenAI-compatible `POST /api/v1/chat/completions` endpoint with free model `nvidia/nemotron-3.5-bolt`, with `poolside/laguna-xs-2.1` as a fallback. No API key, wallet, payment card, or account is required. Free-model capacity and IP rate limits can change. The route validates model output against the app's career catalog and returns a labelled rules-based match when the provider is unavailable.

## Run locally
```bash
python -m venv .venv
# Windows: .venv\\Scripts\\activate
# macOS/Linux:
source .venv/bin/activate
pip install -r requirements.txt
python -m flask --app api.index run --debug
```
Open http://127.0.0.1:5000.

No provider API key is required.

## API
- `GET /api/health` — health/provider metadata.
- `POST /api/recommend` — JSON fields: `skills`, `interests`, `level`, `goal`, and `hours_per_week`.

## Privacy and limitations
Skills, interests, experience level, and career goals are routed through BlockRun to the selected model provider. BlockRun states it does not store or train on prompts; upstream provider terms apply. See [BlockRun Privacy](https://blockrun.ai/privacy) and [Terms](https://blockrun.ai/terms). Do not enter sensitive personal data or confidential information. Match scores are directional estimates, not statistically validated probabilities or employment guarantees. The catalog is a starter knowledge base, not a live labor-market feed. Progress is stored in the current browser only.
