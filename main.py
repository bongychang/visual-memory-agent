from fastapi import FastAPI
from pydantic import BaseModel
from engine import VisualMemoryEngine, ImageIndex

app = FastAPI(title="Visual Memory API")

# Initialize our classes
ai_engine = VisualMemoryEngine()
db_index = ImageIndex()

def load_database():
    """Loads the database from disk into RAM."""
    try:
        db_index.load()
        print(f"Loaded {len(db_index.image_paths)} images into the index.")
        return len(db_index.image_paths)
    except Exception as e:
        print("No index found. The database is empty.")
        return 0

# Load database when the server starts
load_database()

class SearchQuery(BaseModel):
    text: str
    top_k: int = 3

@app.post("/search")
def search_local_images(query: SearchQuery):
    # Safety Check: Don't search if the DB is empty
    if len(db_index.image_paths) == 0:
         return {"query": query.text, "results": []}
         
    # 1. Convert text to vector
    text_vector = ai_engine.embed_text(query.text)
    
    # 2. Search FAISS index
    results = db_index.search(text_vector, k=query.top_k)
    
    # 3. Return a clean JSON response
    return {
        "query": query.text,
        "results": [{"file_path": path, "confidence_score": float(score)} for path, score in results]
    }

# NEW: An endpoint that allows the UI to force a database reload
@app.post("/reload")
def reload_index():
    count = load_database()
    return {"status": "success", "indexed_count": count}