import sys; sys.path.insert(0, ".")
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"

def test_recommend_valid():
    r = client.post("/api/v1/recommend", json={"query": "tempat adem ramah anak", "top_n": 3})
    assert r.status_code == 200
    body = r.json()
    assert body["query"] == "tempat adem ramah anak"
    assert len(body["hasil"]) <= 3
    assert "destinasi" in body["hasil"][0]
    assert "skor" in body["hasil"][0]

def test_recommend_empty_query():
    r = client.post("/api/v1/recommend", json={"query": "   ", "top_n": 3})
    assert r.status_code == 400

def test_recommend_top_n_limit():
    r = client.post("/api/v1/recommend", json={"query": "bagus", "top_n": 99})
    assert r.status_code == 422  # validasi Pydantic

def test_dashboard_found():
    r = client.get("/api/v1/dashboard/Taman Bungkul")
    assert r.status_code == 200
    body = r.json()
    assert "sentimen" in body
    assert "top_keywords" in body
    assert "total_ulasan" in body

def test_dashboard_not_found():
    r = client.get("/api/v1/dashboard/Tempat Tidak Ada")
    assert r.status_code == 404

def test_reviews_by_keyword():
    r = client.get("/api/v1/reviews/Taman Bungkul?keyword=adem")
    assert r.status_code == 200
    body = r.json()
    assert body["keyword"] == "adem"
    assert isinstance(body["ulasan"], list)

def test_list_destinations():
    r = client.get("/api/v1/destinations")
    assert r.status_code == 200
    assert len(r.json()["destinations"]) > 0