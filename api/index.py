import os
import json
from flask import Flask, jsonify, request, send_from_directory

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 24 * 1024
MAX_ITEMS = 20
MAX_ITEM_LENGTH = 80

CAREERS = [
 {"id":"aiml","title":"AI / Machine Learning Engineer","family":"AI & Data","skills":["python","statistics","machine learning","pandas","numpy","tensorflow","pytorch"],"interests":["artificial intelligence","machine learning","data","research"],"roles":["Junior ML Engineer","AI Engineer Intern","Machine Learning Intern"],"steps":[("Python for data","Practice Python, NumPy, pandas and data cleaning."),("Math foundations","Study probability, linear algebra and model metrics."),("Classical ML","Build regression, classification and clustering models."),("Deep learning","Learn neural network fundamentals with PyTorch or TensorFlow."),("Portfolio project","Ship an evaluated, documented ML project.")]},
 {"id":"genai","title":"Generative AI Developer","family":"AI & Data","skills":["python","javascript","apis","llm","prompt engineering","openai","rag","embeddings"],"interests":["generative ai","chatbots","automation","language"],"roles":["Generative AI Developer Intern","LLM Application Developer","AI Automation Engineer"],"steps":[("API engineering","Build reliable services and consume REST APIs."),("LLM fundamentals","Understand tokens, context windows and structured outputs."),("Prompt evaluation","Test prompts for quality, safety and failure cases."),("RAG systems","Learn embeddings, chunking and grounded retrieval."),("Deploy an AI product","Build and deploy a useful assistant with clear limitations.")]},
 {"id":"data","title":"Data Analyst","family":"AI & Data","skills":["sql","excel","python","statistics","power bi","tableau","pandas"],"interests":["data","business","visualization","research"],"roles":["Junior Data Analyst","BI Intern","Analytics Engineer Intern"],"steps":[("Data cleaning","Practice spreadsheet formulas and tidy datasets."),("SQL","Learn joins, aggregations, CTEs and window functions."),("Statistics","Study distributions, sampling and hypothesis testing."),("Dashboards","Build useful Power BI or Tableau dashboards."),("Case study","Publish an analysis with evidence-based recommendations.")]},
 {"id":"backend","title":"Backend Software Engineer","family":"Software Engineering","skills":["python","javascript","java","node.js","apis","sql","databases","git","docker"],"interests":["backend","systems","architecture","problem solving"],"roles":["Backend Developer Intern","Python Developer Intern","API Developer"],"steps":[("Programming","Practice data structures, error handling and testing."),("Web APIs","Build REST endpoints, validation and authentication."),("Databases","Model relational data and write efficient SQL."),("Production basics","Learn Git, Docker, logging and deployment."),("Capstone","Ship a tested API with a database and README.")]},
 {"id":"frontend","title":"Frontend / Full-Stack Developer","family":"Software Engineering","skills":["html","css","javascript","typescript","react","next.js","apis","git"],"interests":["frontend","design","web development","user experience"],"roles":["Frontend Developer Intern","React Developer Intern","Full-Stack Developer Intern"],"steps":[("Web foundations","Master semantic HTML, CSS and responsive design."),("JavaScript","Practice async code, modules and TypeScript."),("React","Build reusable components, forms and state."),("Full-stack","Connect APIs, authentication and persistent storage."),("Portfolio","Deploy an accessible project and document it.")]},
 {"id":"cyber","title":"Cybersecurity Analyst","family":"Infrastructure & Security","skills":["networking","linux","python","security","wireshark","siem"],"interests":["cybersecurity","networks","investigation","security"],"roles":["SOC Analyst Intern","Cybersecurity Intern","Junior Security Analyst"],"steps":[("Networking","Understand TCP/IP, DNS, HTTP, ports and subnetting."),("Linux","Use the CLI and Python for safe automation."),("Security","Study access control, vulnerabilities and threat models."),("Monitoring","Practice log analysis in a legal lab environment."),("Portfolio","Document defensive lab investigations and fixes.")]},
 {"id":"cloud","title":"Cloud / DevOps Engineer","family":"Infrastructure & Security","skills":["linux","git","docker","aws","azure","ci/cd","networking","python"],"interests":["cloud","automation","infrastructure","reliability"],"roles":["Cloud Engineer Intern","DevOps Intern","Platform Engineering Intern"],"steps":[("Linux & networking","Build confidence with shell, DNS and HTTP."),("Git & scripting","Automate repeatable tasks with Git and Python."),("Containers","Package an application using Docker."),("Cloud","Deploy a service and learn IAM, storage and networking."),("CI/CD","Automate tests and deployment with a pipeline.")]}
]


def match(profile):
    skills = [x.lower() for x in profile["skills"]]
    interests = [x.lower() for x in profile["interests"]]
    ranked = []
    for career in CAREERS:
        skill_hits = sum(any(k in s or s in k for s in skills) for k in career["skills"])
        interest_hits = sum(any(k in s or s in k for s in interests) for k in career["interests"])
        ranked.append((min(96, 35 + skill_hits * 9 + interest_hits * 11), career))
    ranked.sort(key=lambda item: item[0], reverse=True)
    return {
        "summary": "Your strongest matches are ranked from the skills and interests you entered. Treat these as starting hypotheses and validate them through projects and experience.",
        "recommendations": [
            {
                "id": career["id"], "title": career["title"], "family": career["family"],
                "match": score, "roles": career["roles"],
                "reason": "Matched against your stated skills and interests. Use this roadmap to close relevant skill gaps.",
                "steps": [{"title": step[0], "detail": step[1], "tag": "milestone"} for step in career["steps"]],
            }
            for score, career in ranked[:3]
        ],
        "source": "rules",
    }


def with_ai(profile, fallback):
    key = os.getenv("OPENAI_API_KEY")
    if not key:
        return fallback
    try:
        from openai import OpenAI
        client = OpenAI(api_key=key, timeout=12.0, max_retries=0)
        response = client.chat.completions.create(
            model=os.getenv("OPENAI_MODEL", "gpt-4.1-mini"),
            temperature=0.3,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": "Return JSON with summary and exactly 3 recommendations. Each recommendation must have id,title,family,match (integer 1-99),roles (2-4 strings),reason,steps (5 objects with title,detail,tag). Only use the candidate paths supplied. Do not invent careers or guarantee employment."},
                {"role": "user", "content": json.dumps({"profile": profile, "candidate_paths": fallback["recommendations"]})},
            ],
        )
        data = json.loads(response.choices[0].message.content or "{}")
        candidates = {item["id"]: item for item in fallback["recommendations"]}
        recommendations = data.get("recommendations")
        if not isinstance(data.get("summary"), str) or not isinstance(recommendations, list) or len(recommendations) != 3:
            return fallback
        cleaned = []
        for item in recommendations:
            if not isinstance(item, dict) or item.get("id") not in candidates:
                return fallback
            candidate = candidates[item["id"]]
            if not isinstance(item.get("match"), int) or not 1 <= item["match"] <= 99:
                return fallback
            roles = item.get("roles")
            steps = item.get("steps")
            if not isinstance(roles, list) or not 2 <= len(roles) <= 4 or not all(isinstance(x, str) for x in roles):
                return fallback
            if not isinstance(steps, list) or len(steps) != 5 or not all(isinstance(x, dict) and isinstance(x.get("title"), str) and isinstance(x.get("detail"), str) for x in steps):
                return fallback
            cleaned.append({
                "id": candidate["id"], "title": candidate["title"], "family": candidate["family"],
                "match": item["match"], "roles": [x[:100] for x in roles],
                "reason": str(item.get("reason", candidate["reason"]))[:500],
                "steps": [{"title": x["title"][:120], "detail": x["detail"][:500], "tag": str(x.get("tag", "milestone"))[:40]} for x in steps],
            })
        return {"summary": data["summary"][:1000], "recommendations": cleaned, "source": "openai"}
    except Exception:
        app.logger.exception("Career personalization failed; using deterministic recommendations")
        return fallback


def parse_text_list(value, field):
    if not isinstance(value, list):
        raise ValueError(f"{field} must be a list.")
    if len(value) > MAX_ITEMS:
        raise ValueError(f"{field} can contain at most {MAX_ITEMS} entries.")
    cleaned = []
    for item in value:
        if not isinstance(item, str):
            raise ValueError(f"Every {field} entry must be text.")
        item = item.strip()
        if not item or len(item) > MAX_ITEM_LENGTH:
            raise ValueError(f"Each {field} entry must contain 1 to {MAX_ITEM_LENGTH} characters.")
        cleaned.append(item)
    return cleaned


@app.get("/")
def home():
    return send_from_directory(os.path.dirname(__file__), "index.html")


@app.get("/api/health")
def health():
    return jsonify({"status": "ok", "service": "career-path-recommender", "ai_configured": bool(os.getenv("OPENAI_API_KEY"))})


@app.post("/api/recommend")
def recommend():
    if not request.is_json:
        return jsonify({"error": "Send a JSON request."}), 400
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"error": "Request body must be a JSON object."}), 400
    try:
        skills = parse_text_list(data.get("skills", []), "Skills")
        interests = parse_text_list(data.get("interests", []), "Interests")
        if not skills and not interests:
            return jsonify({"error": "Add at least one skill or interest."}), 400

        level = data.get("level", "Beginner")
        goal = data.get("goal", "Explore career options")
        hours = data.get("hours_per_week", 6)
        if not isinstance(level, str) or len(level) > 40:
            return jsonify({"error": "Experience level must be a short text value."}), 400
        if not isinstance(goal, str) or len(goal) > 300:
            return jsonify({"error": "Goal must be 300 characters or fewer."}), 400
        if isinstance(hours, bool) or not isinstance(hours, int) or not 1 <= hours <= 40:
            return jsonify({"error": "Learning time must be a whole number from 1 to 40 hours per week."}), 400

        profile = {
            "skills": skills, "interests": interests, "level": level.strip(),
            "goal": goal.strip(), "hours_per_week": hours,
        }
        fallback = match(profile)
        result = with_ai(profile, fallback)
        result["profile"] = profile
        return jsonify(result)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400


@app.errorhandler(413)
def too_large(_):
    return jsonify({"error": "Request too large."}), 413
