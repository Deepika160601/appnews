from fastapi import (
    HTTPException,
    UploadFile,
    status
)

from sqlalchemy import (
    select,
    func
)

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.models import (
    News
)

from app.utils.api_response import (
    success_response
)

from app.utils.s3_helper import (
    upload_category_image_to_s3
)

from app.modules.superadmin.categories.superadmin_category_repository import (
    create_category,
    get_category_by_name,
    get_category_by_id,
    get_all_categories,
    delete_category
    
)
# =========================
# CREATE CATEGORY
# =========================
async def create_category_service(
    db: AsyncSession,
    name: str,
    description: str,
    image: UploadFile | None = None
):

    try:

        existing_category = await get_category_by_name(
            db,
            name
        )

        if existing_category:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Category already exists"
            )

        image_url = None

        if image:
            image_url = await upload_category_image_to_s3(
                image
            )

        category = await create_category(
            db=db,
            name=name,
            description=description,
            image_url=image_url
        )

        return success_response(
            "Category created successfully",
            {
                "category_id": category.category_id,
                "name": category.name,
                "description": category.description,
                "image_url": category.image_url
            }
        )

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


# =========================
# GET ALL CATEGORIES
# =========================
async def get_all_categories_service(
    db: AsyncSession
):

    try:

        categories = await get_all_categories(
            db
        )

        if not categories:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No categories found"
            )

        return success_response(
            "Categories fetched successfully",
            categories
        )

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
# =========================
# DELETE CATEGORY
# =========================
async def delete_category_service(
    db: AsyncSession,
    category_id: int
):

    try:

        category = await get_category_by_id(
            db,
            category_id
        )

        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found"
            )

        news_count_result = await db.execute(
            select(
                func.count(
                    News.news_id
                )
            ).where(
                News.category_id == category_id
            )
        )

        news_count = (
            news_count_result.scalar() or 0
        )

        if news_count > 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete category. News exists under this category."
            )

        await delete_category(
            db,
            category
        )

        return success_response(
            "Category deleted successfully",
            {
                "category_id": category_id
            }
        )

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )