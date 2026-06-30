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
from datetime import datetime

from app.models.models import (
    AdminRequest
)

from app.modules.user.repositories.notification_repository import (
    create_notification
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
        # =========================
    # APPROVE / REJECT ADMIN REQUEST
    # =========================
    @staticmethod
    async def update_admin_request_status(
        db: AsyncSession,
        request_id: int,
        status: str,
        rejection_reason: str = None,
        superadmin_id: int = None
    ):

        admin_request = await (
            SuperAdminRepository.get_admin_request_by_id(
                db,
                request_id
            )
        )

        if not admin_request:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Admin request not found."
            )

        if admin_request.status != "Pending":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="This request has already been processed."
            )

        if status not in ["Approved", "Rejected"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid status."
            )

        if (
            status == "Rejected"
            and not rejection_reason
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Rejection reason is required."
            )

        admin_request.status = status
        admin_request.reviewed_by = superadmin_id
        admin_request.reviewed_at = datetime.utcnow()

        if status == "Rejected":
            admin_request.rejection_reason = rejection_reason

        await SuperAdminRepository.update_admin_request(
            db,
            admin_request
        )

        # Notify User
        await create_notification(
            db=db,
            news_id=None,
            user_id=admin_request.user_id,
            title="Admin Request Update",
            message=(
                "Congratulations! Your admin request has been approved."
                if status == "Approved"
                else f"Your admin request has been rejected. Reason: {rejection_reason}"
            )
        )

        return {
            "success": True,
            "message": f"Admin request {status.lower()} successfully.",
            "data": {
                "request_id": admin_request.request_id,
                "status": admin_request.status,
                "reviewed_by": admin_request.reviewed_by,
                "reviewed_at": admin_request.reviewed_at,
                "rejection_reason": admin_request.rejection_reason
            }
        }