from fastapi import (
    HTTPException,
    status
)

from sqlalchemy.ext.asyncio import AsyncSession

from app.utils.api_response import success_response

from app.modules.superadmin.auth.news.superadmin_news_repository import (
    SuperAdminNewsRepository
)


class SuperAdminNewsService:

    @staticmethod
    async def get_all_news(
        db: AsyncSession
    ):

        news_list = await (
            SuperAdminNewsRepository
            .get_all_news(db)
        )

        if not news_list:
            return success_response(
                "No news found",
                []
            )

        data = []

        for news in news_list:

            data.append(
                {
                    "news_id": news.news_id,
                    "headline": news.title,
                    "admin_name": (
                        news.author.name
                        if news.author
                        else None
                    ),
                    "category": (
                        news.category.name
                        if news.category
                        else None
                    ),
                    "location": news.state,
                    "status": news.status,
                    "views": news.view_count,
                    "breaking_news": (
                        "Yes"
                        if news.is_breaking
                        else "No"
                    ),
                    "date_time": (
                        news.created_at.strftime(
                            "%Y-%m-%d %H:%M:%S"
                        )
                        if news.created_at
                        else None
                    )
                }
            )

        return success_response(
            "News fetched successfully",
            data
        )
    @staticmethod
    async def delete_news(
        db: AsyncSession,
        news_id: int
    ):

        news = await (
            SuperAdminNewsRepository
            .get_news_by_id(
                db,
                news_id
            )
        )

        if not news:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="News not found"
            )

        await (
            SuperAdminNewsRepository
            .delete_news(
                db,
                news
            )
        )

        return success_response(
            "News deleted successfully"
        )