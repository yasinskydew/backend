from fastapi import APIRouter

from app.api.v1.endpoints import categories, files

api_router = APIRouter()
api_router.include_router(categories.router)
api_router.include_router(files.router)
