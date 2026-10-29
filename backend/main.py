from __future__ import annotations

import logging
import os
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes import router
from services.recommender import warm_up_models


def get_cors_origins() -> list[str]:
    configured = os.getenv("BACKEND_CORS_ORIGINS", "")
    if configured:
        # Browsers send the origin without a trailing slash, so "https://x.vercel.app/" would never match.
        return [origin.strip().rstrip("/") for origin in configured.split(",") if origin.strip()]
    return ["http://localhost:5173", "http://127.0.0.1:5173"]


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    # Uvicorn only starts accepting requests after this runs, so a server waking from sleep
    # reports healthy only once the models are in memory and the first resume is fast.
    logging.getLogger("uvicorn.error").info("Models: %s", warm_up_models())
    yield


app = FastAPI(
    title="AI Resume Screening API",
    description="FastAPI backend for resume ranking, skill analysis, evaluation, and model training.",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=get_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)


@app.get("/")
def root() -> dict[str, str]:
    return {
        "status": "ok",
        "service": "resume-screening-api",
        "health": "/health",
        "docs": "/docs",
    }


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}
