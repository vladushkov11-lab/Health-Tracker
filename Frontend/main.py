from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import logging
import sys

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
    ]
)
logger = logging.getLogger(__name__)

app = FastAPI(title="Health Tracker Frontend")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Монтирование статических файлов
app.mount("/static", StaticFiles(directory="static"), name="static")

# Шаблоны
templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    """Главная страница - дашборд"""
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    """Страница входа"""
    return templates.TemplateResponse("login.html", {"request": request})


@app.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    """Страница регистрации"""
    return templates.TemplateResponse("register.html", {"request": request})


@app.get("/profile", response_class=HTMLResponse)
async def profile_page(request: Request):
    """Страница профиля"""
    return templates.TemplateResponse("profile.html", {"request": request})


@app.get("/favicon.ico")
async def favicon():
    """Заглушка для favicon"""
    from fastapi.responses import PlainTextResponse
    return PlainTextResponse(content="", status_code=204)


@app.get("/health")
async def health_check():
    """Проверка работоспособности"""
    return {"status": "ok", "service": "frontend"}

@app.get("/stats", response_class=HTMLResponse)
async def stats_page(request: Request):
    """Страница общей статистики"""
    return templates.TemplateResponse("stats.html", {"request": request})


@app.get("/stats/metric/{metric_type}", response_class=HTMLResponse)
async def stats_metric_page(request: Request, metric_type: str):
    """Страница статистики по конкретной метрике"""
    return templates.TemplateResponse("stats-metric.html", {"request": request, "metric_type": metric_type})


@app.get("/about", response_class=HTMLResponse)
async def about_page(request: Request):
    """Страница о нас"""
    return templates.TemplateResponse("about.html", {"request": request})

@app.get("/docs", response_class=HTMLResponse)
async def docs_page(request: Request):
    """Страница документации"""
    return templates.TemplateResponse("docs.html", {"request": request})

@app.get("/project", response_class=HTMLResponse)
async def project_page(request: Request):
    """Страница о проекте"""
    return templates.TemplateResponse("project.html", {"request": request})

@app.get("/favicon.ico")
async def favicon():
    from fastapi.responses import PlainTextResponse
    return PlainTextResponse(content="", status_code=204)

@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "frontend"}