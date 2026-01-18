from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from similarity import rank_products
from models import RecommendRequest, RecommendResponse
from vector_store import get_vector_store
import time

app = FastAPI(
    title="Smart Search API",
    description="AI-powered product recommendation service using semantic search",
    version="2.0.0"
)

class SearchQuery(BaseModel):
    query: str

@app.get("/")
async def home():
    """Health check endpoint - returns API status and product count."""
    store = get_vector_store()
    return {
        "status": "ok",
        "message": "Smart Search API is running",
        "products_loaded": len(store.products),
        "endpoints": {
            "search": "POST /search - Search for products by query",
            "recommend": "POST /recommend - Get product recommendations",
            "docs": "GET /docs - API documentation"
        }
    }

@app.post("/search")
async def search(req: SearchQuery):
    """
    Search for products based on a natural language query.
    
    Examples:
    - "red party dress"
    - "blue jacket size L"
    - "formal office wear"
    - "summer beach dress"
    
    Returns top 3 matching products with explanations.
    If no exact match found, suggests alternatives.
    """
    start = time.time()
    store = get_vector_store()
    
    if store.is_empty():
        raise HTTPException(
            status_code=400, 
            detail="No products in database. Run: python init_data.py"
        )
    
    result = rank_products(req.query)
    
    return {
        "query": req.query,
        "found": result["found"],
        "message": result["message"],
        "recommendations": result["recommendations"],
        "total_products_in_store": len(store.products),
        "response_time_seconds": round(time.time() - start, 3)
    }

@app.post("/recommend", response_model=RecommendResponse)
async def recommend(req: RecommendRequest):
    """
    Get product recommendations.
    
    - If 'products' list is provided: searches within that list
    - If 'products' is not provided: searches the stored product database
    
    Returns top 3 recommendations with explanations.
    """
    start = time.time()
    store = get_vector_store()
    
    # Determine which products to search
    if req.products:
        # Use provided products (temporary search)
        result = rank_products(req.query, req.products)
        total = len(req.products)
    else:
        # Use stored products
        if store.is_empty():
            raise HTTPException(
                status_code=400, 
                detail="No products in database and none provided. Run: python init_data.py"
            )
        result = rank_products(req.query)
        total = len(store.products)
    
    return RecommendResponse(
        query=req.query,
        found=result["found"],
        message=result["message"],
        recommendations=result["recommendations"],
        total_products=total,
        response_time_seconds=round(time.time() - start, 3)
    )

if __name__ == "__main__":
    import uvicorn
    store = get_vector_store()
    uvicorn.run(app, host="0.0.0.0", port=8001)
