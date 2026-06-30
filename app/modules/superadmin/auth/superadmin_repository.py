from sqlalchemy import (
    select,
    func
)

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.models import (
    Admin,
    News,
    User,
    AdminRequest
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
    @staticmethod
    async def get_superadmin(
    db: AsyncSession
):

     result = await db.execute(
        select(Admin).where(
            Admin.role == "superadmin"
        )
    )

     return result.scalar_one_or_none() 
        # =========================
    # GET ADMIN REQUESTS
    # =========================
    @staticmethod
    async def get_all_admin_requests(
        db: AsyncSession
    ):

        result = await db.execute(
            select(AdminRequest)
            .order_by(
                AdminRequest.created_at.desc()
            )
        )

        return result.scalars().all()


    # =========================
    # GET ADMIN REQUEST BY ID
    # =========================
    @staticmethod
    async def get_admin_request_by_id(
        db: AsyncSession,
        request_id: int
    ):

        result = await db.execute(
            select(AdminRequest).where(
                AdminRequest.request_id == request_id
            )
        )

        return result.scalar_one_or_none()


    # =========================
    # GET USER BY ID
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
    # UPDATE ADMIN REQUEST
    # =========================
    @staticmethod
    async def update_admin_request(
        db: AsyncSession,
        admin_request: AdminRequest
    ):

        await db.commit()

        await db.refresh(admin_request)

        return admin_request
    # =========================
# GET ADMIN BY USER EMAIL
# =========================
@staticmethod
async def get_admin_by_user_email(
    db: AsyncSession,
    email: str
):

    result = await db.execute(
        select(Admin).where(
            Admin.email == email
        )
    )

    return result.scalar_one_or_none()


# =========================
# SAVE CHANGES
# =========================
@staticmethod
async def save_changes(
    db: AsyncSession
):

    await db.commit()