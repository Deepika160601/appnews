from fastapi import (
    HTTPException,
    status
)

from sqlalchemy.ext.asyncio import (
    AsyncSession
)

from sqlalchemy import select

from app.models.models import News

from app.utils.api_response import success_response

from app.modules.user.repositories.like_repository import (
    like_news,
    unlike_news
)

from app.modules.user.repositories.notification_repository import (
    create_notification
)


# =========================
# LIKE NEWS
# USER + ADMIN + SUPERADMIN
# =========================
async def like_news_service(
    db: AsyncSession,
    current_user: dict,
    news_id: int
):

    role = current_user.get("role")

    user_id = None
    admin_id = None

    if role == "user":
        user_id = current_user.get("user_id")

    elif role in ["admin", "superadmin"]:
        admin_id = current_user.get("admin_id")

    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid role"
        )

    if news_id <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid news id"
        )

    result = await db.execute(
        select(News).where(
            News.news_id == news_id
        )
    )

    news = result.scalar_one_or_none()

    if not news:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="News not found"
        )

    like = await like_news(
        db=db,
        news_id=news_id,
        user_id=user_id,
        admin_id=admin_id
    )

    if like == "already_liked":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You have already liked this news"
        )

    if news.author_id:

        await create_notification(
            db=db,
            admin_id=news.author_id,
            news_id=news.news_id,
            title="New Like",
            message="Someone liked your news"
        )

    return success_response(
        "News liked successfully",
        {
            "news_id": news.news_id,
            "like_count": news.like_count,
            "is_liked": True
        }
    )


# =========================
# UNLIKE NEWS
# USER + ADMIN + SUPERADMIN
# =========================
async def unlike_news_service(
    db: AsyncSession,
    current_user: dict,
    news_id: int
):

    role = current_user.get("role")

    user_id = None
    admin_id = None

    if role == "user":
        user_id = current_user.get("user_id")

    elif role in ["admin", "superadmin"]:
        admin_id = current_user.get("admin_id")

    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid role"
        )

    like = await unlike_news(
        db=db,
        news_id=news_id,
        user_id=user_id,
        admin_id=admin_id
    )

    if not like:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Like not found"
        )

    result = await db.execute(
        select(News).where(
            News.news_id == news_id
        )
    )

    news = result.scalar_one_or_none()

    return success_response(
        "News unliked successfully",
        {
            "news_id": news_id,
            "like_count": news.like_count if news else 0,
            "is_liked": False
        }
    )