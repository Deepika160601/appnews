from fastapi import (
    HTTPException,
    status
)

from sqlalchemy.ext.asyncio import (
    AsyncSession
)

from app.utils.api_response import success_response

from app.modules.user.repositories.user_repository import (
    UserRepository
)

from app.modules.admin.auth.admin_repository import (
    AdminRepository
)

from app.modules.user.repositories.notification_repository import (
    get_user_notifications
)


# =========================
# GET NOTIFICATIONS
# =========================

async def get_user_notifications_service(
    db: AsyncSession,
    current_user: dict
):

    role = current_user.get("role")

    if role == "user":

        notifications = await get_user_notifications(
            db=db,
            user_id=current_user["user_id"]
        )

    else:

        notifications = await get_user_notifications(
            db=db,
            admin_id=current_user["admin_id"]
        )

    return success_response(
        "Notifications fetched successfully",
        notifications
    )


# =========================
# UPDATE NOTIFICATION SETTINGS
# =========================

async def update_notification_settings_service(
    db: AsyncSession,
    current_user: dict,
    notification_enabled: bool
):

    role = current_user.get("role")

    if role == "user":

        user = await UserRepository.update_notification_settings(
            db,
            current_user["user_id"],
            notification_enabled
        )

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        return success_response(
            "Notification settings updated successfully",
            {
                "notification_enabled": user.notification_enabled
            }
        )

    admin = await AdminRepository.get_admin_by_id(
        db,
        current_user["admin_id"]
    )

    if not admin:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Admin not found"
        )

    admin.notification_enabled = notification_enabled

    await db.commit()
    await db.refresh(admin)

    return success_response(
        "Notification settings updated successfully",
        {
            "notification_enabled": admin.notification_enabled
        }
    )