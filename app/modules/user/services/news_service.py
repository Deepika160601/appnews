from fastapi import (
    HTTPException,
    status
)

from sqlalchemy.ext.asyncio import (
    AsyncSession
)

from app.utils.api_response import success_response

from app.utils.location_helper import (
    get_location_from_coordinates
)

from app.modules.user.repositories.news_repository import (
    get_latest_news,
    get_news_by_id,
    share_news
)

from app.modules.user.repositories.user_repository import (
    UserRepository
)

from app.modules.admin.auth.admin_repository import (
    AdminRepository
)

from app.modules.user.repositories.news_view_repository import (
    create_news_view
)


# =========================
# GET LATEST NEWS
# =========================
async def get_latest_news_service(
    db: AsyncSession,
    current_user: dict
):

    role = current_user.get("role")

    # =========================
    # USER
    # =========================
    if role == "user":

        user = await UserRepository.get_user_by_id(
            db,
            current_user["user_id"]
        )

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        if (
            user.latitude is None or
            user.longitude is None
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User location not available"
            )

        location = await get_location_from_coordinates(
            user.latitude,
            user.longitude
        )

        if not location:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Unable to detect location"
            )

        news = await get_latest_news(
            db=db,
            language=user.preferred_language,
            state=location.get("state"),
            district=location.get("district"),
            city=location.get("city")
        )

        return success_response(
            "News fetched successfully",
            {
                "language": user.preferred_language,
                "detected_location": location,
                "news": news
            }
        )

    # =========================
    # ADMIN / SUPERADMIN
    # =========================
    admin = await AdminRepository.get_admin_by_id(
        db,
        current_user["admin_id"]
    )

    if not admin:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Admin not found"
        )

    location = None

    if admin.latitude and admin.longitude:

        location = await get_location_from_coordinates(
            admin.latitude,
            admin.longitude
        )

    news = await get_latest_news(
        db=db,
        language=admin.preferred_language,
        state=location.get("state") if location else None,
        district=location.get("district") if location else None,
        city=location.get("city") if location else None
    )

    return success_response(
        "News fetched successfully",
        {
            "language": admin.preferred_language,
            "detected_location": location,
            "news": news
        }
    )


# =========================
# GET NEWS DETAILS
# =========================
async def get_news_by_id_service(
    db: AsyncSession,
    news_id: int,
    current_user: dict
):

    role = current_user.get("role")

    if role == "user":

        user = await UserRepository.get_user_by_id(
            db,
            current_user["user_id"]
        )

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        language = user.preferred_language

    else:

        admin = await AdminRepository.get_admin_by_id(
            db,
            current_user["admin_id"]
        )

        if not admin:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Admin not found"
            )

        language = admin.preferred_language

    news = await get_news_by_id(
        db=db,
        news_id=news_id,
        language=language
    )

    if not news:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="News not found"
        )

    # =========================
    # TRACK NEWS VIEW
    # =========================
    if role == "user":

        await create_news_view(
            db=db,
            user_id=user.user_id,
            news_id=news_id
        )

    return success_response(
        "News details fetched successfully",
        news
    )


# =========================
# SHARE NEWS
# =========================
async def share_news_service(
    db: AsyncSession,
    news_id: int
):

    news = await share_news(
        db,
        news_id
    )

    if not news:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="News not found"
        )

    return success_response(
        "News shared successfully",
        news
    )