from sentence_transformers import SentenceTransformer
import faiss
import numpy as np

model = SentenceTransformer("all-MiniLM-L6-v2")

def embed_and_store(texts):
    # Embed the texts
    vectors = model.encode(texts)
    index = faiss.IndexFlatL2(vectors.shape[1])
    index.add(np.array(vectors))
    print(f"Number of embedded documents: {len(texts)}")  # Debugging line
    return index, texts

def retrieve_top_k(query, index, texts, k=3):
    # Encode the query
    q_vec = model.encode([query])
    D, I = index.search(q_vec, k)
    print(f"Query: {query}")  # Debugging line
    print(f"Indices Retrieved: {I}")  # Debugging line
    print(f"Retrieved Texts: {[texts[i] for i in I[0]]}")  # Debugging line
    return [texts[i] for i in I[0]]
