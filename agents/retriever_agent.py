from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import tempfile

# Load a smaller model to reduce memory consumption
model = SentenceTransformer("paraphrase-albert-small-v2")

# ------------------- Embed and Store ------------------- #
def embed_and_store(texts):
    """Embed texts and store them in a FAISS index."""
    # Embed the texts using the smaller model
    vectors = model.encode(texts)
    
    # Use a flat L2 index
    index = faiss.IndexFlatL2(vectors.shape[1])
    index.add(np.array(vectors))
    
    # Debugging line to track embedded documents
    print(f"Number of embedded documents: {len(texts)}")
    
    return index, texts

# ------------------- Retrieve Top K ------------------- #
def retrieve_top_k(query, index, texts, k=3):
    """Retrieve the top k most similar documents."""
    # Encode the query
    q_vec = model.encode([query])
    
    # Perform the search to retrieve top k
    D, I = index.search(q_vec, k)
    
    # Debugging lines to track the search
    print(f"Query: {query}")
    print(f"Indices Retrieved: {I}")
    print(f"Retrieved Texts: {[texts[i] for i in I[0]]}")
    
    return [texts[i] for i in I[0]]

