from fastapi import FastAPI
from pydantic import BaseModel
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from typing import Optional
import os

app = FastAPI()

# Load embedding model
embed_model = SentenceTransformer("all-MiniLM-L6-v2")

# Sample documents aligned with FAISS
documents = [
    {"content": "Asia tech stocks surged due to favorable policy changes."},
    {"content": "TSMC reported strong earnings driven by AI chip demand."},
    {"content": "Weak export numbers pulled Chinese tech ETFs lower."},
]

# Load FAISS index
try:
    if not os.path.exists("faiss.index"):
        raise FileNotFoundError("FAISS index not found.")
    
    index = faiss.read_index("faiss.index")
    assert index.ntotal == len(documents), "FAISS index size and document count mismatch."

except Exception as e:
    print(f"Startup error: {e}")
    index = None

# Combined input model (includes query)
class AnalysisRequest(BaseModel):
    asia_tech_today: Optional[float] = 0.0
    asia_tech_yesterday: Optional[float] = 0.0
    query: str

# Retrieval function
def retrieve(query: str):
    query_vector = embed_model.encode([query])
    query_vector = np.array(query_vector).astype("float32")
    D, I = index.search(query_vector, k=3)
    return [documents[i] for i in I[0] if 0 <= i < len(documents)]

# Analysis logic
def analyze(data: AnalysisRequest):
    today_pct = data.asia_tech_today * 100
    yday_pct = data.asia_tech_yesterday * 100
    change_pct = round(today_pct - yday_pct, 2)

    if change_pct > 2:
        trend = "increased significantly"
    elif change_pct > 0:
        trend = "slightly increased"
    elif change_pct < -2:
        trend = "decreased significantly"
    elif change_pct < 0:
        trend = "slightly decreased"
    else:
        trend = "remained steady"

    response = (
        f"Your Asia tech allocation is {round(today_pct, 2)}% of AUM, "
        f"up from {round(yday_pct, 2)}% yesterday. "
        f"The allocation has {trend} by {abs(change_pct)}%."
    )

    # Add relevant news
    for doc in retrieve(data.query):
        response += f"\nRelevant Info: {doc['content']}"

    return response

# POST endpoint
@app.post("/analyze")
async def analyze_data(data: AnalysisRequest):
    try:
        return {"result": analyze(data)}
    except Exception as e:
        return {"error": f"Analysis failed: {e}"}
