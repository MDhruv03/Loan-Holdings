from sqlmodel import SQLModel, Field, Relationship
from datetime import date, datetime
from typing import Optional, List

class Borrower(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    principal: float = Field(gt=0)
    interest_rate: float = Field(gt=0)  # Monthly interest rate as percentage
    start_date: date
    principal_recovered: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.now)
    
    # Relationship
    payments: List["Payment"] = Relationship(back_populates="borrower")

class Payment(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    borrower_id: int = Field(foreign_key="borrower.id")
    amount: float = Field(gt=0)
    payment_date: date
    created_at: datetime = Field(default_factory=datetime.now)
    
    # Relationship
    borrower: Optional[Borrower] = Relationship(back_populates="payments")

class Holder(SQLModel,table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    currency: str = Field(default="INR")  # Default currency is Indian Rupee
    phone: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)
    
    # Relationship
    holdings: List["Holding"] = Relationship(back_populates="holder")


class Holding(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    holder_id: int = Field(foreign_key="holder.id")
    amount: float = Field(gt=0)
    type: str  # deposti or transfer
    direction : str # credit green and debit red
    created_at: datetime = Field(default_factory=datetime.now)
    
    # Relationship
    holder: Optional[Holder] = Relationship(back_populates="holdings")