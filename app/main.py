from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware

from fastapi import FastAPI
from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse

from app.db.db import (
    engine,
    AsyncSessionLocal
)

from app.models.models import Base

from app.core.admin_initializer import (
    create_default_superadmin
)

# ========================
# STARTUP
# ========================
@asynccontextmanager
async def lifespan(app: FastAPI):

    # Create Tables
    async with engine.begin() as conn:

        await conn.run_sync(
            Base.metadata.create_all
        )

    # Create Default Super Admin
    async with AsyncSessionLocal() as db:

        await create_default_superadmin(
            db
        )

    yield


# ========================
# FASTAPI APP
# ========================
app = FastAPI(
    title="News API",
    description="Backend for News Application",
    version="1.0.0",
    lifespan=lifespan
)

# ========================
# CORS MIDDLEWARE
# ========================
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ========================
# GLOBAL HTTP EXCEPTION HANDLER
# ========================
@app.exception_handler(HTTPException)
async def http_exception_handler(
    request: Request,
    exc: HTTPException
):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "message": exc.detail,
            "data": None
        }
    )


# ========================
# SUPER ADMIN ROUTERS
# ========================
from app.modules.superadmin.auth.superadmin_router import (
    router as superadmin_router
)

# ========================
# ADMIN ROUTERS
# ========================
from app.modules.admin.auth.admin_router import (
    router as admin_router
)

from app.modules.admin.routers.dashboard_router import (
    router as dashboard_router
)

from app.modules.admin.routers.category_router import (
    router as category_router
)

from app.modules.admin.routers.news_admin_router import (
    router as admin_news_router
)

# ========================
# USER ROUTERS
# ========================
from app.modules.user.routers.user_router import (
    router as user_router
)

from app.modules.user.routers.news_router import (
    router as user_news_router
)

from app.modules.user.routers.comment_router import (
    router as comment_router
)

from app.modules.user.routers.like_router import (
    router as like_router
)

from app.modules.user.routers.bookmark_router import (
    router as bookmark_router
)

from app.modules.user.routers.notification_router import (
    router as notification_router
)

from app.modules.user.routers.search_router import (
    router as search_router
)


# ========================
# SUPER ADMIN ROUTES
# ========================
app.include_router(
    superadmin_router,
    prefix="/superadmin/auth",
    tags=["Super Admin"]
)

# ========================
# ADMIN ROUTES
# ========================
app.include_router(
    admin_router,
    prefix="/admin/auth",
    tags=["Admin Authentication"]
)

app.include_router(
    dashboard_router,
    prefix="/admin/dashboard",
    tags=["Admin Dashboard"]
)

app.include_router(
    category_router,
    prefix="/admin/categories",
    tags=["Admin Categories"]
)

app.include_router(
    admin_news_router,
    prefix="/admin/news",
    tags=["Admin News"]
)

# ========================
# USER ROUTES
# ========================
app.include_router(
    user_router,
    prefix="/auth",
    tags=["User Authentication"]
)

app.include_router(
    user_news_router,
    prefix="/news",
    tags=["News"]
)

app.include_router(
    comment_router,
    prefix="/comments",
    tags=["Comments"]
)

app.include_router(
    like_router,
    prefix="/likes",
    tags=["Likes"]
)

app.include_router(
    bookmark_router,
    prefix="/bookmarks",
    tags=["Bookmarks"]
)

app.include_router(
    notification_router,
    prefix="/notifications",
    tags=["Notifications"]
)

app.include_router(
    search_router,
    prefix="/search",
    tags=["Search"]
)

# ========================
# ROOT
# ========================
@app.get("/")
async def root():

    return {
        "message": "News API is running"
    }