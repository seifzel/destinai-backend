from fastapi import APIRouter, HTTPException, Query
from app.schemas import DashboardResponse, ReviewsResponse
from app import ml_loader

router = APIRouter()

@router.get("/dashboard/{destinasi}", response_model=DashboardResponse)
def get_dashboard(destinasi: str):
    """Data pie chart + keywords untuk satu destinasi."""
    data = ml_loader.get_dashboard(destinasi)
    if not data:
        raise HTTPException(status_code=404, detail=f"Destinasi '{destinasi}' tidak ditemukan.")
    return DashboardResponse(**data)

@router.get("/reviews/{destinasi}", response_model=ReviewsResponse)
def get_reviews_by_keyword(
    destinasi: str,
    keyword: str = Query(..., min_length=1, description="Keyword yang diklik user di dashboard")
):
    """Ulasan yang mengandung keyword tertentu (untuk halaman detail)."""
    ulasan = ml_loader.get_reviews_by_keyword(destinasi, keyword)
    return ReviewsResponse(
        destinasi=destinasi,
        keyword=keyword,
        ulasan=ulasan,
        total=len(ulasan)
    )