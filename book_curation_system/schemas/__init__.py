# schemas/__init__.py
from .book import (
    BookBase,
    BookCreate,
    BookUpdate,
    BookResponse,
    VoteRequest,
    HealthResponse
)

__all__ = [
    "BookBase",
    "BookCreate",
    "BookUpdate",
    "BookResponse",
    "VoteRequest",
    "HealthResponse"
]