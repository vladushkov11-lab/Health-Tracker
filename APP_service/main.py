from fastapi import FastAPI
from contextlib import asynccontextmanager
import logging
import sys
from api.logging_config import logger

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Application startup")
    yield
    logger.info("Application shutdown")

app = FastAPI(lifespan=lifespan)

from api.router_auth import router as router_auth
from api.router_app import router as router_app
from api.router_stats import router as router_stats
app.include_router(router_auth)
app.include_router(router_app)
app.include_router(router_stats)
