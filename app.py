from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from similarity import rank_products
from models import RecommendRequest, RecommendResponse
from vector_store import get_vector_store
import time

app = FastAPI(title="Smart Search API")

class SearchQuery(BaseModel):
    query: str

@app.get("/")
async def home():
    store = get_vector_store()
    return {"status": "ok", "products": len(store.products)}

@app.post("/search")
async def search(req: SearchQuery):
    start = time.time()
    store = get_vector_store()
    if store.is_empty():
        raise HTTPException(400, "No products. Run: python init_data.py")
    recs = rank_products(req.query)
    return {"query": req.query, "recommendations": recs, "time": round(time.time() - start, 3)}

@app.post("/recommend", response_model=RecommendResponse)
async def recommend(req: RecommendRequest):
    start = time.time()
    recs = rank_products(req.query, req.products)
    return RecommendResponse(
        query=req.query, recommendations=recs,
        total_products=len(req.products), response_time_seconds=round(time.time() - start, 3)
    )

if __name__ == "__main__":
    import uvicorn
    store = get_vector_store()
    print(f"\nSmart Search API | Products: {len(store.products)}")
    print("http://localhost:5000/docs\n")
    uvicorn.run(app, host="0.0.0.0", port=5000)
