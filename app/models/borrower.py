"""
Models for borrowers and loan payments
"""
from sqlmodel import SQLModel, Field, Relationship
from datetime import date, datetime
from typing import Optional, List


class Borrower(SQLModel, table=True):
    """Represents a person who has borrowed money"""
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    principal: float = Field(gt=0)
    interest_rate: float = Field(gt=0)  # Monthly interest rate as percentage
    start_date: date
    principal_recovered: bool = Field(default=False)
    is_defaulted: bool = Field(default=False)
    defaulted_on: Optional[date] = None
    default_note: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)
    
    # Relationships
    payments: List["Payment"] = Relationship(back_populates="borrower", cascade_delete=True)
    principal_changes: List["PrincipalChange"] = Relationship(back_populates="borrower", cascade_delete=True)


class Payment(SQLModel, table=True):
    """Represents an interest payment made by a borrower"""
    id: Optional[int] = Field(default=None, primary_key=True)
    borrower_id: int = Field(foreign_key="borrower.id", ondelete="CASCADE")
    amount: float = Field(gt=0)
    payment_date: date
    note: Optional[str] = None
    is_custom: bool = Field(default=False)  # True if custom amount, not standard interest
    created_at: datetime = Field(default_factory=datetime.now)
    
    # Relationship
    borrower: Optional[Borrower] = Relationship(back_populates="payments")


class PrincipalChange(SQLModel, table=True):
    """Tracks changes to principal amount and corresponding interest rate changes"""
    id: Optional[int] = Field(default=None, primary_key=True)
    borrower_id: int = Field(foreign_key="borrower.id", ondelete="CASCADE")
    old_principal: float = Field(gt=0)
    new_principal: float = Field(gt=0)
    old_interest_rate: float = Field(gt=0)
    new_interest_rate: float = Field(gt=0)
    effective_date: date
    note: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)
    
    # Relationship
    borrower: Optional[Borrower] = Relationship(back_populates="principal_changes")
