from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncSession,
    async_sessionmaker
)

from sqlalchemy.orm import declarative_base

from app.core.config import settings

# ========================
# DATABASE URL (MYSQL)
# ========================
DATABASE_URL = (
    f"mysql+aiomysql://"
    f"{settings.DB_USER}:"
    f"{settings.DB_PASSWORD}@"
    f"{settings.DB_HOST}:"
    f"{settings.DB_PORT}/"
    f"{settings.DB_NAME}"
)

# ========================
# ENGINE
# ========================
engine = create_async_engine(
    DATABASE_URL,
    echo=True,
    pool_pre_ping=True,
    pool_recycle=3600,
)

# ========================
# SESSION
# ========================
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# ========================
# BASE
# ========================
Base = declarative_base()

# ========================
# DB DEPENDENCY
# ========================
async def get_db():

    async with AsyncSessionLocal() as db:

        try:
            yield db

        except Exception:
            await db.rollback()
            raise

        finally:
            await db.close()