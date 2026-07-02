from fastapi import (
    HTTPException,
    status
)

from sqlalchemy.ext.asyncio import (
    AsyncSession
)

from sqlalchemy.exc import (
    SQLAlchemyError
)

from app.utils.api_response import (
    success_response
)

from app.modules.admin.repositories.dashboard_repository import (
    DashboardRepository
)


class DashboardService:

    @staticmethod
    async def get_dashboard(
        db: AsyncSession
    ):
        try:

            dashboard_stats = await DashboardRepository.get_dashboard_stats(
                db
            )

            if dashboard_stats is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Dashboard data not found."
                )

            return success_response(
                "Dashboard data fetched successfully",
                dashboard_stats
            )

        except HTTPException:
            raise

        except SQLAlchemyError:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error occurred while fetching dashboard data."
            )

        except Exception:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An unexpected error occurred while fetching dashboard data."
            )