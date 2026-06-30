from fastapi import (
    APIRouter,
    Depends,
    Form,
    File,
    UploadFile
)

from sqlalchemy.ext.asyncio import AsyncSession
from app.modules.superadmin.auth.superadmin_schema import (
    AdminRequestActionRequest
)

from app.db.db import get_db

from app.core.security import (
    get_current_superadmin
)

from app.modules.superadmin.auth.superadmin_service import (
    SuperAdminService
)

router = APIRouter()


# =========================
# SUPER ADMIN LOGIN
# PUBLIC API
# =========================
@router.post("/login")
async def login_superadmin(
    email: str = Form(...),
    password: str = Form(...),
    db: AsyncSession = Depends(get_db)
):

    return await SuperAdminService.login_superadmin(
        db,
        email,
        password
    )


# =========================
# CREATE ADMIN
# SUPER ADMIN ONLY 🔒
# =========================
@router.post(
    "/create-admin",
    dependencies=[Depends(get_current_superadmin)]
)
async def create_admin(
    name: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    address: str = Form(...),
    aadhaar_file: UploadFile = File(...),

    db: AsyncSession = Depends(get_db),

    current_superadmin=Depends(
        get_current_superadmin
    )
):

    return await SuperAdminService.create_admin(
        db,
        name,
        email,
        password,
        address,
        aadhaar_file
    )


# =========================
# GET ALL ADMINS
# SUPER ADMIN ONLY 🔒
# =========================
@router.get(
    "/admins",
    dependencies=[Depends(get_current_superadmin)]
)
async def get_all_admins(
    db: AsyncSession = Depends(get_db),

    current_superadmin=Depends(
        get_current_superadmin
    )
):

    return await SuperAdminService.get_all_admins(
        db
    )
# =========================
# APPROVE / REJECT ADMIN REQUEST
# SUPER ADMIN ONLY 🔒
# =========================
@router.put(
    "/admin-requests/{request_id}",
    dependencies=[Depends(get_current_superadmin)]
)
async def update_admin_request_status(
    request_id: int,
    request: AdminRequestActionRequest,
    db: AsyncSession = Depends(get_db),
    current_superadmin=Depends(get_current_superadmin)
):

    return await SuperAdminService.update_admin_request_status(
        db=db,
        request_id=request_id,
        status=request.status,
        rejection_reason=request.rejection_reason,
        superadmin_id=current_superadmin["admin_id"]
    )
