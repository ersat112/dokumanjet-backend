from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def search(q: str):
    return {"results": [f"Arama sonucu: {q}"]}