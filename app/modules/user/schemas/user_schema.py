from pydantic import (
    BaseModel,
    EmailStr,
    field_validator
)

from typing import (
    Literal,
    Optional
)
# =========================
# REGISTER
# =========================
class UserRegisterRequest(BaseModel):
    name: str
    email: EmailStr
    mobile_number: str
    password: str

    latitude: Optional[float] = None
    longitude: Optional[float] = None

    @field_validator("mobile_number")
    @classmethod
    def validate_mobile_number(
        cls,
        value: str
    ):

        if not value.isdigit():
            raise ValueError(
                "Mobile number must contain only digits"
            )

        if len(value) != 10:
            raise ValueError(
                "Mobile number must be exactly 10 digits"
            )

        return value


# =========================
# LOGIN
# =========================
class UserLoginRequest(BaseModel):
    email: EmailStr
    password: str


# =========================
# TOKEN RESPONSE
# =========================
class TokenResponse(BaseModel):
    access_token: str
    token_type: str


# =========================
# USER RESPONSE
# =========================
class UserResponse(BaseModel):
    user_id: int
    name: str
    email: str
    mobile_number: str
    preferred_language: str

    class Config:
        from_attributes = True


# =========================
# UPDATE LANGUAGE
# =========================
class LanguageUpdateRequest(BaseModel):
    preferred_language: Literal[
        "en",
        "te",
        "hi",
        "ta",
        "kn"
    ]


# =========================
# UPDATE LOCATION
# =========================
class LocationUpdateRequest(BaseModel):
    state: str
    district: str
    mandal: str


    # =========================
# BECOME ADMIN REQUEST
# =========================
class AdminRequestCreate(BaseModel):
    reason: str
    government_id_type: Literal[
        "Aadhaar",
        "PAN",
        "Driving License",
        "Passport",
        "Voter ID"
    ]

    address: Optional[str] = None
    experience: Optional[str] = None


# =========================
# REJECT ADMIN REQUEST
# =========================
class RejectAdminRequest(BaseModel):
    rejection_reason: str