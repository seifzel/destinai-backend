from fastapi import APIRouter, HTTPException
from app.schemas import RecommendRequest, RecommendResponse, DestinationResult
from app import ml_loader

router = APIRouter()

@router.post("/recommend", response_model=RecommendResponse)
def recommend(req: RecommendRequest):
    """Terima query vibes user, kembalikan top-N destinasi."""
    if not req.query.strip():
        raise HTTPException(status_code=400, detail="Query tidak boleh kosong.")

    results = ml_loader.get_recommendations(req.query, top_n=req.top_n)
    return RecommendResponse(
        query=req.query,
        hasil=[DestinationResult(**r) for r in results],
        total=len(results),
    )

@router.get("/destinations")
def list_destinations():
    """Daftar semua destinasi yang tersedia."""
    return {"destinations": ml_loader.list_destinations()}