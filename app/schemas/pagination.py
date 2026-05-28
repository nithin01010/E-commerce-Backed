from pydantic import  BaseModel
from typing import Generic, TypeVar, List, Optional

T = TypeVar('T')

class PaginatedResponse(BaseModel, Generic[T]):
    items: List[T]
    next_cursor: Optional[int] = None