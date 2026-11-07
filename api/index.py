import os, json
from flask import Flask, jsonify, request, send_from_directory
app = Flask(__name__)

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
 skills=[str(x).lower().strip() for x in profile.get("skills",[])]
 interests=[str(x).lower().strip() for x in profile.get("interests",[])]
 ranked=[]
 for c in CAREERS:
  sh=sum(any(k in s or s in k for s in skills) for k in c["skills"])
  ih=sum(any(k in s or s in k for s in interests) for k in c["interests"])
  ranked.append((min(96,35+sh*9+ih*11),c))
 ranked.sort(key=lambda x:x[0],reverse=True)
 return {"summary":"Your strongest matches are ranked from the skills and interests you entered. Treat these as starting hypotheses and validate them through projects and experience.","recommendations":[{"id":c["id"],"title":c["title"],"family":c["family"],"match":score,"roles":c["roles"],"reason":"Matched against your stated skills and interests. Use this roadmap to close relevant skill gaps.","steps":[{"title":s[0],"detail":s[1],"tag":"milestone"} for s in c["steps"]]} for score,c in ranked[:3]],"source":"rules"}

def with_ai(profile,fallback):
 key=os.getenv("OPENAI_API_KEY")
 if not key: return fallback
 try:
  from openai import OpenAI
  client=OpenAI(api_key=key)
  out=client.chat.completions.create(model=os.getenv("OPENAI_MODEL","gpt-4.1-mini"),temperature=.3,response_format={"type":"json_object"},messages=[
   {"role":"system","content":"Return JSON with summary and exactly 3 recommendations. Each recommendation must have id,title,family,match (integer 1-99),roles (2-4 strings),reason,steps (5 objects with title,detail,tag). Be practical, grounded, do not guarantee employment."},
   {"role":"user","content":json.dumps({"profile":profile,"candidate_paths":fallback["recommendations"]})}])
  data=json.loads(out.choices[0].message.content)
  if len(data.get("recommendations",[]))!=3:return fallback
  data["source"]="openai";return data
 except Exception:return fallback

@app.get("/")
def home(): return send_from_directory(os.path.dirname(__file__),"index.html")
@app.get("/api/health")
def health(): return jsonify({"status":"ok","service":"career-path-recommender"})
@app.post("/api/recommend")
def recommend():
 data=request.get_json(silent=True) or {}
 skills=data.get("skills",[]); interests=data.get("interests",[])
 if not isinstance(skills,list) or not isinstance(interests,list):return jsonify({"error":"Skills and interests must be lists."}),400
 if not skills and not interests:return jsonify({"error":"Add at least one skill or interest."}),400
 profile={"skills":skills[:20],"interests":interests[:20],"level":str(data.get("level","Beginner"))[:40],"goal":str(data.get("goal","Explore career options"))[:300],"hours_per_week":max(1,min(40,int(data.get("hours_per_week",6))))}
 fallback=match(profile);result=with_ai(profile,fallback);result["profile"]=profile
 return jsonify(result)
