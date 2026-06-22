from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.models import Category

# =========================
# GET ALL CATEGORIES
# =========================
async def get_all_categories(
    db: AsyncSession
):

    result = await db.execute(
        select(Category)
    )

    return result.scalars().all()
