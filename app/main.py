from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.core.config import get_settings
from app.core.exceptions import register_exception_handlers
from app.core.lifespan import lifespan
from app.schemas.common import HealthResponse

settings = get_settings()

app = FastAPI(
    title=settings.project_name,
    version=settings.api_version,
    openapi_url=f"{settings.api_v1_prefix}/openapi.json",
    docs_url=f"{settings.api_v1_prefix}/docs",
    redoc_url=f"{settings.api_v1_prefix}/redoc",
    lifespan=lifespan,
    description=(
        "REST API for the Yee-Daa platform.\n\n"
        "Documentation is generated **code-first** from route signatures, "
        "`response_model`, Pydantic `Field`/`Query`/`Path` descriptions, and "
        "endpoint docstrings."
    ),
    openapi_tags=[
        {
            "name": "health",
            "description": "Liveness probes for orchestrators and load balancers.",
        },
        {
            "name": "categories",
            "description": "Browse active categories and nested subcategories.",
        },
        {
            "name": "recipes",
            "description": (
                "Recipe catalog: filtered listing and CRUD. "
                "Cover images reference `files` records "
                "(multipart upload or presign → PUT → confirm)."
            ),
        },
        {
            "name": "files",
            "description": (
                "Object-storage file metadata. Supports multipart upload and "
                "direct client upload via `/files/presign` + `/files/confirm`. "
                "Endpoints return metadata and public URLs, not binary streams."
            ),
        },
    ],
    debug=settings.debug,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

register_exception_handlers(app)
app.include_router(api_router, prefix=settings.api_v1_prefix)


@app.get(
    "/health",
    tags=["health"],
    response_model=HealthResponse,
    status_code=status.HTTP_200_OK,
)
async def health() -> HealthResponse:
    """Return service liveness status for orchestrators and load balancers."""
    return HealthResponse(status="ok")
