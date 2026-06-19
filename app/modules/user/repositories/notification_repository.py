from sqlalchemy import (
    select,
    or_
)

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.models import Notification


# =========================
# CREATE NOTIFICATION
# =========================

async def create_notification(
    db: AsyncSession,
    news_id: int,
    title: str,
    message: str,
    user_id: int = None,
    admin_id: int = None
):

    notification = Notification(
        user_id=user_id,
        admin_id=admin_id,
        news_id=news_id,
        title=title,
        message=message,
        type="news",
        target_type="all"
    )

    db.add(notification)

    await db.commit()
    await db.refresh(notification)

    return notification


# =========================
# GET NOTIFICATIONS
# =========================

async def get_user_notifications(
    db: AsyncSession,
    user_id: int = None,
    admin_id: int = None
):

    result = await db.execute(
        select(Notification)
        .where(
            or_(
                Notification.user_id == user_id,
                Notification.admin_id == admin_id
            )
        )
        .order_by(
            Notification.created_at.desc()
        )
    )

    notifications = result.scalars().all()

    return [
        {
            "notification_id": notification.notification_id,
            "news_id": notification.news_id,
            "title": notification.title,
            "message": notification.message,
            "is_read": notification.is_read,
            "created_at": notification.created_at
        }
        for notification in notifications
    ]


# =========================
# GET NOTIFICATION BY ID
# =========================

async def get_notification_by_id(
    db: AsyncSession,
    notification_id: int
):

    result = await db.execute(
        select(Notification).where(
            Notification.notification_id == notification_id
        )
    )

    return result.scalar_one_or_none()


# =========================
# MARK AS READ
# =========================

async def mark_as_read(
    db: AsyncSession,
    notification: Notification
):

    notification.is_read = True

    await db.commit()
    await db.refresh(notification)

    return notification


# =========================
# GET UNREAD NOTIFICATIONS
# =========================

async def get_unread_notifications(
    db: AsyncSession,
    user_id: int = None,
    admin_id: int = None
):

    result = await db.execute(
        select(Notification)
        .where(
            Notification.is_read == False,
            or_(
                Notification.user_id == user_id,
                Notification.admin_id == admin_id
            )
        )
        .order_by(
            Notification.created_at.desc()
        )
    )

    return result.scalars().all()


# =========================
# DELETE NOTIFICATION
# =========================

async def delete_notification(
    db: AsyncSession,
    notification: Notification
):

    await db.delete(notification)

    await db.commit()

    return True