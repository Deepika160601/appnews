from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.models import Admin


class SuperAdminRepository:

    @staticmethod
    async def get_admin_by_email(
        db: AsyncSession,
        email: str
    ):

        result = await db.execute(
            select(Admin).where(
                Admin.email == email
            )
        )

        return result.scalar_one_or_none()

    @staticmethod
    async def create_admin(
        db: AsyncSession,
        admin: Admin
    ):

        db.add(admin)

        await db.commit()

        await db.refresh(admin)

        return admin

    @staticmethod
    async def get_all_admins(
        db: AsyncSession
    ):

        result = await db.execute(
            select(Admin).where(
                Admin.role == "admin"
            )
        )

        return result.scalars().all()