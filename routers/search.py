from fastapi import APIRouter, Query, HTTPException, status
from typing import List
from schemas import SearchResponse, SearchItem
import math

router = APIRouter(
    prefix="/api/v1/search",
    tags=["Search"]
)

# Örnek belge veri kümesi (ileride veritabanına bağlanabilir)
documents = [
    {"id": 1, "title": "Python ile Web Geliştirme", "content": "FastAPI ve Flask kullanarak modern web uygulamaları."},
    {"id": 2, "title": "Yapay Zeka ve Makine Öğrenmesi", "content": "Veri analizi, tahminleme ve modelleme teknikleri."},
    {"id": 3, "title": "Python ile Otomasyon", "content": "Selenium, BeautifulSoup ve RPA sistemleri."},
    {"id": 4, "title": "Veritabanı Sistemleri", "content": "SQL, PostgreSQL, MongoDB ile veri saklama yöntemleri."}
]

# BM25 formülü için IDF hesaplama fonksiyonu
def compute_idf(corpus: List[str], term: str) -> float:
    N = len(corpus)
    df = sum(1 for doc in corpus if term in doc.lower())
    return math.log((N - df + 0.5) / (df + 0.5) + 1)

# BM25 skor hesaplama fonksiyonu
def bm25_score(query: str, document: str, k: float = 1.5, b: float = 0.75) -> float:
    score = 0.0
    terms = query.lower().split()
    tokens = document.lower().split()
    doc_len = len(tokens)
    avg_len = sum(len(d['content'].split()) for d in documents) / len(documents)

    for term in terms:
        f = tokens.count(term)
        if f == 0:
            continue
        idf = compute_idf([d['content'] for d in documents], term)
        denom = f + k * (1 - b + b * (doc_len / avg_len))
        score += idf * ((f * (k + 1)) / (denom + 1e-10))
    return score

@router.get("", response_model=SearchResponse)
async def search_documents(
    query: str = Query(..., description="Aramak istediğiniz kelime")
) -> SearchResponse:
    """
    BM25 algoritmasıyla arama yapar ve SearchResponse formatında sonuç döner.
    """
    results: List[SearchItem] = []
    for doc in documents:
        score = bm25_score(query, doc['content'])
        if score > 0:
            results.append(SearchItem(
                id=doc['id'],
                title=doc['title'],
                snippet=doc['content'],
                url=None,
                score=round(score, 4)
            ))

    sorted_results = sorted(results, key=lambda x: x.score, reverse=True)
    return SearchResponse(results=sorted_results)

