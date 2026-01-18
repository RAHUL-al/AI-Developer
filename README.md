# Smart Search API

AI-powered product recommendation service using **semantic search** with Google Gemini embeddings and FAISS vector database.

## Features

- 🔍 **Semantic Search** - Find products using natural language queries
- 🎯 **Smart Recommendations** - AI-powered similarity matching
- 💬 **Explainable Results** - Each recommendation includes reasoning
- 📦 **Persistent Storage** - Embeddings stored in FAISS for fast retrieval
- 🔄 **Fallback Suggestions** - Suggests alternatives when no exact match found

## Tech Stack

- **FastAPI** - Modern async Python web framework
- **Google Gemini** - Text embeddings (text-embedding-004)
- **FAISS** - Facebook AI Similarity Search
- **Pydantic** - Data validation

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Up Environment

Create a `.env` file:
```
GEMINI_API_KEY=your_gemini_api_key_here
```

### 3. Initialize Database

```bash
python init_data.py
```

This loads 45 demo products into the vector database.

### 4. Run the Server

```bash
python app.py
```

Server runs at: `http://localhost:8001`

## API Endpoints

### Health Check
```
GET /
```
Returns API status and product count.

---

### Search Products
```
POST /search
```

Search the stored product catalog.

**Request:**
```json
{
  "query": "red party dress"
}
```

**Response:**
```json
{
  "query": "red party dress",
  "found": true,
  "message": "Found 3 matching product(s) for 'red party dress':",
  "recommendations": [
    {
      "id": 1,
      "title": "Red Sequin Gown",
      "color": "red",
      "size": ["S", "M", "L"],
      "tags": ["party", "evening", "gown"],
      "score": 0.7419,
      "explanation": "Good match (74%): matches color 'red'; title contains 'red'; tagged as 'party'."
    }
  ],
  "total_products_in_store": 45,
  "response_time_seconds": 0.63
}
```

---

### Get Recommendations
```
POST /recommend
```

Get recommendations from stored DB or custom product list.

**Option 1: Search stored products**
```json
{
  "query": "blue jacket size XL"
}
```

**Option 2: Search custom product list**
```json
{
  "query": "red party dress",
  "products": [
    {"id": 1, "title": "Red Sequin Gown", "color": "red", "tags": ["party"]},
    {"id": 2, "title": "Black Cocktail Dress", "color": "black", "tags": ["cocktail"]},
    {"id": 3, "title": "Red Maxi Dress", "color": "red", "tags": ["casual"]}
  ]
}
```

## Search Examples

| Query | What it finds |
|-------|---------------|
| `"red party dress"` | Red dresses with party tags |
| `"blue jacket size L"` | Blue jackets in size L |
| `"formal office wear"` | Professional/office clothing |
| `"summer beach dress"` | Casual summer/beach items |
| `"wedding gown"` | Bridal/wedding attire |

## Project Structure

```
├── app.py              # FastAPI endpoints
├── similarity.py       # Ranking & explanation logic
├── vector_store.py     # FAISS vector database
├── embedding_service.py # Google Gemini embeddings
├── models.py           # Pydantic data models
├── demo_data.py        # 45 sample products
├── init_data.py        # Database initialization script
├── requirements.txt    # Python dependencies
├── products.index      # FAISS index (generated)
└── products.json       # Product data (generated)
```

## Re-initialize Database

To reset and reload products:

```bash
python init_data.py --force
```

## API Documentation

Interactive API docs available at:
- Swagger UI: `http://localhost:8001/docs`
- ReDoc: `http://localhost:8001/redoc`

## Response Format

When products are found:
```json
{
  "found": true,
  "message": "Found X matching product(s) for 'query':",
  "recommendations": [...]
}
```

When no exact match (suggests alternatives):
```json
{
  "found": false,
  "message": "No exact matches for 'query', but here are similar items you might like:",
  "recommendations": [...]
}
```

## Performance

- Response time: **< 1 second** (typically 0.5-0.8s)
- Embeddings are cached for repeated queries
- FAISS enables fast similarity search even with large catalogs
