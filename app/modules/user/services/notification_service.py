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

    # -------------------------
    # Validate Current User
    # -------------------------
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required."
        )

    role = current_user.get("role")

    if role not in ["user", "admin", "superadmin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Unauthorized user."
        )

    if role == "user":

        user_id = current_user.get("user_id")

        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User authentication failed."
            )

        notifications = await get_user_notifications(
            db=db,
            user_id=user_id
        )

    else:

        admin_id = current_user.get("admin_id")

        if not admin_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Admin authentication failed."
            )

        notifications = await get_user_notifications(
            db=db,
            admin_id=admin_id
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

    # -------------------------
    # Validate Current User
    # -------------------------
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required."
        )

    role = current_user.get("role")

    if role not in ["user", "admin", "superadmin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Unauthorized user."
        )

    if role == "user":

        user_id = current_user.get("user_id")

        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User authentication failed."
            )

        user = await UserRepository.update_notification_settings(
            db,
            user_id,
            notification_enabled
        )

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found."
            )

        return success_response(
            "Notification settings updated successfully",
            {
                "notification_enabled": user.notification_enabled
            }
        )

    admin_id = current_user.get("admin_id")

    if not admin_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Admin authentication failed."
        )

    admin = await AdminRepository.get_admin_by_id(
        db,
        admin_id
    )

    if not admin:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Admin not found."
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