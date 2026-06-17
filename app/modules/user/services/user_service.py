from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.models import (
    User,
    Bookmark,
    Like,
    Comment,
    PollVote,
    Notification
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

    # =========================
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

        user = await UserRepository.get_user_by_id(
            db,
            user_id
        )

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        latitude, longitude = await get_coordinates_from_location(
            state,
            district,
            mandal
        )

        if latitude is None or longitude is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Unable to determine coordinates"
            )

        user.latitude = latitude
        user.longitude = longitude

        await db.commit()
        await db.refresh(user)

        return success_response(
            "Location updated successfully",
            {
                "latitude": latitude,
                "longitude": longitude
            }
        )