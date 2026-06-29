from pydantic import BaseModel, ConfigDict


# =========================
# CREATE CATEGORY REQUEST
# =========================
class CategoryCreateRequest(BaseModel):
    name: str
    description: str


# =========================
# CATEGORY RESPONSE
# =========================
class CategoryResponse(BaseModel):
    category_id: int
    name: str
    description: str
    image_url: str | None = None

    model_config = ConfigDict(from_attributes=True)