from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.models import Comment,News


# =========================
# ADD COMMENT
# =========================
async def add_comment(
    db: AsyncSession,
    data,
    user_id: int = None,
    admin_id: int = None
):

    comment = Comment(
        user_id=user_id,
        admin_id=admin_id,
        news_id=data.news_id,
        content=data.content,
        parent_comment_id=data.parent_comment_id
    )

    db.add(comment)

    await db.commit()

    await db.refresh(comment)

    return comment


# =========================
# GET COMMENTS BY NEWS
# =========================
async def get_comments_by_news(
    db: AsyncSession,
    news_id: int
):

    result = await db.execute(
        select(Comment)
        .options(
            selectinload(Comment.user),
            selectinload(Comment.admin)
        )
        .where(
            Comment.news_id == news_id
        )
        .order_by(
            Comment.created_at.desc()
        )
    )

    comments = result.scalars().all()

    return [
        {
            "comment_id": comment.comment_id,

            "user_id": comment.user_id,
            "admin_id": comment.admin_id,

            "commented_by":
                comment.user.name if comment.user
                else comment.admin.name if comment.admin
                else None,

            "commented_by_type":
                "user" if comment.user
                else "admin" if comment.admin
                else None,

            "news_id": comment.news_id,
            "content": comment.content,
            "parent_comment_id": comment.parent_comment_id,
            "created_at": comment.created_at
        }
        for comment in comments
    ]

# =========================
# DELETE COMMENT
# =========================
async def delete_comment(
    db,
    comment_id: int
):

    result = await db.execute(
        select(Comment).where(
            Comment.comment_id == comment_id
        )
    )

    comment = result.scalar_one_or_none()

    if not comment:
        return None

    result = await db.execute(
        select(News).where(
            News.news_id == comment.news_id
        )
    )

    news = result.scalar_one_or_none()

    if news and news.comment_count > 0:
        news.comment_count -= 1

    await db.delete(comment)
    await db.commit()

    return comment