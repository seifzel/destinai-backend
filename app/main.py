from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import recommend, dashboard

app = FastAPI(
    title="DestinAI API",
    description="Backend mesin sentimen + rekomendasi DestinAI",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # ganti ke URL Vercel saat production
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(recommend.router, prefix="/api/v1", tags=["Rekomendasi"])
app.include_router(dashboard.router, prefix="/api/v1", tags=["Dashboard"])

@app.get("/health")
def health_check():
    return {"status": "ok", "version": "1.0.0"}