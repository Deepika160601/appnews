from fastapi import (
    HTTPException,
    UploadFile,
    status
)

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.models import Admin

from app.core.security import (
    hash_password,
    verify_password,
    create_access_token
)

from app.utils.s3_helper import (
    upload_document_to_s3
)

from app.modules.superadmin.auth.superadmin_repository import (
    SuperAdminRepository
)


class SuperAdminService:

    # =========================
    # LOGIN SUPER ADMIN
    # =========================
    @staticmethod
    async def login_superadmin(
        db: AsyncSession,
        email: str,
        password: str
    ):

        admin = await (
            SuperAdminRepository
            .get_admin_by_email(
                db,
                email
            )
        )

        if not admin:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )

        if admin.role != "superadmin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only Super Admin can login here"
            )

        if not verify_password(
            password,
            admin.password_hash
        ):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )

        token = create_access_token(
            {
                "admin_id": admin.admin_id,
                "email": admin.email,
                "role": admin.role
            }
        )

        return {
            "success": True,
            "message": "Login successful",
            "data": {
                "access_token": token,
                "token_type": "bearer"
            }
        }

    # =========================
    # CREATE ADMIN
    # =========================
    @staticmethod
    async def create_admin(
        db: AsyncSession,
        name: str,
        email: str,
        password: str,
        address: str,
        aadhaar_file: UploadFile
    ):

        existing_admin = await (
            SuperAdminRepository
            .get_admin_by_email(
                db,
                email
            )
        )

        if existing_admin:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already exists"
            )

        if not aadhaar_file:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Aadhaar file is required"
            )

        aadhaar_url = await upload_document_to_s3(
            aadhaar_file
        )

        admin = Admin(
            name=name,
            email=email,
            password_hash=hash_password(
                password
            ),
            address=address,
            aadhaar_file=aadhaar_url,
            role="admin"
        )

        created_admin = await (
            SuperAdminRepository
            .create_admin(
                db,
                admin
            )
        )

        return {
            "success": True,
            "message": "Admin created successfully",
            "data": {
                "admin_id": created_admin.admin_id,
                "name": created_admin.name,
                "email": created_admin.email,
                "aadhaar_file": created_admin.aadhaar_file
            }
        }

    # =========================
    # GET ALL ADMINS
    # =========================
    @staticmethod
    async def get_all_admins(
        db: AsyncSession
    ):

        admins = await (
            SuperAdminRepository
            .get_all_admins(db)
        )

        return {
            "success": True,
            "message": "Admins fetched successfully",
            "data": admins
        }