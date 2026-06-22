from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.models import (
    News,
    Admin,
    Category
)


class SuperAdminNewsRepository:

    @staticmethod
    async def get_all_news(
        db: AsyncSession
    ):

        result = await db.execute(
            select(News)
            .options(
                selectinload(News.author),
                selectinload(News.category)
            )
            .order_by(
                News.created_at.desc()
            )
        )

        return result.scalars().all()
    @staticmethod
    async def get_news_by_id(
        db: AsyncSession,
        news_id: int
    ):

        result = await db.execute(
            select(News).where(
                News.news_id == news_id
            )
        )

        return result.scalar_one_or_none()

    @staticmethod
    async def delete_news(
        db: AsyncSession,
        news: News
    ):

        await db.delete(news)

        await db.commit()