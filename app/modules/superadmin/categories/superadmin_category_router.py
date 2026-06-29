from fastapi import (
    APIRouter,
    Depends,
    UploadFile,
    File,
    Form
)

from sqlalchemy.ext.asyncio import (
    AsyncSession
)

from app.db.db import get_db

from app.core.security import (
    get_current_superadmin
)

from app.modules.superadmin.categories.superadmin_category_service import (
    create_category_service,
    get_all_categories_service,
    delete_category_service
    
)

router = APIRouter(
    prefix="/categories",
    tags=["Super Admin Categories"],
    dependencies=[Depends(get_current_superadmin)]
)


# =========================
# CREATE CATEGORY
# =========================
@router.post("/")
async def create_category(
    name: str = Form(...),
    description: str = Form(...),
    image: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):

    return await create_category_service(
        db=db,
        name=name,
        description=description,
        image=image
    )


# =========================
# GET ALL CATEGORIES
# =========================
@router.get("/")
async def get_categories(
    db: AsyncSession = Depends(get_db)
):

    return await get_all_categories_service(
        db
    )
# =========================
# DELETE CATEGORY
# =========================
@router.delete("/{category_id}")
async def delete_category(
    category_id: int,
    db: AsyncSession = Depends(get_db)
):

    return await delete_category_service(
        db,
        category_id
    )