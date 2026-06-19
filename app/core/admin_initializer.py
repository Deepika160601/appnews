from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.models import Admin
from app.core.config import settings
from app.core.security import hash_password


async def create_default_superadmin(
    db: AsyncSession
):
    result = await db.execute(
        select(Admin).where(
            Admin.email ==
            settings.DEFAULT_ADMIN_EMAIL
        )
    )

    superadmin = result.scalar_one_or_none()

    if superadmin:

        if superadmin.role != "superadmin":
            superadmin.role = "superadmin"
            await db.commit()

        print("Super Admin already exists")
        return

    superadmin = Admin(
        name=settings.DEFAULT_ADMIN_NAME,
        email=settings.DEFAULT_ADMIN_EMAIL,
        password_hash=hash_password(
            settings.DEFAULT_ADMIN_PASSWORD
        ),
        role=settings.DEFAULT_ADMIN_ROLE
    )

    db.add(superadmin)

    await db.commit()

    print(
        "Default Super Admin created successfully"
    )