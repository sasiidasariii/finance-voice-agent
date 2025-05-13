from fastapi import FastAPI
from pydantic import BaseModel
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
import os

# Initialize FastAPI app
app = FastAPI()

# Load embedding model
embed_model = SentenceTransformer("all-MiniLM-L6-v2")

# Load FAISS index and documents
try:
    if not os.path.exists("faiss.index"):
        raise FileNotFoundError("faiss.index not found. Please ensure it exists.")

    index = faiss.read_index("faiss.index")

    # Documents aligned with FAISS vectors
    documents = [
        {"content": "Asia tech stocks surged due to favorable policy changes."},
        {"content": "TSMC reported strong earnings driven by AI chip demand."},
        {"content": "Weak export numbers pulled Chinese tech ETFs lower."},
        # Add more if needed
    ]

    assert index.ntotal == len(documents), (
        f"Mismatch: FAISS index has {index.ntotal} vectors but {len(documents)} documents."
    )

except Exception as e:
    print(f"[Startup Error] {e}")
    index = None
    documents = []

# Input schema
class BriefRequest(BaseModel):
    asia_tech_today: float
    asia_tech_yesterday: float
    query: str

# Document retrieval using FAISS
def retrieve(query: str):
    try:
        query_vector = embed_model.encode([query])
        query_vector = np.array(query_vector).astype("float32")
        D, I = index.search(query_vector, k=3)
        return [documents[i] for i in I[0] if 0 <= i < len(documents)]
    except Exception as e:
        raise RuntimeError(f"[Retrieve Error]: {e}")

# Main analysis function
def analyze(market_data: BriefRequest):
    if index is None:
        return {"error": "FAISS index not loaded."}

    try:
        today_pct = market_data.asia_tech_today * 100
        yday_pct = market_data.asia_tech_yesterday * 100
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

        retrieved_docs = retrieve(market_data.query)
        for doc in retrieved_docs:
            response += f"\nRelevant Info: {doc['content']}"

        return {"result": response}

    except Exception as e:
        return {"error": f"Risk analysis failed: {e}"}

# Final POST endpoint for Streamlit or other agents
@app.post("/brief")
async def get_market_brief(data: BriefRequest):
    return analyze(data)
