from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.core.security import (
    verify_password,
    create_access_token
)

from app.modules.admin.auth.admin_repository import (
    AdminRepository
)

from app.models.models import (
    Admin,
    News,
    Bookmark
)

from app.utils.location_helper import (
    get_location_from_coordinates,
    get_coordinates_from_location
)

from app.utils.api_response import (
    success_response
)


class AdminService:

    # =========================
    # ADMIN LOGIN
    # =========================
    # ADMIN LOGIN
    # =========================
    @staticmethod
    async def login_admin(
        db: AsyncSession,
        email: str,
        password: str
    ):

        admin = await AdminRepository.get_admin_by_email(
            db,
            email
        )

        if not admin:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )

        if admin.role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only Admin can login here"
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

        return success_response(
            "Login successful",
            {
                "access_token": token,
                "token_type": "bearer"
            }
        )


    # =========================
    # ADMIN PROFILE
    # =========================
    @staticmethod
    async def get_profile(
        db: AsyncSession,
        admin_id: int
    ):

        admin = await AdminRepository.get_admin_by_id(
            db,
            admin_id
        )

        if not admin:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Admin not found"
            )

        location = None

        if admin.latitude and admin.longitude:

            location_data = await get_location_from_coordinates(
                admin.latitude,
                admin.longitude
            )

            if location_data:

                city = location_data.get("city")
                state = location_data.get("state")

                if city and state:
                    location = f"{city}, {state}"
                else:
                    location = city or state

        news_result = await db.execute(
            select(News)
            .where(
                News.author_id == admin.admin_id
            )
            .order_by(
                News.created_at.desc()
            )
        )

        news_list = news_result.scalars().all()

        # =========================
        # OVERALL ANALYTICS
        # =========================
        total_bookmarks_received = 0
        total_views_received = 0
        total_likes_received = 0
        total_comments_received = 0
        total_shares_received = 0

        posted_news = []

        for news in news_list:

            bookmark_result = await db.execute(
                select(func.count())
                .select_from(Bookmark)
                .where(
                    Bookmark.news_id == news.news_id
                )
            )

            bookmarks_count = bookmark_result.scalar() or 0

            total_bookmarks_received += bookmarks_count
            total_views_received += news.view_count or 0
            total_likes_received += news.like_count or 0
            total_comments_received += news.comment_count or 0
            total_shares_received += news.share_count or 0

            posted_news.append(
                {
                    "news_id": news.news_id,
                    "title": news.title,

                    "view_count": news.view_count,
                    "like_count": news.like_count,
                    "comment_count": news.comment_count,
                    "share_count": news.share_count,

                    "bookmarks_count": bookmarks_count,

                    "status": news.status,
                    "is_breaking": news.is_breaking,

                    "published_at": news.published_at,
                    "created_at": news.created_at
                }
            )

        return {
            "success": True,
            "message": "Admin profile fetched successfully",
            "data": {
                "admin_id": admin.admin_id,
                "name": admin.name,
                "email": admin.email,

                "location": location,

                "language": admin.preferred_language,
                "notification_enabled": admin.notification_enabled,

                "total_news_posted": len(news_list),

                "total_views_received": total_views_received,
                "total_likes_received": total_likes_received,
                "total_comments_received": total_comments_received,
                "total_shares_received": total_shares_received,
                "total_bookmarks_received": total_bookmarks_received,

                "posted_news": posted_news
            }
        }
        # =========================
    # UPDATE LANGUAGE
    # =========================
    @staticmethod
    async def update_language(
        db: AsyncSession,
        admin_id: int,
        preferred_language: str
    ):

        admin = await AdminRepository.get_admin_by_id(
            db,
            admin_id
        )

        if not admin:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Admin not found"
            )

        admin.preferred_language = preferred_language

        await db.commit()
        await db.refresh(admin)

        return success_response(
            "Language updated successfully",
            {
                "preferred_language": admin.preferred_language
            }
        )

    # =========================
    # UPDATE LOCATION
    # =========================
    @staticmethod
    async def update_location(
        db: AsyncSession,
        admin_id: int,
        state: str,
        district: str,
        mandal: str
    ):

        admin = await AdminRepository.get_admin_by_id(
            db,
            admin_id
        )

        if not admin:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Admin not found"
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

        admin.latitude = latitude
        admin.longitude = longitude

        await db.commit()
        await db.refresh(admin)

        return success_response(
            "Location updated successfully",
            {
                "latitude": latitude,
                "longitude": longitude
            }
        )