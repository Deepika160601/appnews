from fastapi import (
    APIRouter,
    Depends
)

from sqlalchemy.ext.asyncio import (
    AsyncSession
)

from app.db.db import get_db

from app.core.security import (
    get_current_admin_or_user
)

from app.modules.user.schemas.comment_schema import (
    CommentCreateRequest
)

from app.modules.user.services.comment_service import (
    add_comment_service,
    get_comments_service,
    delete_comment_service
)

router = APIRouter()


# =========================
# ADD COMMENT
# USER + ADMIN + SUPERADMIN
# =========================
@router.post("/")
async def create_comment(
    data: CommentCreateRequest,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_admin_or_user)
):

    user_id = current_user.get("user_id")
    admin_id = current_user.get("admin_id")

    return await add_comment_service(
        db=db,
        data=data,
        user_id=user_id,
        admin_id=admin_id
    )


# =========================
# GET COMMENTS BY NEWS
# USER + ADMIN + SUPERADMIN
# =========================
@router.get("/{news_id}")
async def get_comments(
    news_id: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_admin_or_user)
):

    return await get_comments_service(
        db,
        news_id
    )


# =========================
# DELETE COMMENT
# USER + ADMIN + SUPERADMIN
# =========================
@router.delete("/{comment_id}")
async def delete_comment_api(
    comment_id: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_admin_or_user)
):

    return await delete_comment_service(
        db,
        comment_id
    )