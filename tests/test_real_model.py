import sys; sys.path.insert(0, ".")
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health():
    r = client.get("/health")
    assert r.status_code == 200

def test_destinations_real():
    r = client.get("/api/v1/destinations")
    body = r.json()
    assert len(body["destinations"]) >= 1
    print("Destinasi nyata:", body["destinations"])

def test_recommend_real():
    r = client.post("/api/v1/recommend", json={"query":"tempat bagus untuk anak","top_n":3})
    assert r.status_code == 200
    body = r.json()
    assert len(body["hasil"]) > 0
    for h in body["hasil"]:
        assert 0 <= h["skor"] <= 1
        assert 0 <= h["sentimen"] <= 1
    print("Top hasil:", body["hasil"][0])

def test_dashboard_binary():
    dests = client.get("/api/v1/destinations").json()["destinations"]
    r = client.get(f"/api/v1/dashboard/{dests[0]}")
    assert r.status_code == 200
    body = r.json()
    # KRITIKAL: harus BINER, bukan 3-kelas
    assert set(body["sentimen"].keys()) == {"Positive","Negative"}
    assert body["total_ulasan"] > 0
    print(f"Dashboard '{dests[0]}':", body["sentimen"])

def test_dashboard_404():
    r = client.get("/api/v1/dashboard/Tempat Gak Ada")
    assert r.status_code == 404

def test_reviews_keyword():
    dests = client.get("/api/v1/destinations").json()["destinations"]
    dash = client.get(f"/api/v1/dashboard/{dests[0]}").json()
    kw = dash["top_keywords"][0]
    r = client.get(f"/api/v1/reviews/{dests[0]}?keyword={kw}")
    assert r.status_code == 200
    assert r.json()["total"] >= 1
    print(f"Reviews mengandung '{kw}': {r.json()['total']} ulasan")

def test_preprocessing_parity():
    from app.preprocess_clean import preprocess_text
    # Negasi WAJIB dipertahankan (jangan sampai hilang ke stopword)
    assert "tidak" in preprocess_text("tidak nyaman sekali")
    # Slang harus dinormalisasi
    out = preprocess_text("yg bgs bgt")
    assert "bgs" not in out
    print("Preprocessing parity: OK")