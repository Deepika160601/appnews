import re

from fastapi import HTTPException, status

from sqlalchemy import (
    select,
    func
)

from sqlalchemy.exc import SQLAlchemyError

from sqlalchemy.ext.asyncio import AsyncSession

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
# LOGIN (ADMIN ONLY)
# =========================
 @staticmethod
 async def login(
    db: AsyncSession,
    email: str,
    password: str
):
    try:

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
        # Check Admin
        # -------------------------
        admin = await AdminRepository.get_admin_by_email(
            db,
            email
        )

        if not admin:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password."
            )

        if not verify_password(
            password,
            admin.password_hash
        ):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password."
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
                "token_type": "bearer",
                "role": admin.role
            }
        )

    except HTTPException:
        raise

    except SQLAlchemyError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred. Please try again later."
        )

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred. Please try again later."
        )
  # =========================
# ADMIN PROFILE
# =========================
@staticmethod
async def get_profile(
    db: AsyncSession,
    admin_id: int
):
    try:

        # -------------------------
        # Validate Admin ID
        # -------------------------
        if not admin_id or admin_id <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid admin ID."
            )

        # -------------------------
        # Get Admin
        # -------------------------
        admin = await AdminRepository.get_admin_by_id(
            db,
            admin_id
        )

        if not admin:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Admin not found."
            )

        location = None

        # -------------------------
        # Get Location
        # -------------------------
        if admin.latitude is not None and admin.longitude is not None:

            try:
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

            except Exception:
                location = None

        # -------------------------
        # Get News
        # -------------------------
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

        # -------------------------
        # Overall Analytics
        # -------------------------
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

        return success_response(
            "Admin profile fetched successfully",
            {
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
        )

    except HTTPException:
        raise

    except SQLAlchemyError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred while fetching the admin profile."
        )

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while fetching the admin profile."
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
    try:

        # -------------------------
        # Validate Admin ID
        # -------------------------
        if not admin_id or admin_id <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid admin ID."
            )

        # -------------------------
        # Validate State
        # -------------------------
        if not state or not state.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="State is required."
            )

        # -------------------------
        # Validate District
        # -------------------------
        if not district or not district.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="District is required."
            )

        # -------------------------
        # Validate Mandal
        # -------------------------
        if not mandal or not mandal.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Mandal is required."
            )

        state = state.strip()
        district = district.strip()
        mandal = mandal.strip()

        # -------------------------
        # Check Admin
        # -------------------------
        admin = await AdminRepository.get_admin_by_id(
            db,
            admin_id
        )

        if not admin:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Admin not found."
            )

        # -------------------------
        # Get Coordinates
        # -------------------------
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

        # -------------------------
        # Validate Coordinates
        # -------------------------
        if latitude is None or longitude is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid location. Please enter a valid State, District, and Mandal."
            )

        # -------------------------
        # Verify Location
        # -------------------------
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

        # -------------------------
        # Validate State
        # -------------------------
        returned_state = (
            location.get("state") or ""
        ).strip().lower()

        if returned_state != state.lower():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid state. Please enter a valid state."
            )

        # -------------------------
        # Validate District
        # -------------------------
        returned_district = (
            location.get("district") or ""
        ).strip().lower()

        if returned_district != district.lower():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid district. Please enter a valid district."
            )

        # -------------------------
        # Update Location
        # -------------------------
        admin.latitude = latitude
        admin.longitude = longitude

        await db.commit()
        await db.refresh(admin)

        return success_response(
            "Location updated successfully",
            {
                "latitude": admin.latitude,
                "longitude": admin.longitude
            }
        )

    except HTTPException:
        await db.rollback()
        raise

    except SQLAlchemyError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred while updating the location."
        )

    except Exception:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while updating the location."
        )