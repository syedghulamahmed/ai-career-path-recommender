import api.index as service


def test_health_endpoint_reports_service():
    response = service.app.test_client().get("/api/health")
    assert response.status_code == 200
    assert response.get_json()["service"] == "career-path-recommender"


def test_recommend_requires_json_object():
    response = service.app.test_client().post("/api/recommend", data="not json")
    assert response.status_code == 400


def test_recommend_requires_skills_or_interests():
    response = service.app.test_client().post(
        "/api/recommend",
        json={"skills": [], "interests": []},
    )
    assert response.status_code == 400


def test_recommend_validates_list_items():
    response = service.app.test_client().post(
        "/api/recommend",
        json={"skills": ["Python", 123], "interests": []},
    )
    assert response.status_code == 400


def test_recommend_returns_three_known_paths_with_rules_fallback(monkeypatch):
    monkeypatch.setattr(service, "with_ai", lambda profile, fallback: fallback)
    response = service.app.test_client().post(
        "/api/recommend",
        json={
            "skills": ["Python", "statistics", "pandas"],
            "interests": ["machine learning", "data"],
            "level": "Beginner",
            "goal": "Build an AI portfolio",
            "hours_per_week": 8,
        },
    )
    payload = response.get_json()
    assert response.status_code == 200
    assert payload["source"] == "rules"
    assert len(payload["recommendations"]) == 3
    assert all(item["id"] in {"aiml", "genai", "data", "backend", "frontend", "cyber", "cloud"}
               for item in payload["recommendations"])


def test_recommend_rejects_invalid_weekly_hours():
    response = service.app.test_client().post(
        "/api/recommend",
        json={"skills": ["Python"], "interests": [], "hours_per_week": 0},
    )
    assert response.status_code == 400
