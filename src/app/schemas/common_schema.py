from pydantic import BaseModel
from typing import Generic, TypeVar, List

T = TypeVar("T")

class ApiResponseDTO(BaseModel, Generic[T]):
    success: bool
    message: str
    data: T | None = None

#     return {
#     "total_count": total_count,
#     "total_pages": total_pages,
#     "offset": current_page,
#     "limit": limit,
#     "items": items_dto
# }

class PageResponseDTO(BaseModel, Generic[T]):
    total_count: int
    total_page: int
    offset: int
    limit: int
    items: List[T] | None = None