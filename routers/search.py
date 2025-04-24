from fastapi import APIRouter, Query
from typing import List
from schemas import SearchResult
import math

router = APIRouter()

# Örnek belge veri kümesi (daha sonra veritabanına bağlanabilir)
documents = [
    {"id": 1, "title": "Python ile Web Geliştirme", "content": "FastAPI ve Flask kullanarak modern web uygulamaları."},
    {"id": 2, "title": "Yapay Zeka ve Makine Öğrenmesi", "content": "Veri analizi, tahminleme ve modelleme teknikleri."},
    {"id": 3, "title": "Python ile Otomasyon", "content": "Selenium, BeautifulSoup ve RPA sistemleri."},
    {"id": 4, "title": "Veritabanı Sistemleri", "content": "SQL, PostgreSQL, MongoDB ile veri saklama yöntemleri."}
]

# BM25 formülü için gerekli IDF fonksiyonu
def compute_idf(corpus, term):
    N = len(corpus)
    df = sum(1 for doc in corpus if term in doc.lower())
    return math.log((N - df + 0.5) / (df + 0.5) + 1)

# BM25 skor hesaplama
def bm25_score(query, document, k=1.5, b=0.75):
    score = 0.0
    doc_len = len(document.split())
    avg_len = sum(len(d['content'].split()) for d in documents) / len(documents)

    for term in query.lower().split():
        f = document.lower().split().count(term)
        idf = compute_idf([d["content"] for d in documents], term)
        denom = f + k * (1 - b + b * (doc_len / avg_len))
        score += idf * ((f * (k + 1)) / (denom + 1e-10))
    return score

# === Arama endpoint'i ===
@router.get("/", response_model=List[SearchResult])
def search_documents(q: str = Query(..., description="Aramak istediğiniz kelime")):
    results = []
    for doc in documents:
        score = bm25_score(q, doc["content"])
        if score > 0:
            results.append({**doc, "score": round(score, 4)})

    return sorted(results, key=lambda x: x["score"], reverse=True)
