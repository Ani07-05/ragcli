import os
import json
import uuid
from pathlib import Path
from typing import Dict, List, Optional, Union, Any
from datetime import datetime
from llama_cloud_services import LlamaParse
from config import LLAMA_CLOUD_API_KEY
from repository_manager import RepositoryManager
from document_classifier import DocumentClassifier
from log_processor import LogProcessor

class DocumentProcessor:
    """Processes documents using LlamaParse and stores them in repositories"""
    
    def __init__(self):
        self.repo_manager = RepositoryManager()
        self.parser = LlamaParse(
            api_key=LLAMA_CLOUD_API_KEY,
            result_type="markdown",  # Get markdown for better structure
            verbose=True
        )
    
    def process_document(self, 
                        file_path: str, 
                        repo_key: str, 
                        document_metadata: Optional[Dict[str, Any]] = None) -> Dict:
        """
        Process a document and store it in the repository
        
        Args:
            file_path: Path to the document file
            repo_key: Repository key to store the document
            document_metadata: Additional metadata for the document
            
        Returns:
            Dict with document information
        """
        # Ensure repository exists
        repo_path = self.repo_manager.get_repository_path(repo_key)
        if repo_path is None:
            # Create repository if it doesn't exist
            self.repo_manager.create_repository(repo_key)
            repo_path = self.repo_manager.get_repository_path(repo_key)
        
        # Generate a unique document ID
        doc_id = str(uuid.uuid4())
        
        # Get document file name and extension
        file_name = os.path.basename(file_path)
        _, extension = os.path.splitext(file_name)
        
        # Set up metadata
        if document_metadata is None:
            document_metadata = {}
            
        metadata = {
            "id": doc_id,
            "filename": file_name,
            "extension": extension.lower(),
            "processed_at": datetime.now().isoformat(),
            "repository": repo_key,
            **document_metadata
        }
        
        # Process with LlamaParse
        print(f"Processing document: {file_name}")
        try:
            # Parse the document
            result = self.parser.parse(file_path)
            
            # Get content as markdown
            markdown_docs = result.get_markdown_documents(split_by_page=True)
            
            # Create document directory
            doc_dir = repo_path / "documents" / doc_id
            doc_dir.mkdir(parents=True, exist_ok=True)
            
            # Save original file
            original_file_path = doc_dir / "original"
            original_file_path.mkdir(exist_ok=True)
            with open(file_path, "rb") as src_file:
                with open(original_file_path / file_name, "wb") as dest_file:
                    dest_file.write(src_file.read())
            
            # Save processed content
            content_dir = doc_dir / "content"
            content_dir.mkdir(exist_ok=True)
            
            # Save each page as separate file
            pages = []
            for i, doc in enumerate(markdown_docs):
                page_num = i + 1
                page_file = content_dir / f"page_{page_num}.md"
                
                with open(page_file, "w", encoding="utf-8") as f:
                    f.write(doc.text)
                
                pages.append({
                    "page_num": page_num,
                    "file": f"page_{page_num}.md"
                })
            
            # Update metadata with page information
            metadata["total_pages"] = len(pages)
            metadata["pages"] = pages
            
            # Save metadata
            with open(doc_dir / "metadata.json", "w") as f:
                json.dump(metadata, f, indent=2)
            
            # Update repository document count
            self.repo_manager.update_document_count(repo_key, 1)
            
            print(f"Document processed successfully: {doc_id}")
            return metadata
            
        except Exception as e:
            print(f"Error processing document: {e}")
            return {
                "error": str(e),
                **metadata
            }
    
    def process_document_with_classification(self, 
                                           file_path: str, 
                                           repo_key: str, 
                                           document_metadata: Optional[Dict[str, Any]] = None) -> Dict:
        """
        Process a document with automatic classification
        
        Args:
            file_path: Path to the document file
            repo_key: Repository key to store the document
            document_metadata: Additional metadata for the document
            
        Returns:
            Dict with document information
        """
        # Classify the document
        classification = DocumentClassifier.classify_document(file_path)
        
        # Add classification to metadata
        if document_metadata is None:
            document_metadata = {}
        document_metadata["classification"] = classification
        
        # Process based on document type
        if classification["type"] == "log":
            return self._process_log_document(file_path, repo_key, document_metadata)
        else:
            # Use standard processing for non-log documents
            return self.process_document(file_path, repo_key, document_metadata)

    def _process_log_document(self, 
                             file_path: str, 
                             repo_key: str, 
                             document_metadata: Dict[str, Any]) -> Dict:
        """
        Process a log document
        
        Args:
            file_path: Path to the log file
            repo_key: Repository key to store the document
            document_metadata: Additional metadata for the document
            
        Returns:
            Dict with document information
        """
        # Ensure repository exists
        repo_path = self.repo_manager.get_repository_path(repo_key)
        if repo_path is None:
            # Create repository if it doesn't exist
            self.repo_manager.create_repository(repo_key)
            repo_path = self.repo_manager.get_repository_path(repo_key)
        
        # Generate a unique document ID
        doc_id = str(uuid.uuid4())
        
        # Get document file name and extension
        file_name = os.path.basename(file_path)
        _, extension = os.path.splitext(file_name)
        
        # Set up metadata
        metadata = {
            "id": doc_id,
            "filename": file_name,
            "extension": extension.lower(),
            "processed_at": datetime.now().isoformat(),
            "repository": repo_key,
            "document_type": "log",
            **document_metadata
        }
        
        # Create document directory
        doc_dir = repo_path / "documents" / doc_id
        doc_dir.mkdir(parents=True, exist_ok=True)
        
        # Save original file
        original_file_path = doc_dir / "original"
        original_file_path.mkdir(exist_ok=True)
        with open(file_path, "rb") as src_file:
            with open(original_file_path / file_name, "wb") as dest_file:
                dest_file.write(src_file.read())
        
        # Process log file
        content_dir = doc_dir / "content"
        content_dir.mkdir(exist_ok=True)
        
        # Choose chunking strategy based on log size
        file_size = os.path.getsize(file_path)
        if file_size > 5 * 1024 * 1024:  # 5MB
            chunk_strategy = "time_window"
        else:
            chunk_strategy = "fixed_size"
        
        log_metadata = LogProcessor.process_log_file(
            file_path=file_path,
            doc_id=doc_id,
            output_dir=doc_dir,
            chunk_strategy=chunk_strategy
        )
        
        # Update metadata with log processing info
        metadata.update(log_metadata)
        
        # Save metadata
        with open(doc_dir / "metadata.json", "w") as f:
            json.dump(metadata, f, indent=2)
        
        # Update repository document count
        self.repo_manager.update_document_count(repo_key, 1)
        
        print(f"Log document processed successfully: {doc_id}")
        return metadata
    
    def list_documents(self, repo_key: str) -> List[Dict]:
        """List all documents in a repository"""
        repo_path = self.repo_manager.get_repository_path(repo_key)
        if repo_path is None:
            return []
        
        docs_dir = repo_path / "documents"
        if not docs_dir.exists():
            return []
        
        result = []
        for doc_dir in docs_dir.iterdir():
            if doc_dir.is_dir():
                metadata_file = doc_dir / "metadata.json"
                if metadata_file.exists():
                    with open(metadata_file, "r") as f:
                        metadata = json.load(f)
                        result.append(metadata)
        
        return result
    
    def get_document(self, repo_key: str, doc_id: str) -> Optional[Dict]:
        """Get a document by ID from a repository"""
        repo_path = self.repo_manager.get_repository_path(repo_key)
        if repo_path is None:
            return None
        
        doc_dir = repo_path / "documents" / doc_id
        if not doc_dir.exists():
            return None
        
        metadata_file = doc_dir / "metadata.json"
        if not metadata_file.exists():
            return None
        
        with open(metadata_file, "r") as f:
            metadata = json.load(f)
            return metadata
    
    def delete_document(self, repo_key: str, doc_id: str) -> bool:
        """Delete a document from a repository"""
        repo_path = self.repo_manager.get_repository_path(repo_key)
        if repo_path is None:
            return False
        
        doc_dir = repo_path / "documents" / doc_id
        if not doc_dir.exists():
            return False
        
        try:
            # Recursively delete the document directory
            import shutil
            shutil.rmtree(doc_dir)
            
            # Update repository document count
            self.repo_manager.update_document_count(repo_key, -1)
            
            return True
        except Exception as e:
            print(f"Error deleting document: {e}")
            return False
    
    def extract_text_from_document(self, repo_key: str, doc_id: str) -> str:
        """Extract all text from a document"""
        repo_path = self.repo_manager.get_repository_path(repo_key)
        if repo_path is None:
            return ""
        
        doc_dir = repo_path / "documents" / doc_id
        if not doc_dir.exists():
            return ""
        
        metadata_file = doc_dir / "metadata.json"
        if not metadata_file.exists():
            return ""
        
        with open(metadata_file, "r") as f:
            metadata = json.load(f)
        
        # Check if it's a log document
        if metadata.get("document_type") == "log":
            return self._extract_text_from_log(doc_dir, metadata)
        else:
            return self._extract_text_from_standard_doc(doc_dir, metadata)
    
    def _extract_text_from_standard_doc(self, doc_dir: Path, metadata: Dict) -> str:
        """Extract text from a standard document"""
        content_dir = doc_dir / "content"
        if not content_dir.exists():
            return ""
        
        all_text = []
        for page_info in metadata.get("pages", []):
            page_file = content_dir / page_info["file"]
            if page_file.exists():
                with open(page_file, "r", encoding="utf-8") as f:
                    all_text.append(f.read())
        
        return "\n\n".join(all_text)
    
    def _extract_text_from_log(self, doc_dir: Path, metadata: Dict) -> str:
        """Extract text from a log document"""
        content_dir = doc_dir / "content"
        if not content_dir.exists():
            return ""
        
        all_text = []
        for chunk_info in metadata.get("chunks", []):
            chunk_file = content_dir / chunk_info["file"]
            if chunk_file.exists():
                with open(chunk_file, "r", encoding="utf-8") as f:
                    all_text.append(f.read())
        
        return "\n".join(all_text)

# Test the document processor
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 3:
        print("Usage: python document_processor.py <repository_key> <file_path>")
        sys.exit(1)
    
    repo_key = sys.argv[1]
    file_path = sys.argv[2]
    
    processor = DocumentProcessor()
    
    # Process with automatic classification
    result = processor.process_document_with_classification(file_path, repo_key)
    print(f"Processing result: {result}")
    
    # List documents in repository
    documents = processor.list_documents(repo_key)
    print(f"Documents in repository: {len(documents)}")
    for doc in documents:
        print(f"- {doc.get('filename', 'Unknown')} ({doc.get('id', 'Unknown')})")