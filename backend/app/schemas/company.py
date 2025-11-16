"""
Company Pydantic schemas for request/response validation
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from decimal import Decimal


class CompanyBase(BaseModel):
    """Base company schema"""
    ticker: str = Field(..., max_length=10)
    name: str = Field(..., max_length=255)
    sector: Optional[str] = Field(None, max_length=100)
    industry: Optional[str] = Field(None, max_length=100)
    market_cap: Optional[Decimal] = None
    employees: Optional[int] = None
    founded_year: Optional[int] = None
    headquarters: Optional[str] = Field(None, max_length=255)
    website: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    sic_code: Optional[str] = Field(None, max_length=10)
    cik: Optional[str] = Field(None, max_length=10)
    exchange: Optional[str] = Field(None, max_length=20)


class CompanyCreate(CompanyBase):
    """Schema for creating a new company"""
    pass


class CompanyUpdate(BaseModel):
    """Schema for updating company information"""
    name: Optional[str] = Field(None, max_length=255)
    sector: Optional[str] = Field(None, max_length=100)
    industry: Optional[str] = Field(None, max_length=100)
    market_cap: Optional[Decimal] = None
    employees: Optional[int] = None
    headquarters: Optional[str] = Field(None, max_length=255)
    website: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None


class CompanyInDB(CompanyBase):
    """Company schema as stored in database"""
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CompanyResponse(CompanyInDB):
    """Company schema for API responses"""
    pass


class CompanySearch(BaseModel):
    """Schema for company search results"""
    ticker: str
    name: str
    sector: Optional[str] = None
    exchange: Optional[str] = None
    market_cap: Optional[Decimal] = None

    class Config:
        from_attributes = True
