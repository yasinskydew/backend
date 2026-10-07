---
name: fastapi-route
description: Create FastAPI APIRouter endpoint
---

Generate a FastAPI endpoint using APIRouter.

Rules:
1. Use `APIRouter` prefix and tags.
2. Inject services via `Depends()`.
3. Define response_model and status_code.
4. Add docstrings for Swagger UI.
5. Handle exceptions gracefully.

Example:
router = APIRouter(prefix="/users", tags=["users"])

@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: UUID,
    user_service: UserService = Depends(get_user_service)
):
    """Get user by ID"""
    return await user_service.get_by_id(user_id)