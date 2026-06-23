from sqlalchemy import (
    select,
    func
)

from sqlalchemy.ext.asyncio import (
    AsyncSession
)

from app.models.models import (
    User,
    NewsView
)


class SuperAdminLocationRepository:

    # =========================
    # GET LOCATION ANALYTICS
    # =========================
    @staticmethod
    async def get_location_analytics(
        db: AsyncSession
    ):

        # Total Users
        users_result = await db.execute(
            select(
                func.count(
                    User.user_id
                )
            )
        )

        total_users = (
            users_result.scalar() or 0
        )

        # Total Views
        views_result = await db.execute(
            select(
                func.count(
                    NewsView.view_id
                )
            )
        )

        total_views = (
            views_result.scalar() or 0
        )

        # Active Readers
        readers_result = await db.execute(
            select(
                func.count(
                    func.distinct(
                        NewsView.user_id
                    )
                )
            )
        )

        active_readers = (
            readers_result.scalar() or 0
        )

        return {
            "total_users": total_users,
            "total_views": total_views,
            "active_readers": active_readers
        }