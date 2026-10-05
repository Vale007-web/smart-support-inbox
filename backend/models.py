import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime
from database import Base

class Ticket(Base):
    __tablename__ = "tickets"

    id = Column(Integer, primary_key=True, index=True)
    subject = Column(String(255), nullable=False)
    body = Column(Text, nullable=False)
    urgency = Column(String(50), default="NON ANALIZZATO")  # HIGH, MEDIUM, LOW
    category = Column(String(100), default="Generale")
    suggested_reply = Column(Text, nullable=True)
    status = Column(String(50), default="Aperto")           # Open, In Progress, Closed
    created_at = Column(DateTime, default=datetime.datetime.utcnow)