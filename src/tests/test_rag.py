import sys
from rag_engine import RAGEngine
from vector_store_manager_local import VectorStoreManager

def test_rag(repo_key: str, query: str):
    """Test RAG query engine"""
    print("\n=== Testing RAG Query Engine ===")
    print(f"Repository: {repo_key}")
    print(f"Query: \"{query}\"")
    
    # Initialize RAG engine
    rag_engine = RAGEngine()
    
    # First, make sure the repository is indexed
    vector_store = VectorStoreManager()
    vector_store.index_repository(repo_key)
    
    # Query the repository
    result = rag_engine.query(repo_key, query)
    
    # Print the answer
    print("\n=== Answer ===")
    print(result["answer"])
    
    # Print the sources
    print("\n=== Sources ===")
    for i, source in enumerate(result["sources"]):
        print(f"\nSource {i+1} (Score: {source['score']:.4f}):")
        filename = source["metadata"].get("filename", "Unknown")
        page = source["metadata"].get("page_num", "Unknown")
        print(f"From: {filename}, Page: {page}")
        print(f"Excerpt: {source['text']}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python test_rag.py <repository_key> <query>")
        sys.exit(1)
    
    repo_key = sys.argv[1]
    query = sys.argv[2]
    
    test_rag(repo_key, query)