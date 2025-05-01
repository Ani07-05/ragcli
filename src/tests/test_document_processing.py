import os
import sys
from pathlib import Path
from document_processor import DocumentProcessor
from repository_manager import RepositoryManager

def test_repository_manager():
    """Test repository manager functionality"""
    print("\n=== Testing Repository Manager ===")
    
    # Initialize repository manager
    repo_manager = RepositoryManager()
    
    # Create test repository
    test_repo_key = "test_repository"
    repo_manager.create_repository(test_repo_key, "Test repository for document processing")
    
    # List repositories
    repos = repo_manager.list_repositories()
    print(f"Repositories: {repos}")
    
    # Get repository path
    repo_path = repo_manager.get_repository_path(test_repo_key)
    print(f"Repository path: {repo_path}")
    print(f"Repository path exists: {repo_path.exists() if repo_path else False}")
    
    return test_repo_key

def test_document_processing(repo_key, file_path):
    """Test document processing with a sample file"""
    print("\n=== Testing Document Processing ===")
    
    if not os.path.exists(file_path):
        print(f"Error: File not found: {file_path}")
        return
    
    # Initialize document processor
    processor = DocumentProcessor()
    
    # Process document
    print(f"Processing document: {file_path}")
    result = processor.process_document(file_path, repo_key)
    
    print(f"Processing result: {result}")
    
    # List documents in repository
    docs = processor.list_documents(repo_key)
    print(f"Documents in repository: {len(docs)}")
    for doc in docs:
        print(f"- {doc['filename']} ({doc['id']})")
    
    return result

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python test_document_processing.py <path_to_document>")
        sys.exit(1)
    
    file_path = sys.argv[1]
    repo_key = test_repository_manager()
    test_document_processing(repo_key, file_path)