import os
import json
import numpy as np
import faiss
from embedding_service import get_embedding_service
from models import Product

INDEX_FILE = "products.index"
PRODUCTS_FILE = "products.json"

class VectorStore:
    """
    FAISS-based vector store for product embeddings.
    Provides persistent storage - embeddings are saved to disk and loaded on startup.
    """
    
    def __init__(self):
        self.index = faiss.IndexFlatIP(768)  # 768 dimensions for Gemini embeddings
        self.products = []
        self.embedder = get_embedding_service()
        self._load_from_disk()
    
    def add_products(self, products: list[Product]):
        """Add products to the vector store and generate embeddings."""
        if not products:
            return
        
        print(f"Generating embeddings for {len(products)} products...")
        embeddings = []
        for i, p in enumerate(products):
            emb = self.embedder.get_product_embedding(p.title, p.tags, p.color, p.size)
            embeddings.append(emb)
            if (i + 1) % 10 == 0:
                print(f"  Processed {i + 1}/{len(products)} products...")
        
        arr = np.array(embeddings, dtype=np.float32)
        faiss.normalize_L2(arr)
        self.index.add(arr)
        self.products.extend(products)
        print(f"Added {len(products)} products to vector store.")
    
    def search(self, query: str, top_k: int = 3) -> list[tuple[Product, float]]:
        """
        Search for similar products using semantic similarity.
        Returns list of (product, similarity_score) tuples.
        """
        if self.index.ntotal == 0:
            return []
        
        # Get query embedding
        q_emb = self.embedder.get_query_embedding(query)
        q_arr = np.array([q_emb], dtype=np.float32)
        faiss.normalize_L2(q_arr)
        
        # Search FAISS index
        num_results = min(top_k, self.index.ntotal)
        scores, indices = self.index.search(q_arr, num_results)
        
        # Return products with scores
        results = []
        for j, i in enumerate(indices[0]):
            if 0 <= i < len(self.products):
                results.append((self.products[i], float(scores[0][j])))
        
        return results
    
    def save(self):
        """Persist the vector index and product data to disk."""
        faiss.write_index(self.index, INDEX_FILE)
        data = [
            {
                "id": p.id, 
                "title": p.title, 
                "color": p.color, 
                "size": p.size, 
                "tags": p.tags
            } 
            for p in self.products
        ]
        with open(PRODUCTS_FILE, "w") as f:
            json.dump(data, f, indent=2)
        print(f"[OK] Saved {len(self.products)} products to disk")
    
    def _load_from_disk(self):
        """Load persisted data from disk if available."""
        if os.path.exists(INDEX_FILE) and os.path.exists(PRODUCTS_FILE):
            try:
                self.index = faiss.read_index(INDEX_FILE)
                with open(PRODUCTS_FILE) as f:
                    self.products = [Product(**p) for p in json.load(f)]
                print(f"[OK] Loaded {len(self.products)} products from disk")
                return True
            except Exception as e:
                print(f"Warning: Could not load saved data: {e}")
                self.index = faiss.IndexFlatIP(768)
                self.products = []
        return False
    
    def clear(self):
        """Clear all products from the store (does not delete disk files)."""
        self.index.reset()
        self.products.clear()
    
    def is_empty(self) -> bool:
        """Check if the store has no products."""
        return self.index.ntotal == 0
    
    def delete_persistence(self):
        """Delete persisted files from disk."""
        for f in [INDEX_FILE, PRODUCTS_FILE]:
            if os.path.exists(f):
                os.remove(f)
                print(f"Deleted {f}")

# Singleton instance
_store = None

def get_vector_store() -> VectorStore:
    """Get the singleton VectorStore instance."""
    global _store
    if _store is None:
        _store = VectorStore()
    return _store
