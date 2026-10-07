from fastapi import APIRouter

from app.api.v1.endpoints import categories, files, recipes

api_router = APIRouter()
api_router.include_router(categories.router)
api_router.include_router(files.router)
api_router.include_router(recipes.router)
