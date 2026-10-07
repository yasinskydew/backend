---
name: sqlalchemy-repo
description: Create SQLAlchemy 2.0 Async Repository
---

Generate an async repository class using SQLAlchemy 2.0.

Rules:
1. Inherit from a base repository if available.
2. Use `AsyncSession` for database interaction.
3. Use `select()`, `insert()`, `update()` constructs.
4. Always `await` session methods.
5. Handle `NoResultFound` exceptions.
6. Return Pydantic schemas or ORM models as specified.

Example:
class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, user_id: UUID) -> User | None:
        result = await self.session.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()