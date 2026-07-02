from fastapi import (
    HTTPException,
    status
)

from sqlalchemy.ext.asyncio import (
    AsyncSession
)

from app.utils.api_response import success_response

from app.modules.user.repositories.search_repository import (
    search_news
)


# =========================
# SEARCH NEWS
# =========================
async def search_news_service(
    db: AsyncSession,
    keyword: str
):

    # -------------------------
    # Validate Keyword
    # -------------------------
    if not keyword or not keyword.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Search keyword is required."
        )

    keyword = keyword.strip()

    news = await search_news(
        db,
        keyword
    )

    if not news:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No news found."
        )

    return success_response(
        "Search results fetched successfully",
        news
    )