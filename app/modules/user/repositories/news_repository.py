from sqlalchemy import (
    select,
    or_
)

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.models import (
    News,
    NewsTranslation
)
from app.utils.translator import translate_text
import re
from app.core.config import settings

# =========================
# GENERATE SEO SLUG
# =========================
def generate_slug(title: str) -> str:
    slug = title.lower()
    slug = re.sub(r"[^a-z0-9\s-]", "", slug)
    slug = re.sub(r"\s+", "-", slug.strip())
    slug = re.sub(r"-+", "-", slug)
    return slug
# =========================
# GET TRANSLATION
# =========================

async def get_translation(
    db: AsyncSession,
    news_id: int,
    language: str
):
    result = await db.execute(
        select(NewsTranslation).where(
            NewsTranslation.news_id == news_id,
            NewsTranslation.language == language
        )
    )

    return result.scalar_one_or_none()


async def get_or_create_translation(
    db: AsyncSession,
    news,
    language: str
):
    translation = await get_translation(
        db,
        news.news_id,
        language
    )

    if translation:
        return translation

    translation = NewsTranslation(
        news_id=news.news_id,
        language=language,
        translated_title=translate_text(
            news.title,
            news.original_language or "en",
            language
        ),
        translated_summary=translate_text(
            news.summary or "",
            news.original_language or "en",
            language
        ),
        translated_content=translate_text(
            news.content,
            news.original_language or "en",
            language
        )
    )

    db.add(translation)

    # Do not commit inside loop
    await db.flush()

    return translation


# =========================
# GET LATEST NEWS
# =========================

async def get_latest_news(
    db: AsyncSession,
    language: str = "en",
    state: str = None,
    district: str = None,
    mandal: str = None,
    city: str = None,
    village: str = None
):

    # =========================
    # LOCAL BREAKING NEWS
    # =========================
    local_breaking_query = select(News).where(
        News.status == "published",
        News.news_type == "local",
        News.is_breaking == True
    )

    if state:
        local_breaking_query = local_breaking_query.where(
            or_(
                News.state == state,
                News.state.is_(None)
            )
        )

    local_breaking_result = await db.execute(
        local_breaking_query.order_by(
            News.created_at.desc()
        )
    )

    local_breaking = local_breaking_result.scalars().all()

    # =========================
    # NATIONAL BREAKING NEWS
    # =========================
    national_breaking_result = await db.execute(
        select(News)
        .where(
            News.status == "published",
            News.news_type == "national",
            News.is_breaking == True
        )
        .order_by(
            News.created_at.desc()
        )
    )

    national_breaking = national_breaking_result.scalars().all()

    # =========================
    # INTERNATIONAL BREAKING NEWS
    # =========================
    international_breaking_result = await db.execute(
        select(News)
        .where(
            News.status == "published",
            News.news_type == "international",
            News.is_breaking == True
        )
        .order_by(
            News.created_at.desc()
        )
    )

    international_breaking = international_breaking_result.scalars().all()

    # =========================
    # LOCAL NEWS
    # =========================
    local_query = select(News).where(
        News.status == "published",
        News.news_type == "local",
        News.is_breaking == False
    )

    if state:
        local_query = local_query.where(
            or_(
                News.state == state,
                News.state.is_(None)
            )
        )

    local_result = await db.execute(
        local_query.order_by(
            News.created_at.desc()
        )
    )

    local_news = local_result.scalars().all()

    # =========================
    # NATIONAL NEWS
    # =========================
    national_result = await db.execute(
        select(News)
        .where(
            News.status == "published",
            News.news_type == "national",
            News.is_breaking == False
        )
        .order_by(
            News.created_at.desc()
        )
    )

    national_news = national_result.scalars().all()

    # =========================
    # INTERNATIONAL NEWS
    # =========================
    international_result = await db.execute(
        select(News)
        .where(
            News.status == "published",
            News.news_type == "international",
            News.is_breaking == False
        )
        .order_by(
            News.created_at.desc()
        )
    )

    international_news = international_result.scalars().all()

    # =========================
    # FINAL ORDER
    # =========================
    ordered_news = (
        local_breaking +
        national_breaking +
        international_breaking +
        local_news +
        national_news +
        international_news
    )

    print("TOTAL NEWS =", len(ordered_news))

    final_news = []

    for news in ordered_news:

        title = news.title
        summary = news.summary

        if language != "en":

            translation = await get_or_create_translation(
                db,
                news,
                language
            )

            if translation:
                title = translation.translated_title
                summary = translation.translated_summary

        final_news.append(
            {
                "news_id": news.news_id,
                "title": title,
                "summary": summary,

                "news_type": news.news_type,

                "state": news.state,
                "district": news.district,
                "mandal": news.mandal,
                "city": news.city,
                "village": news.village,

                "thumbnail_url": news.thumbnail_url,

                "category_id": news.category_id,

                "is_breaking": news.is_breaking,

                "like_count": news.like_count,
                "comment_count": news.comment_count,
                "view_count": news.view_count,

                "published_at": news.published_at,
                "created_at": news.created_at
            }
        )

    return final_news
## =========================
# GET NEWS BY ID
# =========================

async def get_news_by_id(
    db: AsyncSession,
    news_id: int,
    language: str = "en"
):

    result = await db.execute(
        select(News)
        .where(
            News.news_id == news_id,
            News.status == "published"
        )
    )

    news = result.scalar_one_or_none()

    if not news:
        return None

    news.view_count += 1

    await db.commit()
    await db.refresh(news)

    title = news.title
    summary = news.summary
    content = news.content

    if language != "en":

        translation = await get_or_create_translation(
            db,
            news,
            language
        )

        if translation:
            title = translation.translated_title
            summary = translation.translated_summary
            content = translation.translated_content

    return {
        "news_id": news.news_id,
        "title": title,
        "content": content,
        "summary": summary,

        "news_type": news.news_type,

        "state": news.state,
        "district": news.district,
        "mandal": news.mandal,
        "city": news.city,
        "village": news.village,

        "thumbnail_url": news.thumbnail_url,
        "video_url": news.video_url,

        "category_id": news.category_id,

        "is_breaking": news.is_breaking,

        "like_count": news.like_count,
        "comment_count": news.comment_count,
        "view_count": news.view_count,

        "published_at": news.published_at,
        "created_at": news.created_at
    }
# =========================
# SHARE NEWS
# =========================
async def share_news(
    db: AsyncSession,
    news_id: int
):

    result = await db.execute(
        select(News).where(
            News.news_id == news_id,
            News.status == "published"
        )
    )

    news = result.scalar_one_or_none()

    if not news:
        return None

    # Increment share count
    news.share_count += 1

    await db.commit()
    await db.refresh(news)

    # Generate SEO-friendly slug
    slug = generate_slug(news.title)

    # Generate share URL
    share_url = (
        f"{settings.FRONTEND_URL}/news/"
        f"{news.news_id}/{slug}"
    )

    return {
        "news_id": news.news_id,
        "title": news.title,
        "summary": news.summary,
        "share_count": news.share_count,
        "share_url": share_url
    }