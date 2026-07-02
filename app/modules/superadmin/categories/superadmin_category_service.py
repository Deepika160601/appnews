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

    # -------------------------
    # Validate Category Name
    # -------------------------
    if not name or not name.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Category name is required."
        )

    name = name.strip()

    if len(name) < 3:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Category name must contain at least 3 characters."
        )

    if len(name) > 100:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Category name must not exceed 100 characters."
        )

    # -------------------------
    # Validate Description
    # -------------------------
    if not description or not description.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Category description is required."
        )

    description = description.strip()

    if len(description) < 5:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Category description must contain at least 5 characters."
        )

    # -------------------------
    # Check Duplicate Category
    # -------------------------
    existing_category = await get_category_by_name(
        db,
        name
    )

    if existing_category:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Category already exists."
        )

    # -------------------------
    # Validate Image
    # -------------------------
    image_url = None

    if image:

        allowed_extensions = (
            ".jpg",
            ".jpeg",
            ".png",
            ".webp"
        )

        if not image.filename.lower().endswith(
            allowed_extensions
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only JPG, JPEG, PNG and WEBP images are allowed."
            )

        image_url = await upload_category_image_to_s3(
            image
        )

    # -------------------------
    # Create Category
    # -------------------------
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

## =========================
# GET ALL CATEGORIES
# =========================
async def get_all_categories_service(
    db: AsyncSession
):

    categories = await get_all_categories(
        db
    )

    if not categories:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No categories found."
        )

    return success_response(
        "Categories fetched successfully",
        categories
    )
## =========================
# DELETE CATEGORY
# =========================
async def delete_category_service(
    db: AsyncSession,
    category_id: int
):

    # -------------------------
    # Validate Category ID
    # -------------------------
    if category_id <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid category ID."
        )

    # -------------------------
    # Check Category
    # -------------------------
    category = await get_category_by_id(
        db,
        category_id
    )

    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found."
        )

    # -------------------------
    # Check Existing News
    # -------------------------
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
            detail="Cannot delete category because news exists under this category."
        )

    # -------------------------
    # Delete Category
    # -------------------------
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