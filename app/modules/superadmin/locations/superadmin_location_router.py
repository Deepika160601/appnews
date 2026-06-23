from fastapi import (
    APIRouter,
    Depends
)

from sqlalchemy.ext.asyncio import (
    AsyncSession
)

from app.db.db import (
    get_db
)

from app.core.security import (
    get_current_superadmin
)

from app.modules.superadmin.locations.superadmin_location_service import (
    SuperAdminLocationService
)

router = APIRouter(
    dependencies=[
        Depends(
            get_current_superadmin
        )
    ]
)


# =========================
# GET LOCATION ANALYTICS
# =========================
@router.get("/")
async def get_location_analytics(
    db: AsyncSession = Depends(
        get_db
    )
):

    return await (
        SuperAdminLocationService
        .get_location_analytics(db)
    )