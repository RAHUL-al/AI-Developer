from vector_store import get_vector_store
from models import Product, RecommendedProduct
from embedding_service import TOP_K

def make_explanation(query: str, product: Product, score: float) -> str:
    q = query.lower()
    reasons = []
    if product.color and product.color.lower() in q:
        reasons.append(f"color '{product.color}'")
    for s in product.size:
        if s.lower() in q:
            reasons.append(f"size {s}")
            break
    common = set(q.split()) & set(product.title.lower().split())
    if common: reasons.append(f"'{', '.join(common)}'")
    tags = [t for t in product.tags if any(w in t.lower() for w in q.split())]
    if tags: reasons.append(f"tagged '{', '.join(tags)}'")
    return f"Matches: {'; '.join(reasons)}." if reasons else "Semantic match."

def rank_products(query: str, products: list[Product] = None) -> list[RecommendedProduct]:
    store = get_vector_store()
    if products:
        store.clear()
        store.add_products(products)
    results = store.search(query, top_k=TOP_K)
    return [RecommendedProduct(
        id=p.id, title=p.title, color=p.color, size=p.size, tags=p.tags,
        score=round(s, 4), explanation=make_explanation(query, p, s)
    ) for p, s in results]
