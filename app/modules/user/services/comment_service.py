from fastapi import (
    HTTPException,
    status
)

from sqlalchemy.ext.asyncio import (
    AsyncSession
)

from app.utils.api_response import success_response

from app.modules.user.repositories.comment_repository import (
    add_comment,
    get_comments_by_news,
      delete_comment
)

from app.modules.admin.repositories.news_admin_repository import (
    get_news_by_id
)

from app.modules.user.repositories.notification_repository import (
    create_notification
)


# =========================
# ADD COMMENT
# USER + ADMIN + SUPERADMIN
# =========================
async def add_comment_service(
    db: AsyncSession,
    data,
    user_id: int = None,
    admin_id: int = None
):

    if not data.content.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Comment cannot be empty"
        )

    news = await get_news_by_id(
        db,
        data.news_id
    )

    if not news:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="News not found"
        )

    comment = await add_comment(
        db=db,
        data=data,
        user_id=user_id,
        admin_id=admin_id
    )

    # =========================
    # NOTIFY NEWS OWNER
    # =========================
    if hasattr(news, "author_id") and news.author_id:

        await create_notification(
            db=db,
            admin_id=news.author_id,
            news_id=news.news_id,
            title="New Comment",
            message="A new comment was added to your news"
        )

    return success_response(
        "Comment added successfully",
        {
            "comment_id": comment.comment_id,
            "news_id": comment.news_id,
            "user_id": comment.user_id,
            "admin_id": comment.admin_id,
            "content": comment.content,
            "parent_comment_id": comment.parent_comment_id,
            "created_at": comment.created_at,
            "is_commented": True
        }
    )


# =========================
# GET COMMENTS
# USER + ADMIN + SUPERADMIN
# =========================
async def get_comments_service(
    db: AsyncSession,
    news_id: int
):

    comments = await get_comments_by_news(
        db,
        news_id
    )

    if not comments:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No comments found"
        )

    return success_response(
        "Comments fetched successfully",
        comments
    )
# =========================
# DELETE COMMENT
# USER + ADMIN + SUPERADMIN
# =========================
async def delete_comment_service(
    db: AsyncSession,
    comment_id: int
):

    comment = await delete_comment(
        db,
        comment_id
    )

    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found"
        )

    return success_response(
        "Comment deleted successfully",
        {
            "comment_id": comment_id,
            "is_commented": False
        }
    )