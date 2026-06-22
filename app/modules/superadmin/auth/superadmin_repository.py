from sqlalchemy import (
    select,
    func
)

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.models import (
    Admin,
    News
)


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

        admins = result.scalars().all()

        admin_list = []

        for admin in admins:

            published_result = await db.execute(
                select(func.count(News.news_id)).where(
                    News.author_id == admin.admin_id,
                    News.status == "published"
                )
            )

            draft_result = await db.execute(
                select(func.count(News.news_id)).where(
                    News.author_id == admin.admin_id,
                    News.status == "draft"
                )
            )

            breaking_result = await db.execute(
                select(func.count(News.news_id)).where(
                    News.author_id == admin.admin_id,
                    News.is_breaking == True
                )
            )

            avg_views_result = await db.execute(
                select(func.avg(News.view_count)).where(
                    News.author_id == admin.admin_id
                )
            )

            avg_views = avg_views_result.scalar()

            admin_list.append(
                {
                    "admin_id": admin.admin_id,
                    "name": admin.name,
                    "email": admin.email,
                    "address": admin.address,
                    "aadhaar_file": admin.aadhaar_file,
                    "published": published_result.scalar() or 0,
                    "rejected": 0,
                    "drafts": draft_result.scalar() or 0,
                    "breaking": breaking_result.scalar() or 0,
                    "avg_views": round(avg_views) if avg_views else 0
                }
            )

        return admin_list