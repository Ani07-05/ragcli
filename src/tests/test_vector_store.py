import sys
from repository_manager import RepositoryManager
from document_processor import DocumentProcessor
from vector_store_manager_local import VectorStoreManager

def test_indexing(repo_key: str, doc_id: str = None):
    """Test indexing documents in a repository"""
    print("\n=== Testing Document Indexing ===")
    
    vector_manager = VectorStoreManager()
    
    if doc_id:
        # Index a specific document
        print(f"Indexing document {doc_id} in repository {repo_key}")
        result = vector_manager.index_document(repo_key, doc_id)
        print(f"Indexing result: {result}")
    else:
        # Index all documents in the repository
        print(f"Indexing all documents in repository {repo_key}")
        results = vector_manager.index_repository(repo_key)
        print(f"Indexing results: {results}")

def test_search(repo_key: str, query: str):
    """Test searching a repository"""
    print(f"\n=== Testing Repository Search ===")
    print(f"Query: \"{query}\"")
    
    vector_manager = VectorStoreManager()
    results = vector_manager.search_repository(repo_key, query)
    
    print(f"\nFound {len(results)} results:")
    for i, result in enumerate(results):
        print(f"\n--- Result {i+1} (Score: {result['score']:.4f}) ---")
        
        # Print metadata
        doc_id = result['metadata'].get('doc_id', 'Unknown')
        filename = result['metadata'].get('filename', 'Unknown')
        page = result['metadata'].get('page_num', 'Unknown')
        
        print(f"Source: {filename}, Page: {page}, Doc ID: {doc_id}")
        
        # Print truncated text
        max_text_len = 300
        text = result['text']
        if len(text) > max_text_len:
            displayed_text = text[:max_text_len] + "..."
        else:
            displayed_text = text
            
        print(f"\nContent: {displayed_text}")
    
    return results

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python test_vector_store.py <repository_key> <query> [document_id]")
        sys.exit(1)
    
    repo_key = sys.argv[1]
    query = sys.argv[2]
    doc_id = sys.argv[3] if len(sys.argv) > 3 else None
    
    # Test indexing
    test_indexing(repo_key, doc_id)
    
    # Test searching
    test_search(repo_key, query)