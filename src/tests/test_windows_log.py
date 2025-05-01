import sys
from pathlib import Path
from document_processor import DocumentProcessor
from document_classifier import DocumentClassifier
from vector_store_manager_local import VectorStoreManager
from rag_engine import RAGEngine

def test_windows_log_processing(log_file_path):
    """Test processing and RAG on Windows log file"""
    print("\n=== Testing Windows Log File Processing ===")
    
    # 1. Verify log file exists
    log_file = Path(log_file_path)
    if not log_file.exists():
        print(f"Error: Log file {log_file} does not exist")
        return
    
    print(f"Found log file: {log_file}")
    
    # 2. Classify the log file first
    classification = DocumentClassifier.classify_document(str(log_file))
    print(f"\nDocument classification: {classification}")
    
    # 3. Process log file
    print(f"\nProcessing log file: {log_file}")
    processor = DocumentProcessor()
    repo_key = "windows_log_repository"
    
    # Process with classification
    result = processor.process_document_with_classification(
        file_path=str(log_file),
        repo_key=repo_key
    )
    
    print(f"\nProcessing result:")
    print(f"  Document ID: {result.get('id')}")
    print(f"  File: {result.get('filename')}")
    print(f"  Document Type: {result.get('document_type')}")
    print(f"  Total Chunks: {result.get('total_chunks')}")
    print(f"  Chunk Strategy: {result.get('chunk_strategy')}")
    
    # Print log metadata if available
    log_metadata = result.get('log_metadata', {})
    if log_metadata:
        print(f"\nLog Metadata:")
        print(f"  First Timestamp: {log_metadata.get('first_timestamp')}")
        print(f"  Last Timestamp: {log_metadata.get('last_timestamp')}")
        print(f"  Timespan (hours): {log_metadata.get('timespan_hours')}")
        print(f"  Error Count: {log_metadata.get('error_count')}")
        print(f"  Warning Count: {log_metadata.get('warning_count')}")
    
    # 4. Index the repository with debugging
    print("\nIndexing log repository...")
    vector_store = VectorStoreManager()
    
    # Get document ID from the result
    doc_id = result.get('id')
    if doc_id:
        # Index specific document with debugging
        success = vector_store.index_document(repo_key, doc_id)
        print(f"Indexing success: {success}")
    else:
        print("Error: No document ID returned from processing")
        return
    
    # Verify the chunks were correctly loaded
    doc_dir = processor.repo_manager.get_repository_path(repo_key) / "documents" / doc_id / "content"
    if doc_dir.exists():
        print(f"\nVerifying content directory: {doc_dir}")
        files = list(doc_dir.glob("*"))
        print(f"Found {len(files)} files in content directory:")
        for file in files[:5]:  # Show first 5 files
            print(f"  - {file.name}")
        if len(files) > 5:
            print(f"  - ... and {len(files) - 5} more")
    
    # 5. Test RAG queries
    if success:
        print("\n=== Testing RAG Queries on Windows Log Repository ===")
        rag_engine = RAGEngine()
        
        test_queries = [
            "What types of events are recorded in this log?",
            "Are there any critical errors in the log?",
            "What time period does this log cover?",
            "What are the most common log entries about?"
        ]
        
        for query in test_queries:
            print(f"\nQuery: {query}")
            result = rag_engine.query(repo_key, query)
            print(f"Answer: {result['answer']}")
            
            # Print the first source for verification
            if result["sources"]:
                print(f"\nFirst source excerpt: {result['sources'][0]['text'][:150]}...")

if __name__ == "__main__":
    # Use the first argument as the log file path or default to a standard location
    log_file_path = sys.argv[1] if len(sys.argv) > 1 else "Windows_2k.log"
    test_windows_log_processing(log_file_path)