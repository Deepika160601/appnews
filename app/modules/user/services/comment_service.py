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

    # -------------------------
    # Validate News ID
    # -------------------------
    if data.news_id <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid news ID."
        )

    # -------------------------
    # Validate Comment
    # -------------------------
    if not data.content or not data.content.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Comment cannot be empty."
        )

    data.content = data.content.strip()

    if len(data.content) > 1000:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Comment must not exceed 1000 characters."
        )

    # -------------------------
    # Validate Parent Comment
    # -------------------------
    if (
        hasattr(data, "parent_comment_id")
        and data.parent_comment_id is not None
        and data.parent_comment_id <= 0
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid parent comment ID."
        )

    # -------------------------
    # Validate User/Admin
    # -------------------------
    if user_id is None and admin_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required."
        )

    # -------------------------
    # Check News
    # -------------------------
    news = await get_news_by_id(
        db,
        data.news_id
    )

    if not news:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="News not found."
        )

    # -------------------------
    # Add Comment
    # -------------------------
    comment = await add_comment(
        db=db,
        data=data,
        user_id=user_id,
        admin_id=admin_id
    )

    # -------------------------
    # Notify News Owner
    # -------------------------
    if news.author_id:
        await create_notification(
            db=db,
            admin_id=news.author_id,
            news_id=news.news_id,
            title="New Comment",
            message="Your news has received a new comment."
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

    # -------------------------
    # Validate News ID
    # -------------------------
    if news_id <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid news ID."
        )

    # -------------------------
    # Check News
    # -------------------------
    news = await get_news_by_id(
        db,
        news_id
    )

    if not news:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="News not found."
        )

    # -------------------------
    # Get Comments
    # -------------------------
    comments = await get_comments_by_news(
        db,
        news_id
    )

    return success_response(
        "Comments fetched successfully"
        if comments else
        "No comments found.",
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

    # -------------------------
    # Validate Comment ID
    # -------------------------
    if comment_id <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid comment ID."
        )

    # -------------------------
    # Delete Comment
    # -------------------------
    comment = await delete_comment(
        db,
        comment_id
    )

    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found."
        )

    return success_response(
        "Comment deleted successfully",
        {
            "comment_id": comment_id,
            "is_commented": False
        }
    )