"""Generic APIResponse wrapper and common schemas."""
from typing import TypeVar, Generic, Optional, Any
from pydantic import BaseModel

T = TypeVar("T")


class APIResponse(BaseModel, Generic[T]):
    success: bool = True
    data: Optional[T] = None
    message: Optional[str] = None
    error: Optional[Any] = None

    @classmethod
    def ok(cls, data: T = None, message: str = None) -> "APIResponse[T]":
        return cls(success=True, data=data, message=message)

    @classmethod
    def fail(cls, message: str, error: Any = None) -> "APIResponse":
        return cls(success=False, data=None, message=message, error=error)


class ErrorDetail(BaseModel):
    code: str
    details: Any = None
