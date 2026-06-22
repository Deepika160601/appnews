from sqlalchemy.ext.asyncio import AsyncSession

from app.models.models import NewsView


# =========================
# CREATE NEWS VIEW
# =========================
async def create_news_view(
    db: AsyncSession,
    user_id: int,
    news_id: int
):

    news_view = NewsView(
        user_id=user_id,
        news_id=news_id
    )

    db.add(news_view)

    await db.commit()

    await db.refresh(news_view)

    return news_view