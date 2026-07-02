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

from app.modules.superadmin.locations.superadmin_location_repository import (
    SuperAdminLocationRepository
)


class SuperAdminLocationService:

 # =========================
# GET LOCATION ANALYTICS
# =========================
  @staticmethod
  async def get_location_analytics(
    db: AsyncSession
):

    locations = await (
        SuperAdminLocationRepository
        .get_location_analytics(db)
    )

    if locations is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Location analytics not found."
        )

    return success_response(
        "Location analytics fetched successfully",
        {
            "locations": locations
        }
    ) 