from pydantic_settings import BaseSettings


class Settings(BaseSettings):

    # ========================
    # DATABASE
    # ========================
    DB_HOST: str
    DB_PORT: int
    DB_USER: str
    DB_PASSWORD: str
    DB_NAME: str

    # ========================
    # SECURITY
    # ========================
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int

    # ========================
    # DEFAULT ADMIN
    # ========================
    DEFAULT_ADMIN_NAME: str
    DEFAULT_ADMIN_EMAIL: str
    DEFAULT_ADMIN_PASSWORD: str
    DEFAULT_ADMIN_ROLE: str

    # ========================
    # AWS S3
    # ========================
    AWS_ACCESS_KEY_ID: str
    AWS_SECRET_ACCESS_KEY: str
    AWS_REGION: str
    AWS_S3_BUCKET_NAME: str

    # ========================
    # FRONTEND
    # ========================
    FRONTEND_URL: str

    class Config:
        env_file = ".env"


settings = Settings()