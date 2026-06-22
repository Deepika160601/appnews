from sqlalchemy import (
    select,
    func,
    extract
)

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.models import (
    NewsView,
    News,
    Category,
    User,
    Admin
)


class SuperAdminAnalyticsRepository:

    # =========================
    # LIVE VISITORS
    # =========================
    @staticmethod
    async def get_live_visitors(
        db: AsyncSession
    ):

        result = await db.execute(
            select(
                func.count(
                    NewsView.view_id
                )
            )
        )

        return result.scalar() or 0

    # =========================
    # HOURLY VIEWS
    # =========================
    @staticmethod
    async def get_hourly_views(
        db: AsyncSession
    ):

        result = await db.execute(
            select(
                extract(
                    "hour",
                    NewsView.viewed_at
                ).label("hour"),

                func.count(
                    NewsView.view_id
                ).label("views")
            )
            .group_by("hour")
            .order_by("hour")
        )

        return result.all()

    # =========================
    # TOP CATEGORIES
    # =========================
    @staticmethod
    async def get_top_categories(
        db: AsyncSession
    ):

        result = await db.execute(
            select(
                Category.name,
                func.count(
                    News.news_id
                ).label("total_posts")
            )
            .join(
                News,
                News.category_id ==
                Category.category_id
            )
            .group_by(
                Category.category_id
            )
            .order_by(
                func.count(
                    News.news_id
                ).desc()
            )
            .limit(5)
        )

        return result.all()

    # =========================
    # TOP LOCATIONS
    # =========================
    @staticmethod
    async def get_top_locations(
        db: AsyncSession
    ):

        result = await db.execute(
            select(
                News.city,
                func.count(
                    News.news_id
                ).label("total_news")
            )
            .group_by(
                News.city
            )
            .order_by(
                func.count(
                    News.news_id
                ).desc()
            )
            .limit(5)
        )

        return result.all()

    # =========================
    # TOP ADMINS
    # =========================
    @staticmethod
    async def get_top_admins(
        db: AsyncSession
    ):

        result = await db.execute(
            select(
                Admin.name,
                func.count(
                    News.news_id
                ).label("total_news")
            )
            .join(
                News,
                News.author_id ==
                Admin.admin_id
            )
            .group_by(
                Admin.admin_id
            )
            .order_by(
                func.count(
                    News.news_id
                ).desc()
            )
            .limit(5)
        )

        return result.all()

    # =========================
    # LANGUAGE CONSUMPTION
    # =========================
    @staticmethod
    async def get_language_consumption(
        db: AsyncSession
    ):

        result = await db.execute(
            select(
                User.preferred_language,
                func.count(
                    User.user_id
                ).label("total_users")
            )
            .group_by(
                User.preferred_language
            )
        )

        return result.all()