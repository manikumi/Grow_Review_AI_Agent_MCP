from datetime import date
from typing import Optional

from pydantic import BaseModel


class Review(BaseModel):
    id: str          # SHA-256 of review text (no PII key)
    rating: int      # 1-5
    date: date
    text: str
    title: Optional[str] = None
