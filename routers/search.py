from fastapi import APIRouter, Query
from typing import List
from schemas import SearchResponse, SearchItem
import math

router = APIRouter(
    prefix="/api/v1/search",
    tags=["Search"]
)

# Örnek belge veri kümesi
documents = [
    {"id": 1, "title": "Python ile Web Geliştirme", "content": "FastAPI ve Flask kullanarak modern web uygulamaları."},
    # ...
]

def compute_idf(corpus: List[str], term: str) -> float:
    # …

def bm25_score(query: str, document: str, k: float = 1.5, b: float = 0.75) -> float:
    # …

@router.get("", response_model=SearchResponse)
async def search_documents(
    query: str = Query(..., description="Aramak istediğiniz kelime")
) -> SearchResponse:
    results = []
    for doc in documents:
        score = bm25_score(query, doc["content"])
        if score > 0:
            # SearchItem’in alanları: id, title, snippet (content), url, score
            results.append(SearchItem(
                id=doc["id"],
                title=doc["title"],
                snippet=doc["content"],
                url=None,
                score=round(score, 4)
            ))
    # Sıralayıp SearchResponse’a paketliyoruz
    return SearchResponse(results=sorted(results, key=lambda x: x.score, reverse=True))
