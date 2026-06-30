from pydantic import (
    BaseModel,
    EmailStr
)
from typing import (
    Literal,
    Optional
)


class SuperAdminLoginRequest(
    BaseModel
):
    email: EmailStr
    password: str
# =========================
# ADMIN REQUEST ACTION
# =========================
class AdminRequestActionRequest(
    BaseModel
):
    status: Literal[
        "Approved",
        "Rejected"
    ]

    rejection_reason: Optional[str] = None