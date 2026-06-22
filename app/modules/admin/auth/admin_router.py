from fastapi import (
    APIRouter,
    Depends
)

from sqlalchemy.ext.asyncio import (
    AsyncSession
)

from app.db.db import get_db

from app.core.security import (
    get_current_admin
)

from app.modules.admin.auth.admin_schema import (
    AdminLoginRequest
)

from app.modules.admin.auth.admin_service import (
    AdminService
)

router = APIRouter()


# =========================
# ADMIN LOGIN
# PUBLIC API
# =========================
@router.post("/login")
async def login_admin(
    request: AdminLoginRequest,
    db: AsyncSession = Depends(get_db)
):

    return await AdminService.login_admin(
        db,
        request.email,
        request.password
    )


# =========================
# ADMIN PROFILE
# ADMIN ONLY 🔒
# =========================
@router.get(
    "/profile",
    dependencies=[Depends(get_current_admin)]
)
async def get_admin_profile(
    db: AsyncSession = Depends(get_db),
    current_admin=Depends(get_current_admin)
):

    return await AdminService.get_profile(
        db,
        current_admin["admin_id"]
    )