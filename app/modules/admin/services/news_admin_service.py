
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

from app.modules.user.repositories.notification_repository import (
    create_notification
)


# =========================
# CREATE NEWS
# =========================
async def create_news_service(
    db: AsyncSession,
    data,
    admin_id: int,
    thumbnail: UploadFile,
    video: UploadFile = None
):

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
            detail="News already exists"
        )

    if not thumbnail:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Thumbnail image is required"
        )

    thumbnail_url = await upload_image_to_s3(
        thumbnail
    )

    video_url = None

    if video:
        video_url = await upload_video_to_s3(
            video
        )

    news_data = data.dict()

    news_data["author_id"] = admin_id
    news_data["thumbnail_url"] = thumbnail_url
    news_data["video_url"] = video_url

    news = await create_news(
        db,
        news_data
    )

    # =========================
    # AUTO TRANSLATION
    # =========================
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
# =========================
# GET ALL NEWS
# =========================
async def get_all_news_service(
    db: AsyncSession
):

    news_list = await get_all_news(
        db
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

    news = await get_news_by_id(
        db,
        news_id
    )

    if not news:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="News not found"
        )

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

    news = await get_news_by_id(
        db,
        news_id
    )

    if not news:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="News not found"
        )

    published_news = await publish_news(
        db,
        news
    )

    users = await UserRepository.get_all_users(
        db
    )

    for user in users:

        await create_notification(
            db=db,
            user_id=user.user_id,
            news_id=published_news.news_id,
            title="Breaking News",
            message=published_news.title
        )

    return success_response(
        "News published successfully",
        published_news
    )


# =========================
# DELETE NEWS
# =========================
async def delete_news_service(
    db: AsyncSession,
    news_id: int
):

    news = await get_news_by_id(
        db,
        news_id
    )

    if not news:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="News not found"
        )

    await delete_news(
        db,
        news
    )

    return success_response(
        "News deleted successfully",
        {
            "news_id": news_id
        }
    )

