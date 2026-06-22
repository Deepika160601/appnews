from fastapi import (
    HTTPException,
    status
)

from sqlalchemy.ext.asyncio import (
    AsyncSession
)

from app.utils.api_response import success_response

from app.modules.admin.repositories.category_repository import (

    get_all_categories,

)
# =========================
# GET ALL CATEGORIES
# =========================
async def get_all_categories_service(
    db: AsyncSession
):

    categories = await get_all_categories(
        db
    )

    return success_response(
        "Categories fetched successfully",
        categories
    )


#