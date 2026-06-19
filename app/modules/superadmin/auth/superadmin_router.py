from fastapi import (
    APIRouter,
    Depends,
    Form,
    File,
    UploadFile
)

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.db import get_db

from app.core.security import (
    get_current_superadmin
)

from app.modules.superadmin.auth.superadmin_service import (
    SuperAdminService
)

router = APIRouter()


@router.post("/login")
async def login_superadmin(
    email: str = Form(...),
    password: str = Form(...),
    db: AsyncSession = Depends(
        get_db
    )
):

    return await (
        SuperAdminService
        .login_superadmin(
            db,
            email,
            password
        )
    )


@router.post("/create-admin")
async def create_admin(
    name: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    address: str = Form(...),

    aadhaar_file: UploadFile = File(...),

    db: AsyncSession = Depends(
        get_db
    ),

    current_superadmin=Depends(
        get_current_superadmin
    )
):

    return await (
        SuperAdminService
        .create_admin(
            db,
            name,
            email,
            password,
            address,
            aadhaar_file
        )
    )


@router.get("/admins")
async def get_all_admins(
    db: AsyncSession = Depends(
        get_db
    ),

    current_superadmin=Depends(
        get_current_superadmin
    )
):

    return await (
        SuperAdminService
        .get_all_admins(
            db
        )
    )