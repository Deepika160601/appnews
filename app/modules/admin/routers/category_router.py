from fastapi import (
    APIRouter,
    Depends
)

from sqlalchemy.ext.asyncio import (
    AsyncSession
)

from app.db.db import get_db
from app.core.security import (
    get_current_admin
)

from app.modules.admin.schemas.category_schema import (
    CategoryCreateRequest
)

from app.modules.admin.services.category_service import (
    get_all_categories_service,
  
)

router = APIRouter(
    dependencies=[Depends(get_current_admin)]
)
# =========================
# GET ALL CATEGORIES
# =========================
@router.get("/")
async def list_categories(
    db: AsyncSession = Depends(get_db)
):

    return await get_all_categories_service(
        db
    )
