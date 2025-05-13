# build_faiss_index.py
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np

documents = [
    {"content": "Asia tech stocks surged due to favorable policy changes."},
    {"content": "TSMC reported strong earnings driven by AI chip demand."},
    {"content": "Weak export numbers pulled Chinese tech ETFs lower."},
]

embed_model = SentenceTransformer("all-MiniLM-L6-v2")
texts = [doc["content"] for doc in documents]
vectors = embed_model.encode(texts)
vectors = np.array(vectors).astype('float32')

index = faiss.IndexFlatL2(vectors.shape[1])
index.add(vectors)
faiss.write_index(index, "faiss.index")

print("✅ faiss.index built and saved.")
