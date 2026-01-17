import os
from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAIEmbeddings

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
TOP_K = 3

class EmbeddingService:
    def __init__(self):
        if not GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY required")
        self.embedder = GoogleGenerativeAIEmbeddings(
            model="models/text-embedding-004",
            google_api_key=GEMINI_API_KEY
        )
        self.cache = {}
    
    def get_embedding(self, text: str):
        if text in self.cache:
            return self.cache[text]
        emb = self.embedder.embed_query(text)
        self.cache[text] = emb
        return emb
    
    def get_query_embedding(self, query: str):
        return self.embedder.embed_query(query)
    
    def get_product_embedding(self, title, tags, color="", size=None):
        parts = [title]
        if color: parts.append(f"Color: {color}")
        if size: parts.append(f"Sizes: {', '.join(size)}")
        if tags: parts.append(f"Tags: {', '.join(tags)}")
        return self.get_embedding(". ".join(parts))

_service = None
def get_embedding_service():
    global _service
    if _service is None:
        _service = EmbeddingService()
    return _service
