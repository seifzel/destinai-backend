"""ml_loader.py — REAL MODE (artefak dari notebook Achmad)."""
import os, re, logging
import numpy as np
import pandas as pd
import joblib
from sklearn.metrics.pairwise import cosine_similarity

# ⬇️ Import dari modul Bani (satu sumber kebenaran untuk preprocessing)
from app.preprocess_clean import preprocess_text

logger = logging.getLogger(__name__)

_MODELS_DIR = os.path.join(os.path.dirname(__file__), "..", "models")
_sent  = joblib.load(os.path.join(_MODELS_DIR, "sentiment_model.joblib"))
_rec   = joblib.load(os.path.join(_MODELS_DIR, "recommender.joblib"))
_df    = pd.read_csv(os.path.join(_MODELS_DIR, "clean_dataset_final.csv"))

_sent_vec   = _sent["vectorizer"]
_sent_model = _sent["model"]
_rec_vec    = _rec["rec_vectorizer"]
_prof_mat   = _rec["profile_matrix"]
_profiles   = _rec["profiles"]
_feat_names = _rec["feature_names"]

logger.info(f"✓ Model termuat. Kelas: {list(_sent_model.classes_)}")
logger.info(f"✓ Total destinasi: {len(_profiles)} | total ulasan: {len(_df)}")


def get_recommendations(query: str, top_n: int = 5, alpha: float = 0.7):
    cleaned = preprocess_text(query)
    qv = _rec_vec.transform([cleaned])
    sims = cosine_similarity(qv, _prof_mat)[0]
    rng = sims.max() - sims.min()
    sim_norm = (sims - sims.min()) / (rng + 1e-9)
    final = alpha * sim_norm + (1 - alpha) * _profiles["sent_score"].values
    out = (_profiles
           .assign(relevansi=sims.round(4),
                   sentimen=_profiles["sent_score"].round(4),
                   skor=final.round(4))
           .sort_values("skor", ascending=False)
           .head(top_n)
           [["destinasi","relevansi","sentimen","skor"]]
           .reset_index(drop=True))
    return out.to_dict(orient="records")


def get_dashboard(destinasi: str):
    sub = _df[_df["destinasi"] == destinasi]
    if sub.empty:
        return None
    breakdown = sub["sentiment"].value_counts().to_dict()
    # Pastikan 2 kelas selalu ada (defensive, walau bin_df sudah biner)
    for k in ["Positive", "Negative"]:
        breakdown.setdefault(k, 0)
    idx = _profiles.index[_profiles["destinasi"] == destinasi]
    kws = []
    if len(idx):
        row = _prof_mat[idx[0]].toarray()[0]
        top = row.argsort()[::-1][:8]
        kws = [_feat_names[i] for i in top if row[i] > 0]
    return {
        "destinasi": destinasi,
        "total_ulasan": int(len(sub)),
        "sentimen": {k: int(breakdown[k]) for k in ["Positive","Negative"]},
        "top_keywords": list(kws),
    }


def get_reviews_by_keyword(destinasi: str, keyword: str):
    sub = _df[_df["destinasi"] == destinasi]
    mask = sub["text_cleaned"].str.contains(
        rf"\b{re.escape(keyword.lower())}\b", regex=True, na=False)
    return sub[mask]["review"].tolist()


def list_destinations():
    return sorted(_df["destinasi"].unique().tolist())


def predict_sentiment(text: str):
    """Prediksi sentimen untuk teks bebas. Bonus endpoint untuk frontend."""
    cleaned = preprocess_text(text)
    vec = _sent_vec.transform([cleaned])
    label = _sent_model.predict(vec)[0]
    prob = _sent_model.predict_proba(vec)[0]
    return {
        "label": str(label),
        "confidence": float(prob.max()),
        "classes": list(_sent_model.classes_)
    }