from datetime import datetime
from typing import Generic, Optional, TypeVar

from pydantic import BaseModel, Field

DataT = TypeVar("DataT")


class ApiResponse(BaseModel, Generic[DataT]):
    success: bool = True
    message: str = ""
    data: Optional[DataT] = None
    errors: Optional[list[str]] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        from_attributes = True