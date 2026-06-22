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

from app.modules.superadmin.analytics.superadmin_analytics_service import (
    SuperAdminAnalyticsService
)

router = APIRouter(
    dependencies=[
        Depends(
            get_current_superadmin
        )
    ]
)


# =========================
# GET ANALYTICS
# =========================
@router.get("/")
async def get_analytics(
    db: AsyncSession = Depends(
        get_db
    )
):

    return await (
        SuperAdminAnalyticsService
        .get_analytics(db)
    )