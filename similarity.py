from vector_store import get_vector_store
from models import Product, RecommendedProduct
from embedding_service import TOP_K

def make_explanation(query: str, product: Product, score: float) -> str:
    """Generate human-readable explanation for why a product was recommended."""
    q = query.lower()
    reasons = []
    
    # Check color match
    if product.color and product.color.lower() in q:
        reasons.append(f"matches color '{product.color}'")
    
    # Check size match
    for s in product.size:
        if s.lower() in q or s.lower() in q.replace(" ", ""):
            reasons.append(f"available in size {s}")
            break
    
    # Check title word matches
    title_words = set(product.title.lower().split())
    query_words = set(q.split())
    common = title_words & query_words
    if common:
        reasons.append(f"title contains '{', '.join(common)}'")
    
    # Check tag matches
    matching_tags = []
    for tag in product.tags:
        if any(word in tag.lower() for word in q.split()):
            matching_tags.append(tag)
    if matching_tags:
        reasons.append(f"tagged as '{', '.join(matching_tags)}'")
    
    # Add similarity score context
    if score >= 0.8:
        quality = "Excellent"
    elif score >= 0.6:
        quality = "Good"
    else:
        quality = "Partial"
    
    if reasons:
        return f"{quality} match ({score:.0%}): {'; '.join(reasons)}."
    else:
        return f"{quality} semantic match ({score:.0%}): Similar style and characteristics."

def has_strong_match(query: str, product: Product, score: float) -> bool:
    """Check if this is a strong match based on query keywords."""
    q = query.lower()
    query_words = set(q.split())
    
    # Check for color match
    if product.color and product.color.lower() in q:
        return True
    
    # Check for explicit size match (only standalone sizes like "xl", "size m", etc.)
    size_keywords = {"xs", "s", "m", "l", "xl", "xxl", "small", "medium", "large"}
    for s in product.size:
        s_lower = s.lower()
        # Only count if size appears as a standalone word in query
        if s_lower in query_words and s_lower in size_keywords:
            return True
    
    # Check for meaningful keyword match in title (ignore single-letter words)
    title_words = set(word for word in product.title.lower().split() if len(word) > 1)
    meaningful_query_words = set(word for word in query_words if len(word) > 2)
    if title_words & meaningful_query_words:
        return True
    
    # Check for tag match (require meaningful word overlap)
    for tag in product.tags:
        if any(word in tag.lower() for word in meaningful_query_words):
            return True
    
    # High similarity score is also a strong match
    if score >= 0.7:
        return True
    
    return False

def rank_products(query: str, products: list[Product] = None, top_k: int = TOP_K) -> dict:
    """
    Rank products based on query similarity.
    Returns a dict with 'found', 'recommendations', and 'message'.
    """
    store = get_vector_store()
    
    # If products provided, use temporary search
    if products:
        store.clear()
        store.add_products(products)
    
    # Check if store is empty
    if store.is_empty():
        return {
            "found": False,
            "message": "No products in the database. Please initialize with demo data.",
            "recommendations": []
        }
    
    # Search for matching products
    results = store.search(query, top_k=top_k)
    
    if not results:
        # Get any 3 random suggestions as fallback
        fallback_results = store.search("dress clothing fashion", top_k=3)
        return {
            "found": False,
            "message": f"No exact matches found for '{query}'. Here are some suggestions you might like:",
            "recommendations": [
                RecommendedProduct(
                    id=p.id, title=p.title, color=p.color, size=p.size, tags=p.tags,
                    score=round(s, 4), explanation="Suggested alternative from our collection."
                ) for p, s in fallback_results
            ]
        }
    
    # Check if we have strong matches
    strong_matches = [(p, s) for p, s in results if has_strong_match(query, p, s)]
    
    if strong_matches:
        # We found good matches
        return {
            "found": True,
            "message": f"Found {len(strong_matches)} matching product(s) for '{query}':",
            "recommendations": [
                RecommendedProduct(
                    id=p.id, title=p.title, color=p.color, size=p.size, tags=p.tags,
                    score=round(s, 4), explanation=make_explanation(query, p, s)
                ) for p, s in strong_matches[:top_k]
            ]
        }
    else:
        # Only weak/semantic matches - suggest alternatives
        return {
            "found": False,
            "message": f"No exact matches for '{query}', but here are similar items you might like:",
            "recommendations": [
                RecommendedProduct(
                    id=p.id, title=p.title, color=p.color, size=p.size, tags=p.tags,
                    score=round(s, 4), explanation=make_explanation(query, p, s)
                ) for p, s in results
            ]
        }
