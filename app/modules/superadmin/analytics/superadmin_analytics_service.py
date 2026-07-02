from fastapi import (
    HTTPException,
    status
)

from sqlalchemy.ext.asyncio import (
    AsyncSession
)

from app.utils.api_response import (
    success_response
)

from app.modules.superadmin.analytics.superadmin_analytics_repository import (
    SuperAdminAnalyticsRepository
)


class SuperAdminAnalyticsService:

    # =========================
    # GET ANALYTICS
    # =========================
    @staticmethod
    async def get_analytics(
        db: AsyncSession
    ):

        live_visitors = await (
            SuperAdminAnalyticsRepository
            .get_live_visitors(db)
        )

        hourly_views = await (
            SuperAdminAnalyticsRepository
            .get_hourly_views(db)
        )

        top_categories = await (
            SuperAdminAnalyticsRepository
            .get_top_categories(db)
        )

        top_locations = await (
            SuperAdminAnalyticsRepository
            .get_top_locations(db)
        )

        top_admins = await (
            SuperAdminAnalyticsRepository
            .get_top_admins(db)
        )

        language_consumption = await (
            SuperAdminAnalyticsRepository
            .get_language_consumption(db)
        )

        if (
            live_visitors is None
            and hourly_views is None
            and top_categories is None
            and top_locations is None
            and top_admins is None
            and language_consumption is None
        ):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Analytics data not found."
            )

        hourly_data = []

        for hour in range(24):

            views = 0

            for item in hourly_views:

                if int(item.hour) == hour:

                    views = item.views
                    break

            hourly_data.append(
                {
                    "hour": f"{hour}h",
                    "views": views
                }
            )

        category_data = [
            {
                "category_name": item.name,
                "total_posts": item.total_posts
            }
            for item in top_categories
        ]

        location_data = [
            {
                "location": item.city,
                "total_news": item.total_news
            }
            for item in top_locations
        ]

        admin_data = [
            {
                "admin_name": item.name,
                "total_news": item.total_news
            }
            for item in top_admins
        ]

        language_data = [
            {
                "language": item.preferred_language,
                "total_users": item.total_users
            }
            for item in language_consumption
        ]

        return success_response(
            "Analytics fetched successfully",
            {
                "live_visitors": live_visitors,
                "hourly_views": hourly_data,
                "top_categories": category_data,
                "top_locations": location_data,
                "top_admins": admin_data,
                "language_consumption": language_data
            }
        )