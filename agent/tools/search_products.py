from rag_pipeline.vector_store import build_vector_store, load_vector_store
from rag_pipeline.retriever import retriever
from rag_pipeline.reranker import rerank
from rag_pipeline.compressor import compress

def search_product(query: str, user_id: str = "agent") -> str:
     """
    Tool: search_products
    Searches product knowledge base using the full RAG pipeline.
    Returns compressed, relevant product information for the query.
 
    Use when customer asks about:
    - Product features, specs, details
    - Price of a product
    - Availability or stock
    - Comparison between products
    - Which product is best for their need
    """
     
     try:
        # Step 1 — load or build vector store
        index, documents = load_vector_store()
        if index is None:
            index, documents = build_vector_store()

        # Step 2 — retrieve top chunks
        retrieved_chunks = retriever(
            query,
            index,
            documents,
            domain='product'
        )

        if not retrieved_chunks:
            return "No relevant products found for this query."
        
        # Step 3 — rerank to top 3
        try:
            reranked_chunks = rerank(query, retrieved_chunks, top_k=3)
        except Exception as e:
            print(f"[RERANK ERROR] {e}")
            reranked_chunks = retrieved_chunks[:3]

        # Step 4 — compress context
        compressed = compress(query, reranked_chunks, user_id)
 
        return compressed
     
     except Exception as e:
        print(f"[SEARCH_PRODUCTS ERROR] {e}")
        return "Sorry, I had trouble searching the products. Please try again."

        