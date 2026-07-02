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

    # -------------------------
    # Validate Current User
    # -------------------------
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required."
        )

    # -------------------------
    # Validate News ID
    # -------------------------
    if news_id <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid news ID."
        )

    role = current_user.get("role")

    if role not in ["user", "admin", "superadmin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Unauthorized user."
        )

    user_id = None
    admin_id = None

    if role == "user":
        user_id = current_user.get("user_id")

        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User authentication failed."
            )

    elif role in ["admin", "superadmin"]:
        admin_id = current_user.get("admin_id")

        if not admin_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Admin authentication failed."
            )

    # -------------------------
    # Check News
    # -------------------------
    result = await db.execute(
        select(News).where(
            News.news_id == news_id
        )
    )

    news = result.scalar_one_or_none()

    if not news:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="News not found."
        )

    # -------------------------
    # Like News
    # -------------------------
    like = await like_news(
        db=db,
        news_id=news_id,
        user_id=user_id,
        admin_id=admin_id
    )

    if like == "already_liked":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You have already liked this news."
        )

    # -------------------------
    # Notify News Owner
    # -------------------------
    if news.author_id:
        await create_notification(
            db=db,
            admin_id=news.author_id,
            news_id=news.news_id,
            title="New Like",
            message="Your news has received a new like."
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

    # -------------------------
    # Validate Current User
    # -------------------------
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required."
        )

    # -------------------------
    # Validate News ID
    # -------------------------
    if news_id <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid news ID."
        )

    role = current_user.get("role")

    if role not in ["user", "admin", "superadmin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Unauthorized user."
        )

    user_id = None
    admin_id = None

    if role == "user":
        user_id = current_user.get("user_id")

        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User authentication failed."
            )

    elif role in ["admin", "superadmin"]:
        admin_id = current_user.get("admin_id")

        if not admin_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Admin authentication failed."
            )

    # -------------------------
    # Unlike News
    # -------------------------
    like = await unlike_news(
        db=db,
        news_id=news_id,
        user_id=user_id,
        admin_id=admin_id
    )

    if not like:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Like not found."
        )

    # -------------------------
    # Get Updated News
    # -------------------------
    result = await db.execute(
        select(News).where(
            News.news_id == news_id
        )
    )

    news = result.scalar_one_or_none()

    if not news:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="News not found."
        )

    return success_response(
        "News unliked successfully",
        {
            "news_id": news.news_id,
            "like_count": news.like_count,
            "is_liked": False
        }
    )