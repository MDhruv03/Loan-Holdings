"""
Models for holdings and transfers
"""
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from typing import Optional, List


class Holder(SQLModel, table=True):
    """Represents a person who holds money or has holdings"""
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    currency: str = Field(default="INR")  # INR, THB, RMB
    phone: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)
    
    # Relationship
    holdings: List["Holding"] = Relationship(back_populates="holder", cascade_delete=True)


class Holding(SQLModel, table=True):
    """Represents a transaction in a holder's account"""
    id: Optional[int] = Field(default=None, primary_key=True)
    holder_id: int = Field(foreign_key="holder.id", ondelete="CASCADE")
    amount: float
    transaction_type: str  # "deposit", "transfer_in", "transfer_out", "withdrawal"
    related_holder_id: Optional[int] = None  # For transfers, ID of the other party
    note: Optional[str] = None
    transaction_date: datetime = Field(default_factory=datetime.now)
    created_at: datetime = Field(default_factory=datetime.now)
    
    # Relationship
    holder: Optional[Holder] = Relationship(back_populates="holdings")
