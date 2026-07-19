from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.routes import api_router
from app.core.config import settings
from app.core.logging import init_logging
from app.core.middleware import RequestLoggingMiddleware, SecurityLoggingMiddleware


def create_application() -> FastAPI:
    init_logging()

    print("CORS ORIGINS:", settings.cors_origins)

    app = FastAPI(
        title=settings.project_name,
        version=settings.api_version,
        openapi_url=f"{settings.api_prefix}/openapi.json",
        docs_url="/docs",
        redoc_url="/redoc",
    )

    # Middlewares
    app.add_middleware(SecurityLoggingMiddleware)
    app.add_middleware(RequestLoggingMiddleware)
    
    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(api_router, prefix=settings.api_prefix)
    return app


app = create_application()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        log_config=None,
        reload=settings.debug,
    )
