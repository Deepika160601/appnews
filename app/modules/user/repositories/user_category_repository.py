from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.models import Category


class UserCategoryRepository:

    @staticmethod
    async def get_categories(
        db: AsyncSession
    ):
        result = await db.execute(
            select(Category)
        )

        return result.scalars().all()