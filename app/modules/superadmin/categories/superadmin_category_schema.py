from pydantic import BaseModel


class CategoryCreateRequest(BaseModel):
    name: str
    description: str