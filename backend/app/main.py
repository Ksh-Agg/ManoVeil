from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.config import get_settings
from app.api.router import api_router
from app.middleware.cors import setup_cors


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    yield
    # Shutdown


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title="ManoVeil API",
        description="Universal AI/ML Mental Health Intelligence Platform",
        version="1.0.0",
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc",
    )
    setup_cors(app)
    app.include_router(api_router)

    @app.get("/health")
    async def health():
        return {"status": "healthy", "service": "manoveil-api"}

    return app


app = create_app()
