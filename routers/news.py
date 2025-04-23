from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def get_news():
    return {"news": ["Manşet 1", "Manşet 2"]}