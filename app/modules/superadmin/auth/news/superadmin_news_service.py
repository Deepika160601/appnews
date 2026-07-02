from fastapi import (
    HTTPException,
    status
)

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError

from app.utils.api_response import success_response

from app.modules.superadmin.auth.news.superadmin_news_repository import (
    SuperAdminNewsRepository
)


class SuperAdminNewsService:

    # =========================
    # GET ALL NEWS
    # =========================
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

    # =========================
    # DELETE NEWS
    # =========================
    @staticmethod
    async def delete_news(
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
                    detail="News not found."
                )

            # -------------------------
            # Delete News
            # -------------------------
            await (
                SuperAdminNewsRepository
                .delete_news(
                    db,
                    news
                )
            )

            # -------------------------
            # Success Response
            # -------------------------
            return success_response(
                "News deleted successfully"
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