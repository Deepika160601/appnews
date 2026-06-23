from fastapi import (
    APIRouter,
    Depends
)

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.db import get_db

from app.core.security import (
    get_current_user
)

from app.modules.user.services.user_category_service import (
    UserCategoryService
)

router = APIRouter(
    prefix="/user/categories",
    tags=["User Categories"]
)


@router.get("")
async def get_categories(
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await UserCategoryService.get_categories(
        db
    )