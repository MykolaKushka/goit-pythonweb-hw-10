from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.middleware import SlowAPIMiddleware
from slowapi.errors import RateLimitExceeded

from app.routes import router as contacts_router
from app.routes_auth import router as auth_router, ratelimit_handler

from app.limiter_config import limiter  # якщо limiter перенесено в окремий файл

app = FastAPI()
app.state.limiter = limiter
app.add_middleware(SlowAPIMiddleware)

# ❗ Обробник перевищення ліміту
app.add_exception_handler(RateLimitExceeded, ratelimit_handler)

# CORS дозволений
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # або конкретно: ["http://localhost:3000"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Підключення маршрутів
app.include_router(auth_router)
app.include_router(contacts_router)
