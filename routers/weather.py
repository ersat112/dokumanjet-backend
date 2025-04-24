from fastapi import APIRouter, Query, HTTPException
from schemas import WeatherResponse
import requests
import os

router = APIRouter()

@router.get("/", response_model=WeatherResponse)
def get_weather(city: str = Query(..., description="Şehir adı")):
    api_key = os.getenv("OPENWEATHERMAP_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="OPENWEATHERMAP_API_KEY tanımlı değil.")

    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric&lang=tr"
    response = requests.get(url)

    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="Hava durumu alınamadı.")

    data = response.json()

    return WeatherResponse(
        city=data["name"],
        temperature=data["main"]["temp"],
        humidity=data["main"]["humidity"],
        wind_speed=data["wind"]["speed"],
        description=data["weather"][0]["description"]
    )
