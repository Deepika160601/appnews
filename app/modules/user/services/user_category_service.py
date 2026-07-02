from fastapi import (
    HTTPException,
    status
)

from sqlalchemy.ext.asyncio import AsyncSession

from app.utils.api_response import success_response

from app.modules.user.repositories.user_category_repository import (
    UserCategoryRepository
)


class UserCategoryService:

    @staticmethod
    async def get_categories(
        db: AsyncSession
    ):

        categories = await (
            UserCategoryRepository
            .get_categories(db)
        )

        if not categories:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No categories found."
            )

        data = [
            {
                "category_id": category.category_id,
                "name": category.name,
                "description": category.description,
                "image_url": category.image_url
            }
            for category in categories
        ]

        return success_response(
            message="Categories fetched successfully",
            data=data
        )