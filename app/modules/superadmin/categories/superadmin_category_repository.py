from sqlalchemy import (
    select,
    func
)

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.models import (
    Category,
    News
)


# =========================
# CREATE CATEGORY
# =========================
async def create_category(
    db: AsyncSession,
    name: str,
    description: str,
    image_url: str | None = None
):

    category = Category(
        name=name,
        description=description,
        image_url=image_url
    )

    db.add(category)

    await db.commit()

    await db.refresh(category)

    return category


# =========================
# GET CATEGORY BY NAME
# =========================
async def get_category_by_name(
    db: AsyncSession,
    name: str
):

    result = await db.execute(
        select(Category).where(
            Category.name == name
        )
    )

    return result.scalar_one_or_none()


# =========================
# GET CATEGORY BY ID
# =========================
async def get_category_by_id(
    db: AsyncSession,
    category_id: int
):

    result = await db.execute(
        select(Category).where(
            Category.category_id == category_id
        )
    )

    return result.scalar_one_or_none()


# =========================
# GET ALL CATEGORIES
# =========================
async def get_all_categories(
    db: AsyncSession
):

    total_news_result = await db.execute(
        select(
            func.count(
                News.news_id
            )
        )
    )

    total_news = (
        total_news_result.scalar() or 0
    )

    result = await db.execute(
        select(
            Category.category_id,
            Category.name,
            Category.description,
            Category.image_url,
            func.count(
                News.news_id
            ).label("total_posts")
        )
        .outerjoin(
            News,
            News.category_id ==
            Category.category_id
        )
        .group_by(
            Category.category_id,
            Category.name,
            Category.description,
            Category.image_url
        )
        .order_by(
            Category.category_id
        )
    )

    categories = result.all()

    response = []

    for index, category in enumerate(
        categories,
        start=1
    ):

        share_percentage = 0

        if total_news > 0:

            share_percentage = round(
                (
                    category.total_posts /
                    total_news
                ) * 100,
                1
            )

        response.append(
            {
                "category_id":
                    category.category_id,

                "category_number":
                    f"#{index:02d}",

                "category_name":
                    category.name,

                "description":
                    category.description,

                "image_url":
                    category.image_url,

                "total_posts":
                    category.total_posts,

                "share_percentage":
                    share_percentage,

                "growth_percentage":
                    0
            }
        )

    return response


# =========================
# DELETE CATEGORY
# =========================
async def delete_category(
    db: AsyncSession,
    category: Category
):

    await db.delete(category)

    await db.commit()
    # =========================
