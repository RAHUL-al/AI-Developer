from pydantic import BaseModel, Field
from typing import Optional

class Product(BaseModel):
    id: int
    title: str
    color: str = ""
    size: list[str] = []
    tags: list[str] = []

class RecommendRequest(BaseModel):
    query: str
    products: list[Product]

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
    recommendations: list[RecommendedProduct]
    total_products: int
    response_time_seconds: float
