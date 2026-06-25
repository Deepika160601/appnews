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

    result = await db.execute(
        select(
            User.city,
            User.state,
            func.count(
                func.distinct(
                    NewsView.user_id
                )
            ).label("active_readers")
        )
        .join(
            NewsView,
            User.user_id == NewsView.user_id
        )
        .where(
            User.city.is_not(None),
            User.state.is_not(None)
        )
        .group_by(
            User.city,
            User.state
        )
        .order_by(
            func.count(
                func.distinct(
                    NewsView.user_id
                )
            ).desc()
        )
    )

    locations = result.all()

    return [
        {
            "city": item.city,
            "state": item.state,
            "active_readers": item.active_readers,

            # Placeholder until you implement growth calculation
            "growth_percentage": 0
        }
        for item in locations
    ]