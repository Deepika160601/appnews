from pydantic import (
    BaseModel,
    EmailStr
)


class SuperAdminLoginRequest(
    BaseModel
):
    email: EmailStr
    password: str