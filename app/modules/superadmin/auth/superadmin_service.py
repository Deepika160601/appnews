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

import re


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

        # -------------------------
        # Validate Email
        # -------------------------
        if not email or not email.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email is required."
            )

        email = email.strip().lower()

        if not re.fullmatch(
            r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$",
            email
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Please enter a valid email address."
            )

        # -------------------------
        # Validate Password
        # -------------------------
        if not password or not password.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password is required."
            )

        # -------------------------
        # Get Super Admin
        # -------------------------
        admin = await SuperAdminRepository.get_admin_by_email(
            db,
            email
        )

        if not admin:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password."
            )

        # -------------------------
        # Check Role
        # -------------------------
        if admin.role != "superadmin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only Super Admin can log in."
            )

        # -------------------------
        # Verify Password
        # -------------------------
        if not verify_password(
            password,
            admin.password_hash
        ):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password."
            )

        # -------------------------
        # Generate Token
        # -------------------------
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
                "token_type": "bearer",
                "role": admin.role
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

        # -------------------------
        # Validate Name
        # -------------------------
        if not name or not name.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Name is required."
            )

        if len(name.strip()) < 3:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Name must contain at least 3 characters."
            )

        if not re.fullmatch(
            r"^[A-Za-z ]+$",
            name.strip()
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Name should contain only alphabets and spaces."
            )

        # -------------------------
        # Validate Email
        # -------------------------
        if not email or not email.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email is required."
            )

        email = email.strip().lower()

        if not re.fullmatch(
            r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$",
            email
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Please enter a valid email address."
            )

        # -------------------------
        # Check Existing Email
        # -------------------------
        existing_admin = await SuperAdminRepository.get_admin_by_email(
            db,
            email
        )

        if existing_admin:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Admin with this email already exists."
            )

        # -------------------------
        # Validate Password
        # -------------------------
        if not password or not password.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password is required."
            )

        if len(password) < 8:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password must be at least 8 characters long."
            )

        # -------------------------
        # Validate Address
        # -------------------------
        if not address or not address.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Address is required."
            )

        # -------------------------
        # Validate Aadhaar File
        # -------------------------
        if not aadhaar_file:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Aadhaar file is required."
            )

        allowed_extensions = (
            ".pdf",
            ".jpg",
            ".jpeg",
            ".png"
        )

        if not aadhaar_file.filename.lower().endswith(
            allowed_extensions
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only PDF, JPG, JPEG and PNG files are allowed."
            )

        # -------------------------
        # Upload Aadhaar
        # -------------------------
        aadhaar_url = await upload_document_to_s3(
            aadhaar_file
        )

        # -------------------------
        # Create Admin
        # -------------------------
        admin = Admin(
            name=name.strip(),
            email=email,
            password_hash=hash_password(password),
            address=address.strip(),
            aadhaar_file=aadhaar_url,
            role="admin"
        )

        created_admin = await SuperAdminRepository.create_admin(
            db,
            admin
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

        admins = await SuperAdminRepository.get_all_admins(
            db
        )

        if not admins:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No admins found."
            )

        return {
            "success": True,
            "message": "Admins fetched successfully",
            "data": admins
        }
#    # =========================
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

        # -------------------------
        # Validate Request ID
        # -------------------------
        if request_id <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid request ID."
            )

        # -------------------------
        # Validate Super Admin ID
        # -------------------------
        if superadmin_id is None or superadmin_id <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid super admin ID."
            )

        # -------------------------
        # Validate Status
        # -------------------------
        if not status or not status.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Status is required."
            )

        status = status.strip().capitalize()

        if status not in ["Approved", "Rejected"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Status must be either 'Approved' or 'Rejected'."
            )

        # -------------------------
        # Get Admin Request
        # -------------------------
        admin_request = await SuperAdminRepository.get_admin_request_by_id(
            db,
            request_id
        )

        if not admin_request:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Admin request not found."
            )

        # -------------------------
        # Check Request Status
        # -------------------------
        if admin_request.status != "Pending":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="This admin request has already been processed."
            )

        # -------------------------
        # Validate Rejection Reason
        # -------------------------
        if status == "Rejected":

            if not rejection_reason or not rejection_reason.strip():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Rejection reason is required."
                )

            rejection_reason = rejection_reason.strip()

        # -------------------------
        # Update Request
        # -------------------------
        admin_request.status = status
        admin_request.reviewed_by = superadmin_id
        admin_request.reviewed_at = datetime.utcnow()

        if status == "Rejected":
            admin_request.rejection_reason = rejection_reason

        await SuperAdminRepository.update_admin_request(
            db,
            admin_request
        )

        # -------------------------
        # Notify User
        # -------------------------
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