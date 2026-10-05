from pydantic import BaseModel
from datetime import datetime
from typing import Optional

# Template for creating a new ticket
class TicketCreate(BaseModel):
    subject: str
    body: str

# Complete response schema (including AI-generated data and ID)
class TicketResponse(BaseModel):
    id: int
    subject: str
    body: str
    urgency: str
    category: str
    suggested_reply: Optional[str] = None
    status: str
    created_at: datetime

    class Config:
        from_attributes = True