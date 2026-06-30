from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.models import User
from app.models.models import AdminRequest

class UserRepository:

    # =========================
    # GET BY EMAIL
    # =========================
    @staticmethod
    async def get_user_by_email(
        db: AsyncSession,
        email: str
    ):

        result = await db.execute(
            select(User).where(
                User.email == email
            )
        )

        return result.scalar_one_or_none()

    # =========================
    # GET BY MOBILE NUMBER
    # =========================
    @staticmethod
    async def get_user_by_mobile_number(
        db: AsyncSession,
        mobile_number: str
    ):

        result = await db.execute(
            select(User).where(
                User.mobile_number == mobile_number
            )
        )

        return result.scalar_one_or_none()

    # =========================
    # GET BY ID
    # =========================
    @staticmethod
    async def get_user_by_id(
        db: AsyncSession,
        user_id: int
    ):

        result = await db.execute(
            select(User).where(
                User.user_id == user_id
            )
        )

        return result.scalar_one_or_none()

    # =========================
    # CREATE USER
    # =========================
    @staticmethod
    async def create_user(
        db: AsyncSession,
        user: User
    ):

        db.add(user)

        await db.commit()

        await db.refresh(user)

        return user

    # =========================
    # UPDATE LANGUAGE
    # =========================
    @staticmethod
    async def update_user_language(
        db: AsyncSession,
        user_id: int,
        preferred_language: str
    ):

        result = await db.execute(
            select(User).where(
                User.user_id == user_id
            )
        )

        user = result.scalar_one_or_none()

        if not user:
            return None

        user.preferred_language = preferred_language

        await db.commit()

        await db.refresh(user)

        return user

    # =========================
    # GET ALL USERS
    # =========================
    @staticmethod
    async def get_all_users(
        db: AsyncSession
    ):

        result = await db.execute(
            select(User)
        )

        return result.scalars().all()

    # =========================
    # GET PROFILE
    # =========================
    @staticmethod
    async def get_profile(
        db: AsyncSession,
        user_id: int
    ):

        result = await db.execute(
            select(User).where(
                User.user_id == user_id
            )
        )

        return result.scalar_one_or_none()

    # =========================
    # UPDATE NOTIFICATION SETTINGS
    # =========================
    @staticmethod
    async def update_notification_settings(
        db: AsyncSession,
        user_id: int,
        notification_enabled: bool
    ):

        result = await db.execute(
            select(User).where(
                User.user_id == user_id
            )
        )

        user = result.scalar_one_or_none()

        if not user:
            return None

        user.notification_enabled = notification_enabled

        await db.commit()

        await db.refresh(user)

        return user
        # =========================
    # GET PENDING ADMIN REQUEST
    # =========================
    @staticmethod
    async def get_pending_admin_request(
        db: AsyncSession,
        user_id: int
    ):

        result = await db.execute(
            select(AdminRequest).where(
                AdminRequest.user_id == user_id,
                AdminRequest.status == "Pending"
            )
        )

        return result.scalar_one_or_none()


    # =========================
    # CREATE ADMIN REQUEST
    # =========================
    @staticmethod
    async def create_admin_request(
        db: AsyncSession,
        admin_request: AdminRequest
    ):

        db.add(admin_request)

        await db.commit()

        await db.refresh(admin_request)

        return admin_request


    # =========================
    # GET ADMIN REQUEST BY USER
    # =========================
    @staticmethod
    async def get_admin_request_by_user(
        db: AsyncSession,
        user_id: int
    ):

        result = await db.execute(
            select(AdminRequest).where(
                AdminRequest.user_id == user_id
            )
        )

        return result.scalar_one_or_none()