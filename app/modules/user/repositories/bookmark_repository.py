from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.models import (
    Bookmark,
    News
)


# =========================
# ADD BOOKMARK
# =========================
async def add_bookmark(
    db: AsyncSession,
    user_id: int = None,
    admin_id: int = None,
    news_id: int = None
):

    query = select(Bookmark).where(
        Bookmark.news_id == news_id
    )

    if user_id:
        query = query.where(
            Bookmark.user_id == user_id
        )

    elif admin_id:
        query = query.where(
            Bookmark.admin_id == admin_id
        )

    result = await db.execute(query)

    existing = result.scalar_one_or_none()

    if existing:
        return "already_bookmarked"

    bookmark = Bookmark(
        user_id=user_id,
        admin_id=admin_id,
        news_id=news_id
    )

    db.add(bookmark)

    await db.commit()

    await db.refresh(bookmark)

    return bookmark


# =========================
# GET USER/ADMIN BOOKMARKS
# =========================
async def get_user_bookmarks(
    db: AsyncSession,
    user_id: int = None,
    admin_id: int = None
):

    query = (
        select(
            Bookmark.bookmark_id,
            Bookmark.news_id,
            Bookmark.created_at,
            News.title,
            News.summary,
            News.thumbnail_url
        )
        .join(
            News,
            Bookmark.news_id == News.news_id
        )
    )

    if user_id:
        query = query.where(
            Bookmark.user_id == user_id
        )

    elif admin_id:
        query = query.where(
            Bookmark.admin_id == admin_id
        )

    result = await db.execute(query)

    rows = result.all()

    return [
        {
            "bookmark_id": row.bookmark_id,
            "news_id": row.news_id,
            "title": row.title,
            "summary": row.summary,
            "thumbnail_url": row.thumbnail_url,
            "created_at": row.created_at
        }
        for row in rows
    ]


# =========================
# REMOVE BOOKMARK
# =========================
async def remove_bookmark(
    db: AsyncSession,
    user_id: int = None,
    admin_id: int = None,
    news_id: int = None
):

    query = select(Bookmark).where(
        Bookmark.news_id == news_id
    )

    if user_id:
        query = query.where(
            Bookmark.user_id == user_id
        )

    elif admin_id:
        query = query.where(
            Bookmark.admin_id == admin_id
        )

    result = await db.execute(query)

    bookmark = result.scalar_one_or_none()

    if not bookmark:
        return None

    await db.delete(bookmark)

    await db.commit()

    return bookmark