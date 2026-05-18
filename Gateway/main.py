from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.router_auth import router as auth_router
from api.router_app import router as app_router
from api.middlewares import LoggingMiddleware, RequestLoggingMiddleware
import logging
import sys

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
    ]
)
logger = logging.getLogger(__name__)


app = FastAPI()

origins = ["http://localhost:8001",
    "http://localhost:8003",
    "http://127.0.0.1:8001",
    "http://127.0.0.1:8003",]
@app.get("/")
async def root():
    return {"message": "Gateway is running", "status": "ok"}
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Список разрешённых источников
    allow_credentials=True,  # Разрешить отправку cookies и заголовков авторизации
    allow_methods=["*"],  # Разрешить все HTTP-методы (GET, POST и т. д.)
    allow_headers=["*"], # Разрешить все заголовки
    max_age=600
)
app.add_middleware(LoggingMiddleware)
app.include_router(auth_router)
app.include_router(app_router)





