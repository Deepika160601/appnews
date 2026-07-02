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

from app.modules.admin.repositories.category_repository import (
    get_all_categories,
)


# =========================
# GET ALL CATEGORIES
# =========================
async def get_all_categories_service(
    db: AsyncSession
):
    try:

        # -------------------------
        # Get Categories
        # -------------------------
        categories = await get_all_categories(
            db
        )

        if categories is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Categories not found."
            )

        return success_response(
            "Categories fetched successfully",
            categories
        )

    except HTTPException:
        raise

    except SQLAlchemyError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred while fetching categories."
        )

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while fetching categories."
        )