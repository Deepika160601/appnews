
from fastapi import (
    HTTPException,
    status,
    UploadFile
)

from sqlalchemy.ext.asyncio import (
    AsyncSession
)

from app.utils.api_response import success_response

from app.utils.translator import (
    translate_text
)

from app.utils.s3_helper import (
    upload_image_to_s3,
    upload_video_to_s3
)

from app.modules.admin.repositories.news_admin_repository import (
    create_news,
    create_news_translation,
    get_all_news,
    get_news_by_id,
    get_news_by_title,
    publish_news,
    delete_news,
    get_category_by_id
)

from app.modules.user.repositories.user_repository import (
    UserRepository
)
from sqlalchemy.exc import SQLAlchemyError
from app.modules.user.repositories.notification_repository import (
    create_notification
)
from app.modules.superadmin.auth.superadmin_repository import (
    SuperAdminRepository
)

## =========================
# CREATE NEWS
# =========================
async def create_news_service(
    db: AsyncSession,
    data,
    admin_id: int,
    thumbnail: UploadFile,
    video: UploadFile = None
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
        # Validate Title
        # -------------------------
        if not data.title or not data.title.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="News title is required."
            )

        # -------------------------
        # Validate Content
        # -------------------------
        if not data.content or not data.content.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="News content is required."
            )
            # -------------------------
        # Validate Summary
        # -------------------------
        if data.summary is not None and not data.summary.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Summary cannot be empty."
            )

        # -------------------------
        # Validate Category
        # -------------------------
        if not data.category_id or data.category_id <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Valid category is required."
            )

        category = await get_category_by_id(
            db,
            data.category_id
        )

        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found."
            )

        # -------------------------
        # Validate News Type
        # -------------------------
        if data.news_type not in [
            "Local",
            "National",
            "International"
        ]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid news type."
            )

        # -------------------------
        # Validate Original Language
        # -------------------------
        if data.original_language not in [
            "en",
            "te"
        ]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Unsupported language."
            )

        # -------------------------
        # Validate Thumbnail
        # -------------------------
        if not thumbnail:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Thumbnail image is required."
            )

        allowed_image_extensions = (
            ".jpg",
            ".jpeg",
            ".png",
            ".webp"
        )

        if not thumbnail.filename.lower().endswith(
            allowed_image_extensions
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only JPG, JPEG, PNG and WEBP images are allowed."
            )

        # -------------------------
        # Validate Video
        # -------------------------
        if video:

            allowed_video_extensions = (
                ".mp4",
                ".mov",
                ".avi",
                ".mkv"
            )

            if not video.filename.lower().endswith(
                allowed_video_extensions
            ):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Only MP4, MOV, AVI and MKV videos are allowed."
                )

        # -------------------------
        # Check Duplicate News
        # -------------------------
        existing_news = await get_news_by_title(
            db,
            data.title
        )

        if (
            existing_news and
            existing_news.content.strip().lower()
            == data.content.strip().lower()
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="News already exists."
            )

        # -------------------------
        # Validate Thumbnail
        # -------------------------
        if not thumbnail:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Thumbnail image is required."
            )

        # -------------------------
        # Upload Thumbnail
        # -------------------------
        thumbnail_url = await upload_image_to_s3(
            thumbnail
        )

        # -------------------------
        # Upload Video
        # -------------------------
        video_url = None

        if video:
            video_url = await upload_video_to_s3(
                video
            )

        # -------------------------
        # Create News
        # -------------------------
        news_data = data.dict()

        news_data["author_id"] = admin_id
        news_data["thumbnail_url"] = thumbnail_url
        news_data["video_url"] = video_url

        news = await create_news(
            db,
            news_data
        )

        # -------------------------
        # Auto Translation
        # -------------------------
        if data.original_language == "en":

            await create_news_translation(
                db=db,
                news_id=news.news_id,
                language="te",
                translated_title=translate_text(
                    data.title,
                    "en",
                    "te"
                ),
                translated_summary=translate_text(
                    data.summary or "",
                    "en",
                    "te"
                ),
                translated_content=translate_text(
                    data.content,
                    "en",
                    "te"
                )
            )

        elif data.original_language == "te":

            await create_news_translation(
                db=db,
                news_id=news.news_id,
                language="en",
                translated_title=translate_text(
                    data.title,
                    "te",
                    "en"
                ),
                translated_summary=translate_text(
                    data.summary or "",
                    "te",
                    "en"
                ),
                translated_content=translate_text(
                    data.content,
                    "te",
                    "en"
                )
            )

        category = await get_category_by_id(
            db,
            news.category_id
        )

        return success_response(
            "News created successfully",
            {
                "news_id": news.news_id,
                "title": news.title,
                "content": news.content,
                "summary": news.summary,
                "category_id": news.category_id,
                "category_name": category.name if category else None,
                "author_id": news.author_id,
                "news_type": news.news_type,
                "country": news.country,
                "state": news.state,
                "district": news.district,
                "mandal": news.mandal,
                "city": news.city,
                "village": news.village,
                "is_breaking": news.is_breaking,
                "thumbnail_url": news.thumbnail_url,
                "video_url": news.video_url,
                "view_count": news.view_count,
                "like_count": news.like_count,
                "comment_count": news.comment_count,
                "share_count": news.share_count,
                "status": news.status,
                "created_at": news.created_at,
                "published_at": news.published_at
            }
        )

    except HTTPException:
        await db.rollback()
        raise

    except SQLAlchemyError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred while creating news."
        )

    except Exception:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while creating news."
        )
      
## =========================
# GET ALL NEWS
# =========================
async def get_all_news_service(
    db: AsyncSession
):

    news_list = await get_all_news(
        db
    )

    if news_list is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="News not found."
        )

    return success_response(
        "News fetched successfully",
        news_list
    )

# =========================
# GET NEWS BY ID
# =========================
async def get_news_by_id_service(
    db: AsyncSession,
    news_id: int
):

    # -------------------------
    # Validate News ID
    # -------------------------
    if news_id <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid news ID."
        )

    # -------------------------
    # Get News
    # -------------------------
    news = await get_news_by_id(
        db,
        news_id
    )

    # -------------------------
    # Check News Exists
    # -------------------------
    if not news:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="News not found."
        )

    # -------------------------
    # Success Response
    # -------------------------
    return success_response(
        "News fetched successfully",
        news
    )
# =========================
# PUBLISH NEWS
# =========================
async def publish_news_service(
    db: AsyncSession,
    news_id: int
):

    try:

        # -------------------------
        # Validate News ID
        # -------------------------
        if news_id <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid news ID."
            )

        # -------------------------
        # Get News
        # -------------------------
        news = await get_news_by_id(
            db,
            news_id
        )

        if not news:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="News not found."
            )

        # -------------------------
        # Check News Status
        # -------------------------
        if news.status == "published":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="News is already published."
            )

        # -------------------------
        # Publish News
        # -------------------------
        published_news = await publish_news(
            db,
            news
        )

        # -------------------------
        # Get Super Admin
        # -------------------------
        superadmin = await SuperAdminRepository.get_superadmin(
            db
        )

        # -------------------------
        # Notify Super Admin
        # -------------------------
        if superadmin:

            await create_notification(
                db=db,
                admin_id=superadmin.admin_id,
                news_id=published_news.news_id,
                title="News Published",
                message=(
                    f"Admin published news: "
                    f"{published_news.title}"
                )
            )

        # -------------------------
        # Success Response
        # -------------------------
        return success_response(
            "News published successfully",
            published_news
        )

    except HTTPException:
        await db.rollback()
        raise

    except SQLAlchemyError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred while publishing news."
        )

    except Exception:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while publishing news."
        )
# from sqlalchemy.exc import SQLAlchemyError


# =========================
# DELETE NEWS
# =========================
async def delete_news_service(
    db: AsyncSession,
    news_id: int
):

    try:

        # -------------------------
        # Validate News ID
        # -------------------------
        if news_id <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid news ID."
            )

        # -------------------------
        # Get News
        # -------------------------
        news = await get_news_by_id(
            db,
            news_id
        )

        if not news:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="News not found."
            )

        # -------------------------
        # Delete News
        # -------------------------
        await delete_news(
            db,
            news
        )

        # -------------------------
        # Success Response
        # -------------------------
        return success_response(
            "News deleted successfully",
            {
                "news_id": news_id
            }
        )

    except HTTPException:
        await db.rollback()
        raise

    except SQLAlchemyError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred while deleting news."
        )

    except Exception:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while deleting news."
        )