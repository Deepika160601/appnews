import os
import uuid

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

from app.modules.superadmin.auth.superadmin_repository import (
    SuperAdminRepository
)


class SuperAdminService:

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
                status_code=404,
                detail="Super Admin not found"
            )

        if admin.role != "superadmin":

            raise HTTPException(
                status_code=403,
                detail="Access denied"
            )

        if not verify_password(
            password,
            admin.password_hash
        ):

            raise HTTPException(
                status_code=401,
                detail="Invalid credentials"
            )

        token = create_access_token(
            {
                "admin_id":
                admin.admin_id,

                "email":
                admin.email,

                "role":
                admin.role
            }
        )

        return {
            "success": True,
            "message":
            "Login successful",
            "data": {
                "access_token":
                token,

                "token_type":
                "bearer"
            }
        }

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
                status_code=400,
                detail="Email already exists"
            )

        upload_dir = (
            "uploads/aadhaar"
        )

        os.makedirs(
            upload_dir,
            exist_ok=True
        )

        extension = (
            aadhaar_file.filename
            .split(".")[-1]
        )

        filename = (
            f"{uuid.uuid4()}.{extension}"
        )

        file_path = os.path.join(
            upload_dir,
            filename
        )

        content = await (
            aadhaar_file.read()
        )

        with open(
            file_path,
            "wb"
        ) as file:

            file.write(
                content
            )

        admin = Admin(
            name=name,
            email=email,
            password_hash=hash_password(
                password
            ),
            address=address,
            aadhaar_file=file_path,
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
            "message":
            "Admin created successfully",
            "data": {
                "admin_id":
                created_admin.admin_id,

                "name":
                created_admin.name,

                "email":
                created_admin.email
            }
        }

    @staticmethod
    async def get_all_admins(
        db: AsyncSession
    ):

        admins = await (
            SuperAdminRepository
            .get_all_admins(
                db
            )
        )

        return {
            "success": True,
            "message":
            "Admins fetched successfully",
            "data": [
                {
                    "admin_id":
                    admin.admin_id,

                    "name":
                    admin.name,

                    "email":
                    admin.email,

                    "address":
                    admin.address,

                    "aadhaar_file":
                    admin.aadhaar_file
                }
                for admin in admins
            ]
        }