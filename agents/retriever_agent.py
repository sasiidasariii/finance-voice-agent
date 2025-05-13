from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
from functools import lru_cache

# ------------------- Lazy Load Model ------------------- #
@lru_cache(maxsize=1)
def get_model():
    return SentenceTransformer("paraphrase-albert-small-v2")

# ------------------- Embed and Store ------------------- #
def embed_and_store(texts):
    """Embed texts and store them in a FAISS index."""
    model = get_model()  # Load model only when needed
    vectors = model.encode(texts)

    index = faiss.IndexFlatL2(vectors.shape[1])
    index.add(np.array(vectors))

    print(f"Number of embedded documents: {len(texts)}")
    return index, texts

# ------------------- Retrieve Top K ------------------- #
def retrieve_top_k(query, index, texts, k=3):
    """Retrieve the top k most similar documents."""
    model = get_model()  # Load model only when needed
    q_vec = model.encode([query])

    D, I = index.search(q_vec, k)
    print(f"Query: {query}")
    print(f"Indices Retrieved: {I}")
    print(f"Retrieved Texts: {[texts[i] for i in I[0]]}")
    return [texts[i] for i in I[0]]
