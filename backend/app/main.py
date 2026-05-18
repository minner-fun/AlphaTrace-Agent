from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import agent, jobs, reports
from app.config import get_settings
from app.database import Base, engine


def create_app() -> FastAPI:
    settings = get_settings()
    Base.metadata.create_all(bind=engine)

    app = FastAPI(
        title="AlphaTrace Agent API",
        description="Market intelligence agent backend for Arc ERC-8004 and ERC-8183 jobs.",
        version="0.1.0",
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(jobs.router)
    app.include_router(reports.router)
    app.include_router(agent.router)

    @app.get("/health")
    def health():
        return {"status": "ok", "service": "alphatrace-agent"}

    return app


app = create_app()

