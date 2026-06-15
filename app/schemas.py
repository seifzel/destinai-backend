from pydantic import BaseModel, Field
from typing import List

# ─── REQUEST (dari Frontend ke Backend) ───────────────
class RecommendRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=200, example="tempat adem ramah anak")
    top_n: int = Field(5, ge=1, le=10)

# ─── RESPONSE (dari Backend ke Frontend) ──────────────
class DestinationResult(BaseModel):
    destinasi: str
    relevansi: float   # cosine similarity (0.0–1.0)
    sentimen: float    # rata-rata skor sentimen destinasi (0.0–1.0)
    skor: float        # skor final gabungan untuk sorting (0.0–1.0)

class RecommendResponse(BaseModel):
    query: str
    hasil: List[DestinationResult]
    total: int

class SentimentBreakdown(BaseModel):
    Positive: int
    Negative: int

class DashboardResponse(BaseModel):
    destinasi: str
    total_ulasan: int
    sentimen: SentimentBreakdown     # data untuk Pie Chart
    top_keywords: List[str]          # tombol keyword yang bisa diklik

class ReviewsResponse(BaseModel):
    destinasi: str
    keyword: str
    ulasan: List[str]
    total: int