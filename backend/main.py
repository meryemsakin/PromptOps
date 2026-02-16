"""PromptOps — LLM Observability & Optimization Platform."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.database import init_db
from backend.routers import projects, ingest, analytics


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize database on startup."""
    await init_db()
    yield


app = FastAPI(
    title="PromptOps",
    description="LLM Observability & Optimization Platform — Track costs, monitor performance, optimize prompts.",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS — allow dashboard to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(projects.router)
app.include_router(ingest.router)
app.include_router(analytics.router)


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "promptops-api", "version": "0.1.0"}
