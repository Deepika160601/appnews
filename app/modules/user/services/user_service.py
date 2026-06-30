from fastapi import (
    HTTPException,
    UploadFile,
    status
)
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.models import (
    User,
    Bookmark,
    Like,
    Comment,
    PollVote,
    Notification,
    AdminRequest
)
from app.utils.location_helper import (
    get_location_from_coordinates,
    get_coordinates_from_location
)

from sqlalchemy import select, func
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token
)

from app.utils.api_response import success_response

from app.modules.user.repositories.user_repository import (
    UserRepository
)

from app.utils.s3_helper import (
    upload_document_to_s3
)
from app.modules.user.repositories.notification_repository import (
    create_notification
)
class UserService:

    # =========================
    # REGISTER USER
    # =========================
    @staticmethod
    async def register_user(
        db: AsyncSession,
        name: str,
        email: str,
        mobile_number: str,
        password: str,
        latitude: float | None = None,
        longitude: float | None = None
    ):

        existing_user = await UserRepository.get_user_by_email(
            db,
            email
        )

        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )

        existing_mobile = await UserRepository.get_user_by_mobile_number(
            db,
            mobile_number
        )

        if existing_mobile:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Mobile number already registered"
            )

        user = User(
            name=name,
            email=email,
            mobile_number=mobile_number,
            password_hash=hash_password(password),
            latitude=latitude,
            longitude=longitude
        )

        created_user = await UserRepository.create_user(
            db,
            user
        )

        return success_response(
            "User registered successfully",
            {
                "user_id": created_user.user_id,
                "name": created_user.name,
                "email": created_user.email,
                "mobile_number": created_user.mobile_number,
                "preferred_language": created_user.preferred_language,
                "latitude": created_user.latitude,
                "longitude": created_user.longitude,
                "created_at": created_user.created_at
            }
        )
        # =========================
    # LOGIN USER
    # =========================
    @staticmethod
    async def login_user(
        db: AsyncSession,
        email: str,
        password: str
    ):

        user = await UserRepository.get_user_by_email(
            db,
            email
        )

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        if not verify_password(
            password,
            user.password_hash
        ):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )

        access_token = create_access_token(
            {
                "user_id": user.user_id,
                "email": user.email,
                "role": "user"
            }
        )

        return success_response(
            "Login successful",
            {
                "access_token": access_token,
                "token_type": "bearer"
            }
        )

    # =========================
    # GET PROFILE
    # =========================
    @staticmethod
    async def get_profile(
        db: AsyncSession,
        user_id: int
    ):

        user = await UserRepository.get_user_by_id(
            db,
            user_id
        )

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        location = None

        if user.latitude and user.longitude:
            location = await get_location_from_coordinates(
                user.latitude,
                user.longitude
            )

        # Total Bookmarks
        bookmark_result = await db.execute(
            select(func.count())
            .select_from(Bookmark)
            .where(
                Bookmark.user_id == user.user_id
            )
        )

        total_bookmarks = bookmark_result.scalar() or 0

        # Total Likes
        like_result = await db.execute(
            select(func.count())
            .select_from(Like)
            .where(
                Like.user_id == user.user_id
            )
        )

        total_likes = like_result.scalar() or 0

        # Total Comments
        comment_result = await db.execute(
            select(func.count())
            .select_from(Comment)
            .where(
                Comment.user_id == user.user_id
            )
        )

        total_comments = comment_result.scalar() or 0

        # Total Poll Votes
        poll_vote_result = await db.execute(
            select(func.count())
            .select_from(PollVote)
            .where(
                PollVote.user_id == user.user_id
            )
        )

        total_poll_votes = poll_vote_result.scalar() or 0

        # Unread Notifications
        notification_result = await db.execute(
            select(func.count())
            .select_from(Notification)
            .where(
                Notification.user_id == user.user_id,
                Notification.is_read == False
            )
        )

        unread_notifications = notification_result.scalar() or 0

        return success_response(
            "Profile fetched successfully",
            {
                "user_id": user.user_id,
                "name": user.name,
                "email": user.email,
                "mobile_number": user.mobile_number,

                "location": location,

                "preferred_language": user.preferred_language,
                "notification_enabled": user.notification_enabled,

                "total_bookmarks": total_bookmarks,
                "total_likes": total_likes,
                "total_comments": total_comments,
                "total_poll_votes": total_poll_votes,
                "unread_notifications": unread_notifications
            }
        )
    # =========================
    # UPDATE LANGUAGE
    # =========================
    @staticmethod
    async def update_language(
        db: AsyncSession,
        user_id: int,
        preferred_language: str
    ):

        user = await UserRepository.get_user_by_id(
            db,
            user_id
        )

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        user.preferred_language = preferred_language

        await db.commit()
        await db.refresh(user)

        return success_response(
            "Language updated successfully",
            {
                "preferred_language": user.preferred_language
            }
        )
#    # =========================
    # UPDATE LOCATION
    # =========================
    @staticmethod
    async def update_location(
        db: AsyncSession,
        user_id: int,
        state: str,
        district: str,
        mandal: str
    ):

        # Check if user exists
        user = await UserRepository.get_user_by_id(
            db,
            user_id
        )

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found."
            )

        # Get coordinates from the entered location
        try:
            latitude, longitude = await get_coordinates_from_location(
                state,
                district,
                mandal
            )
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Location service is temporarily unavailable. Please try again later."
            )

        # Invalid location
        if latitude is None or longitude is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid location. Please enter a valid State, District, and Mandal."
            )

        # Reverse geocode to verify location
        try:
            location = await get_location_from_coordinates(
                latitude,
                longitude
            )
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Unable to verify the provided location. Please try again later."
            )

        if not location:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Location verification failed."
            )

        # Validate State
        returned_state = (
            location.get("state") or ""
        ).strip().lower()

        entered_state = (
            state or ""
        ).strip().lower()

        if returned_state != entered_state:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid state. Please enter a valid state."
            )

        # Validate District
        returned_district = (
            location.get("district") or ""
        ).strip().lower()

        entered_district = (
            district or ""
        ).strip().lower()

        if returned_district != entered_district:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid district. Please enter a valid district."
            )

        # Update user location
        user.latitude = latitude
        user.longitude = longitude
        user.state = location.get("state")
        user.district = location.get("district")
        user.city = location.get("city")
        user.country = location.get("country")

        await db.commit()
        await db.refresh(user)

        return success_response(
            "Location updated successfully",
            {
                "latitude": user.latitude,
                "longitude": user.longitude,
                "city": user.city,
                "district": user.district,
                "state": user.state,
                "country": user.country
            }
        )
        # =========================
    # REQUEST TO BECOME ADMIN
    # =========================
    @staticmethod
    async def request_become_admin(
        db: AsyncSession,
        user_id: int,
        reason: str,
        government_id_type: str,
        address: str,
        experience: str,
        government_id: UploadFile
    ):

        # Check user
        user = await UserRepository.get_user_by_id(
            db,
            user_id
        )

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found."
            )

        # Check pending request
        pending_request = await UserRepository.get_pending_admin_request(
            db,
            user_id
        )

        if pending_request:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="You already have a pending admin request."
            )

        # Upload Government ID
        try:
            government_id_url = await upload_document_to_s3(
                government_id
            )
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Unable to upload Government ID. Please try again later."
            )

        # Create request
        admin_request = AdminRequest(
            user_id=user.user_id,
            reason=reason,
            government_id_type=government_id_type,
            government_id_url=government_id_url,
            address=address,
            experience=experience,
            status="Pending"
        )

        await UserRepository.create_admin_request(
            db,
            admin_request
        )

        # Notify Super Admin
        await create_notification(
            db=db,
            news_id=None,
            title="New Admin Request",
            message=f"{user.name} has requested to become an Admin.",
            admin_id=1
        )

        return success_response(
            "Admin request submitted successfully.",
            {
                "request_id": admin_request.request_id,
                "status": admin_request.status
            }
        )