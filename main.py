import json
import os
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
import redis
import requests
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

app = FastAPI(
    title="Weather API",
    description="A simple API for retrieving current weather information",
    version="1.0.0",
)

# Configuración de la API Key de OpenWeatherMap 
OPENWEATHER_API_KEY = "YOUR_API_KEY"
# Configuración de la URL base de la API de OpenWeatherMap
OPENWEATHER_URL = "https://api.openweathermap.org/data/2.5/weather"
#configuración de redis
redis_client = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)
CACHE_EXPIRATION = 21600  # 6 horas de expiracion

#slowapi
limiter = Limiter(key_func=get_remote_address)

#middleware de slowapi
app.state.limiter = limiter
app.add_middleware(SlowAPIMiddleware)

#manejamos la exepcion del rate limit
@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=429,
        content={"message": "Has alcanzado el límite de solicitudes. Inténtalo de nuevo más tarde."}
    )


@app.get("/", tags=["root"])
def home():
    return {"message": "Welcome to the Weather API"}


@app.get("/weather/{city}", status_code=200, response_model=dict)
@limiter.limit("3/minute")
async def get_weather(city: str, request: Request) -> str:
    
    # Verificamos si el clima para la ciudad está en cache
    cached_weather = redis_client.get(city.lower())

    # Si el clima está en cache, lo retornamos
    if cached_weather: 
        return json.loads(cached_weather)

    # Creamos los parametros que tendra la peticion a la api
    param = {
        "q": city,
        "appid": OPENWEATHER_API_KEY,
        "units": "imperial"
    }

    # Realizamos la peticion a la API y obtenemos el clima
    response = requests.get(OPENWEATHER_URL, params=param)

    #manejamos las exepeciones
    if response.status_code == 404:
        raise HTTPException(status_code=404, detail="City code invalid")
    elif response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="Error fetchind data")

    # Obtenemos los datos de la respuesta
    weather_data = response.json()

    # Guardamos el clima en cache para evitar hacer la peticion a la API cada vez que se consulta la información
    redis_client.setex(city.lower(), CACHE_EXPIRATION, json.dumps(weather_data))

    return weather_data



