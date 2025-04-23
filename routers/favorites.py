from fastapi import APIRouter

router = APIRouter()

@router.post("/add")
async def add_favorite():
    return {"msg": "Favori eklendi"}

@router.get("/")
async def get_favorites():
    return {"favorites": ["Örnek Favori"]}