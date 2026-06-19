from fastapi import (
    HTTPException,
    status
)

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.models import News

from app.utils.api_response import success_response

from app.modules.user.repositories.bookmark_repository import (
    add_bookmark,
    get_user_bookmarks,
    remove_bookmark
)

from app.modules.user.repositories.notification_repository import (
    create_notification
)


async def add_bookmark_service(
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

    bookmark = await add_bookmark(
        db=db,
        user_id=user_id,
        admin_id=admin_id,
        news_id=news_id
    )

    if bookmark == "already_bookmarked":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="News already bookmarked"
        )

    result = await db.execute(
        select(News).where(
            News.news_id == news_id
        )
    )

    news = result.scalar_one_or_none()

    if news and news.author_id:
        await create_notification(
            db=db,
            admin_id=news.author_id,
            news_id=news.news_id,
            title="New Bookmark",
            message="Someone bookmarked your news"
        )

    return success_response(
        "News bookmarked successfully",
        {
            "bookmark_id": bookmark.bookmark_id,
            "news_id": bookmark.news_id,
            "is_bookmarked": True
        }
    )


async def get_user_bookmarks_service(
    db: AsyncSession,
    current_user: dict
):

    role = current_user.get("role")

    user_id = None
    admin_id = None

    if role == "user":
        user_id = current_user.get("user_id")

    elif role in ["admin", "superadmin"]:
        admin_id = current_user.get("admin_id")

    bookmarks = await get_user_bookmarks(
        db=db,
        user_id=user_id,
        admin_id=admin_id
    )

    return success_response(
        "Bookmarks fetched successfully",
        bookmarks
    )


async def remove_bookmark_service(
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

    bookmark = await remove_bookmark(
        db=db,
        user_id=user_id,
        admin_id=admin_id,
        news_id=news_id
    )

    if not bookmark:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bookmark not found"
        )

    return success_response(
        "Bookmark removed successfully",
        {
            "news_id": news_id,
            "is_bookmarked": False
        }
    )