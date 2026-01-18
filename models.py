from pydantic import BaseModel, Field
from typing import Optional, List

class Product(BaseModel):
    id: int
    title: str
    color: str = ""
    size: list[str] = []
    tags: list[str] = []

class RecommendRequest(BaseModel):
    query: str
    products: Optional[List[Product]] = None  # Optional - if not provided, searches stored products

class RecommendedProduct(BaseModel):
    id: int
    title: str
    color: str
    size: list[str]
    tags: list[str]
    score: float
    explanation: str

class RecommendResponse(BaseModel):
    query: str
    found: bool  # Whether exact matches were found
    message: str  # Descriptive message about the search results
    recommendations: list[RecommendedProduct]
    total_products: int
    response_time_seconds: float
