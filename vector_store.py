import os
import json
import numpy as np
import faiss
from embedding_service import get_embedding_service
from models import Product

INDEX_FILE = "products.index"
PRODUCTS_FILE = "products.json"

class VectorStore:
    def __init__(self):
        self.index = faiss.IndexFlatIP(768)
        self.products = []
        self.embedder = get_embedding_service()
        self.load()
    
    def add_products(self, products: list[Product]):
        if not products: return
        embeddings = []
        for p in products:
            emb = self.embedder.get_product_embedding(p.title, p.tags, p.color, p.size)
            embeddings.append(emb)
        arr = np.array(embeddings, dtype=np.float32)
        faiss.normalize_L2(arr)
        self.index.add(arr)
        self.products.extend(products)
    
    def search(self, query: str, top_k: int = 3):
        if self.index.ntotal == 0: return []
        q_emb = self.embedder.get_query_embedding(query)
        q_arr = np.array([q_emb], dtype=np.float32)
        faiss.normalize_L2(q_arr)
        scores, indices = self.index.search(q_arr, min(top_k, self.index.ntotal))
        return [(self.products[i], float(scores[0][j])) for j, i in enumerate(indices[0]) if i < len(self.products)]
    
    def save(self):
        faiss.write_index(self.index, INDEX_FILE)
        data = [{"id": p.id, "title": p.title, "color": p.color, "size": p.size, "tags": p.tags} for p in self.products]
        with open(PRODUCTS_FILE, "w") as f: json.dump(data, f)
        print(f"Saved {len(self.products)} products")
    
    def load(self):
        if os.path.exists(INDEX_FILE) and os.path.exists(PRODUCTS_FILE):
            self.index = faiss.read_index(INDEX_FILE)
            with open(PRODUCTS_FILE) as f: self.products = [Product(**p) for p in json.load(f)]
            print(f"Loaded {len(self.products)} products")
            return True
        return False
    
    def clear(self):
        self.index.reset()
        self.products.clear()
    
    def is_empty(self):
        return self.index.ntotal == 0

_store = None
def get_vector_store():
    global _store
    if _store is None: _store = VectorStore()
    return _store
