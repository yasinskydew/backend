---
name: pydantic-schema
description: Generate Pydantic V2 schemas for FastAPI
---

Generate Pydantic V2 models for request/response.

Rules:
1. Use `BaseModel` from `pydantic`.
2. Use `Field` for validation constraints (min_length, gt, etc.).
3. Separate `Create`, `Update`, and `Response` schemas.
4. Do not include sensitive fields (password) in Response schemas.
5. Use `Optional` for update fields.

Example:
class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)

class UserResponse(BaseModel):
    id: UUID
    email: EmailStr
    is_active: bool
    
    class Config:
        from_attributes = True