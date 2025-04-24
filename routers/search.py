from fastapi import APIRouter, Query
from typing import List
from schemas import SearchResult
import math

router = APIRouter()

documents = [
{"id": 1, "title": "Python Web", "content": "FastAPI ve Flask modern web için kullanılır."},
{"id": 2, "title": "Makine Öğrenimi", "content": "Veri analizi ve yapay zeka teknikleri."},
{"id": 3, "title": "PostgreSQL", "content": "Veritabanı sorguları ve bağlantılar."}
]

def compute_idf(corpus, term):
N = len(corpus)
df = sum(1 for doc in corpus if term in doc.lower())
return math.log((N - df + 0.5) / (df + 0.5) + 1)

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

@router.get("/", response_model=List[SearchResult])
def search_documents(q: str = Query(...)):
results = []
for doc in documents:
score = bm25_score(q, doc["content"])
if score > 0:
results.append({**doc, "score": round(score, 4)})
return sorted(results, key=lambda x: x["score"], reverse=True)
