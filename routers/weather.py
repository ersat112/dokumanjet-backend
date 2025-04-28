import os
from typing import Optional
from fastapi import APIRouter, Query, HTTPException, status
import httpx
from schemas import WeatherInfo

# Router tanımı
router = APIRouter(
    prefix="/api/v1/weather",
    tags=["Weather"]
)

# OpenWeatherMap konfigürasyonu
OPENWEATHER_URL = os.getenv("OPENWEATHERMAP_URL", "https://api.openweathermap.org/data/2.5/weather")
API_KEY = os.getenv("OPENWEATHERMAP_API_KEY")

@router.get("/", response_model=WeatherInfo)
async def get_weather(
    city: str = Query(..., description="Şehir veya lokasyon adı"),
    units: Optional[str] = Query("metric", regex="^(metric|imperial)$", description="Ölçü birimi: metric veya imperial"),
    lang: Optional[str] = Query("tr", min_length=2, max_length=2, description="Dil kodu (ör: tr, en)")
) -> WeatherInfo:
    """
    Belirtilen şehir için OpenWeatherMap üzerinden hava durumu verilerini getirir.
    """
    if not API_KEY:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="OPENWEATHERMAP_API_KEY environment variable is not set"
        )

    params = {
        "q": city,
        "appid": API_KEY,
        "units": units,
        "lang": lang
    }
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(OPENWEATHER_URL, params=params)
    except httpx.RequestError as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Hava durumu servisine bağlanırken hata oluştu: {e}"
        )

    if resp.status_code != 200:
        raise HTTPException(
            status_code=resp.status_code,
            detail=f"Hava durumu alınamadı: {resp.text}"
        )

    data = resp.json()
    try:
        return WeatherInfo(
            city=data.get("name"),
            temperature=data["main"]["temp"],
            humidity=data["main"]["humidity"],
            wind_speed=data["wind"]["speed"],
            description=data["weather"][0]["description"]
        )
    except (KeyError, IndexError) as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Hava durumu verileri işlenirken hata oluştu: {e}"
        )
