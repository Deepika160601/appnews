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

        try:

            locations = await (
                SuperAdminLocationRepository
                .get_location_analytics(db)
            )

            return success_response(
                "Location analytics fetched successfully",
                {
                    "locations": locations
                }
            )

        except Exception as e:

            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to fetch location analytics: {str(e)}"
            )