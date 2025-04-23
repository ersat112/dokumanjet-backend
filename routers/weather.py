from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def get_weather(lat: float, lon: float):
    return {"location": "Konum", "temperature": "20°C"}