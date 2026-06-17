from pydantic import BaseModel
from typing import Optional


from pydantic import BaseModel
from typing import Optional


# =========================
# CREATE NEWS REQUEST
# =========================
class NewsCreateRequest(BaseModel):

    title: str

    content: str

    summary: Optional[str] = None

    original_language: str = "en"

    category_id: int

    news_type: str
    country: str

    state: Optional[str] = None

    district: Optional[str] = None

    mandal: Optional[str] = None

    city: Optional[str] = None

    village: Optional[str] = None

    is_breaking: bool = False

    thumbnail_url: Optional[str] = None

    video_url: Optional[str] = None


# =========================
# NEWS RESPONSE
# =========================
class NewsResponse(BaseModel):

    news_id: int

    title: str

    content: str

    summary: Optional[str]

    category_id: int

    news_type: str
    country: str

    state: Optional[str]

    district: Optional[str]

    mandal: Optional[str]

    city: Optional[str]

    village: Optional[str]

    author_id: int

    status: str

    is_breaking: bool

    view_count: int

    like_count: int

    comment_count: int

    thumbnail_url: Optional[str]

    video_url: Optional[str]

    class Config:
        from_attributes = True


# =========================
# APPROVE NEWS REQUEST
# =========================
class ApproveNewsRequest(BaseModel):

    admin_id: int


# =========================
# REJECT NEWS REQUEST
# =========================
class RejectNewsRequest(BaseModel):

    admin_id: int

    rejection_reason: str
# =========================
# APPROVE NEWS REQUEST
# =========================
class ApproveNewsRequest(BaseModel):

    admin_id: int


# =========================
# REJECT NEWS REQUEST
# =========================
class RejectNewsRequest(BaseModel):

    admin_id: int

    rejection_reason: str