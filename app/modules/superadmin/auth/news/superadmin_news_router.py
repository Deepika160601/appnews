from fastapi import (
    APIRouter,
    Depends
)

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.db import get_db

from app.core.security import (
    get_current_superadmin
)

from app.modules.superadmin.auth.news.superadmin_news_service import (
    SuperAdminNewsService
)

router = APIRouter()


@router.get(
    "/news",
    dependencies=[Depends(get_current_superadmin)]
)
async def get_all_news(
    db: AsyncSession = Depends(get_db),
    current_superadmin=Depends(
        get_current_superadmin
    )
):

    return await (
        SuperAdminNewsService
        .get_all_news(db)
    )
@router.delete(
    "/news/{news_id}",
    dependencies=[Depends(get_current_superadmin)]
)
async def delete_news(
    news_id: int,
    db: AsyncSession = Depends(get_db),

    current_superadmin=Depends(
        get_current_superadmin
    )
):

    return await (
        SuperAdminNewsService
        .delete_news(
            db,
            news_id
        )
    )