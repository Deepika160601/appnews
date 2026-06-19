from fastapi import (
    APIRouter,
    Depends
)

from pydantic import BaseModel

from sqlalchemy.ext.asyncio import (
    AsyncSession
)

from app.db.db import get_db

from app.core.security import (
    get_current_admin_or_user
)

from app.modules.user.services.notification_service import (
    get_user_notifications_service,
    update_notification_settings_service
)

router = APIRouter()


class NotificationSettingsRequest(BaseModel):
    notification_enabled: bool


# =========================
# GET MY NOTIFICATIONS
# =========================

@router.get("/")
async def get_notifications(
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_admin_or_user)
):

    return await get_user_notifications_service(
        db,
        current_user
    )


# =========================
# NOTIFICATION ON / OFF
# =========================

@router.put("/settings")
async def update_notification_settings(
    request: NotificationSettingsRequest,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_admin_or_user)
):

    return await update_notification_settings_service(
        db,
        current_user,
        request.notification_enabled
    )