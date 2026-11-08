# Pathfinder AI — AI Career Path Recommender

A career-direction tool for interns. Enter skills, interests, experience level, career goal, and weekly learning time to receive three career matches, relevant roles, and practical roadmaps.

## Features
- Career catalog spanning AI/ML, Generative AI, data analytics, software engineering, cybersecurity, and cloud/DevOps.
- AI-personalized ranking, explanations, job-role ideas, and learning roadmaps.
- Validated outputs constrained to the app's known career catalog.
- Interactive roadmap checklists stored in browser localStorage.
- Rules-based matching fallback when the external AI provider is unavailable.

## Stack
Python, Flask, Vireonix Chat Completions API, HTML, CSS, JavaScript, Vercel.

## AI provider
Uses Vireonix's OpenAI-compatible `POST /v1/chat/completions` endpoint with model `auto`; no API key or Authorization header is required. The free service is governed by per-IP hourly limits and has no SLA. On a temporary 429/provider error, the app labels and returns its local rules-based match instead of calling it AI-generated.

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
Skills, interests, experience level, and career goals are sent to Vireonix and may be retained and used for model training and improvement. The interface provides a disclosure and links to https://vireonix.ai/terms. Do not enter sensitive personal data or confidential information. Match scores are directional estimates, not statistically validated probabilities or employment guarantees. The catalog is a starter knowledge base, not a live labor-market feed. Progress is stored in the current browser only.
