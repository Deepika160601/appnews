

from fastapi import (
    APIRouter,
    Depends
)

from sqlalchemy.ext.asyncio import (
    AsyncSession
)

from app.db.db import get_db

from app.core.security import (
    get_current_user,
    get_current_admin_or_user
)

from app.modules.admin.auth.admin_service import (
    AdminService
)

from app.modules.user.schemas.user_schema import (
    UserRegisterRequest,
    UserLoginRequest,
    LanguageUpdateRequest,
    LocationUpdateRequest
)

from app.modules.user.services.user_service import (
    UserService
)

router = APIRouter()


# =========================
# REGISTER USER
# =========================
@router.post("/register")
async def register_user(
    request: UserRegisterRequest,
    db: AsyncSession = Depends(get_db)
):

    return await UserService.register_user(
        db=db,
        name=request.name,
        email=request.email,
        mobile_number=request.mobile_number,
        password=request.password,
        latitude=request.latitude,
        longitude=request.longitude
    )


# =========================
# LOGIN USER
# =========================
@router.post("/login")
async def login_user(
    request: UserLoginRequest,
    db: AsyncSession = Depends(get_db)
):

    return await UserService.login_user(
        db=db,
        email=request.email,
        password=request.password
    )
#---------------GET PROFILE------------------
@router.get("/profile")
async def get_profile(
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_admin_or_user)
):

    role = current_user.get("role")

    if role == "user":
        return await UserService.get_profile(
            db,
            current_user["user_id"]
        )

    return await AdminService.get_profile(
        db,
        current_user["admin_id"]
    )
# =========================
# UPDATE LANGUAGE
# =========================
@router.put("/language")
async def update_language(
    request: LanguageUpdateRequest,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_admin_or_user)
):

    role = current_user.get("role")

    if role == "user":
        return await UserService.update_language(
            db,
            current_user["user_id"],
            request.preferred_language
        )

    return await AdminService.update_language(
        db,
        current_user["admin_id"],
        request.preferred_language
    )


# =========================
# UPDATE LOCATION
# =========================
@router.put("/location")
async def update_location(
    request: LocationUpdateRequest,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_admin_or_user)
):

    role = current_user.get("role")

    if role == "user":
        return await UserService.update_location(
            db,
            current_user["user_id"],
            request.state,
            request.district,
            request.mandal
        )

    return await AdminService.update_location(
        db,
        current_user["admin_id"],
        request.state,
        request.district,
        request.mandal
    )