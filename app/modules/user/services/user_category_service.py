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

        data = [
            {
                "category_id": category.category_id,
                "name": category.name,
                "description": category.description
            }
            for category in categories
        ]

        return success_response(
            message="Categories fetched successfully",
            data=data
        )