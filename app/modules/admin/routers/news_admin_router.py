
from fastapi import (
    APIRouter,
    Depends,
    Form,
    UploadFile,
    File
)

from sqlalchemy.ext.asyncio import (
    AsyncSession
)

from app.db.db import get_db

from app.core.security import (
    get_current_admin
)

from app.modules.admin.schemas.news_admin_schema import (
    NewsCreateRequest
)

from app.modules.admin.services.news_admin_service import (
    create_news_service,
    get_all_news_service,
    publish_news_service,
    delete_news_service,
    get_news_by_id_service
)

router = APIRouter(
    dependencies=[Depends(get_current_admin)]
)


# =========================
# CREATE NEWS
# =========================
@router.post("/")
async def add_news(
    title: str = Form(...),
    content: str = Form(...),
    summary: str = Form(None),

    original_language: str = Form("en"),

    category_id: int = Form(...),

    news_type: str = Form(...),
    country: str = Form(...),

    state: str = Form(None),
    district: str = Form(None),
    mandal: str = Form(None),
    city: str = Form(None),
    village: str = Form(None),

    is_breaking: bool = Form(False),

    thumbnail: UploadFile = File(...),

    video: UploadFile = File(None),

    db: AsyncSession = Depends(get_db),

    current_admin=Depends(get_current_admin)
):

    data = NewsCreateRequest(
        title=title,
        content=content,
        summary=summary,

        original_language=original_language,

        category_id=category_id,

        news_type=news_type,
        country=country,

        state=state,
        district=district,
        mandal=mandal,
        city=city,
        village=village,

        is_breaking=is_breaking
    )

    return await create_news_service(
        db=db,
        data=data,
        admin_id=current_admin["admin_id"],
        thumbnail=thumbnail,
        video=video
    )


# =========================
# GET ALL NEWS
# =========================
@router.get("/")
async def list_news(
    db: AsyncSession = Depends(get_db)
):

    return await get_all_news_service(
        db
    )


# =========================
# GET NEWS BY ID
# =========================
@router.get("/{news_id}")
async def get_news(
    news_id: int,
    db: AsyncSession = Depends(get_db)
):

    return await get_news_by_id_service(
        db,
        news_id
    )


# =========================
# PUBLISH NEWS
# =========================
@router.put("/publish/{news_id}")
async def publish_news(
    news_id: int,
    db: AsyncSession = Depends(get_db)
):

    return await publish_news_service(
        db,
        news_id
    )


# =========================
# DELETE NEWS
# =========================
@router.delete("/{news_id}")
async def remove_news(
    news_id: int,
    db: AsyncSession = Depends(get_db)
):

    return await delete_news_service(
        db,
        news_id
    )

