from pydantic import BaseModel, validator
from typing import Optional, List
from datetime import date as date_type
from enum import Enum

class TransactionType(str, Enum):
    INCOME = "income"
    EXPENSE = "expense"

class TransactionCreate(BaseModel):
    date: date_type
    amount: float
    description: str
    type: TransactionType
    category: Optional[str] = None
    
    @validator('amount')
    def amount_positive(cls, v):
        if v <= 0:
            raise ValueError('Amount must be positive')
        return v
    
    @validator('description')
    def description_not_empty(cls, v):
        if not v.strip():
            raise ValueError('Description cannot be empty')
        return v.strip()

class TransactionResponse(BaseModel):
    id: int
    date: date_type
    amount: float
    description: str
    type: TransactionType
    category: str
    created_at: str
    
    class Config:
        from_attributes = True

class TransactionUpdate(BaseModel):
    date: Optional[date_type] = None
    amount: Optional[float] = None
    description: Optional[str] = None
    category: Optional[str] = None

class BulkTransactionCreate(BaseModel):
    transactions: List[TransactionCreate]