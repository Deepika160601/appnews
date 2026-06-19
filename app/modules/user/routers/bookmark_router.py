from fastapi import (
    APIRouter,
    Depends
)

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.db import get_db

from app.core.security import (
    get_current_admin_or_user
)

from app.modules.user.schemas.bookmark_schema import (
    BookmarkCreateRequest
)

from app.modules.user.services.bookmark_service import (
    add_bookmark_service,
    get_user_bookmarks_service,
    remove_bookmark_service
)

router = APIRouter()


# =========================
# DEBUG API
# =========================
@router.get("/debug")
async def debug_bookmark(
    current_user=Depends(get_current_admin_or_user)
):
    return {
        "success": True,
        "message": "Token Verified",
        "data": current_user
    }


# =========================
# ADD BOOKMARK
# USER + ADMIN + SUPERADMIN
# =========================
@router.post("/")
async def add_user_bookmark(
    data: BookmarkCreateRequest,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_admin_or_user)
):

    return await add_bookmark_service(
        db=db,
        current_user=current_user,
        news_id=data.news_id
    )


# =========================
# GET BOOKMARKS
# USER + ADMIN + SUPERADMIN
# =========================
@router.get("/")
async def get_bookmarks(
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_admin_or_user)
):

    return await get_user_bookmarks_service(
        db=db,
        current_user=current_user
    )


# =========================
# DELETE BOOKMARK
# USER + ADMIN + SUPERADMIN
# =========================
@router.delete("/{news_id}")
async def delete_bookmark(
    news_id: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_admin_or_user)
):

    return await remove_bookmark_service(
        db=db,
        current_user=current_user,
        news_id=news_id
    )