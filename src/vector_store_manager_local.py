import os
import json
from typing import List, Dict, Optional, Any
from pathlib import Path

from llama_index.core import VectorStoreIndex, Document, Settings
from llama_index.core import StorageContext, load_index_from_storage
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core.retrievers import VectorIndexRetriever
from llama_index.core.embeddings import resolve_embed_model

from repository_manager import RepositoryManager
from config import CHUNK_SIZE, CHUNK_OVERLAP, EMBEDDING_MODEL

class VectorStoreManager:
    """Manages vector stores for document repositories using embeddings"""
    
    def __init__(self):
        self.repo_manager = RepositoryManager()
        
        # Set up the embedding model as default in Settings
        # Using LlamaIndex's built-in helpers for HuggingFace embeddings
        embed_model = resolve_embed_model("local:" + EMBEDDING_MODEL)
        Settings.embed_model = embed_model
    
    def _load_document_content(self, repo_key: str, doc_id: str) -> List[Document]:
        """Load document content from a repository"""
        repo_path = self.repo_manager.get_repository_path(repo_key)
        if repo_path is None:
            return []
        
        doc_dir = repo_path / "documents" / doc_id
        if not doc_dir.exists():
            return []
        
        metadata_file = doc_dir / "metadata.json"
        if not metadata_file.exists():
            return []
        
        with open(metadata_file, "r") as f:
            metadata = json.load(f)
        
        content_dir = doc_dir / "content"
        
        # Check if this is a log document
        is_log_document = metadata.get("document_type") == "log"
        
        documents = []
        if is_log_document:
            # For log documents, look for chunks instead of pages
            for chunk_info in metadata.get("chunks", []):
                chunk_file = content_dir / chunk_info["file"]
                if chunk_file.exists():
                    with open(chunk_file, "r", encoding="utf-8", errors="ignore") as f:
                        content = f.read()
                        
                        doc = Document(
                            text=content,
                            metadata={
                                "doc_id": doc_id,
                                "filename": metadata.get("filename", ""),
                                "chunk_num": chunk_info.get("chunk_num", 0),
                                "repository": repo_key,
                                "document_type": "log"
                            }
                        )
                        documents.append(doc)
        else:
            # For standard documents, look for pages
            for page_info in metadata.get("pages", []):
                page_file = content_dir / page_info["file"]
                if page_file.exists():
                    with open(page_file, "r", encoding="utf-8") as f:
                        content = f.read()
                        
                        doc = Document(
                            text=content,
                            metadata={
                                "doc_id": doc_id,
                                "filename": metadata.get("filename", ""),
                                "page_num": page_info.get("page_num", 0),
                                "repository": repo_key
                            }
                        )
                        documents.append(doc)
        
        if not documents:
            print(f"Warning: No content files found for document {doc_id}")
            # Debug: Print what we were looking for
            if is_log_document:
                chunks = metadata.get("chunks", [])
                print(f"Was looking for {len(chunks)} log chunks")
                if chunks:
                    chunk_file = chunks[0]['file']
                    chunk_path = content_dir / chunk_file
                    print(f"For example: {chunk_file} in {content_dir}")
                    print(f"File exists: {chunk_path.exists()}")
                    
                    # List files in content directory
                    print("Files in content directory:")
                    for file in content_dir.iterdir():
                        print(f"  - {file.name}")
            else:
                pages = metadata.get("pages", [])
                print(f"Was looking for {len(pages)} document pages")
                if pages:
                    print(f"For example: {pages[0]['file']} in {content_dir}")
        
        return documents
    
    def _get_index_path(self, repo_key: str) -> Path:
        """Get the path to the index directory for a repository"""
        repo_path = self.repo_manager.get_repository_path(repo_key)
        if repo_path is None:
            raise ValueError(f"Repository '{repo_key}' not found")
        
        return repo_path / "index"
    
    def index_document(self, repo_key: str, doc_id: str) -> bool:
        """Index a document in a repository"""
        print(f"Indexing document {doc_id} in repository {repo_key}")
        
        # Load document content
        documents = self._load_document_content(repo_key, doc_id)
        if not documents:
            print(f"No content found for document {doc_id}")
            return False
        
        # Create or load existing index
        index_path = self._get_index_path(repo_key)
        
        try:
            # Create node parser
            node_parser = SentenceSplitter(
                chunk_size=CHUNK_SIZE,
                chunk_overlap=CHUNK_OVERLAP
            )
            
            if (index_path / "docstore.json").exists():
                # Load existing index
                storage_context = StorageContext.from_defaults(persist_dir=str(index_path))
                index = load_index_from_storage(storage_context)
                
                # Insert new documents
                for doc in documents:
                    index.insert(doc)
            else:
                # Create new index
                index = VectorStoreIndex.from_documents(
                    documents,
                    node_parser=node_parser,
                    show_progress=True
                )
            
            # Save index
            index.storage_context.persist(persist_dir=str(index_path))
            
            print(f"Successfully indexed document {doc_id}")
            return True
            
        except Exception as e:
            print(f"Error indexing document: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
    
    def index_repository(self, repo_key: str) -> Dict[str, bool]:
        """Index all documents in a repository"""
        from document_processor import DocumentProcessor
        
        processor = DocumentProcessor()
        documents = processor.list_documents(repo_key)
        
        results = {}
        for doc in documents:
            doc_id = doc.get("id")
            if doc_id:
                results[doc_id] = self.index_document(repo_key, doc_id)
        
        return results
    
    def search_repository(self, 
                         repo_key: str, 
                         query: str, 
                         top_k: int = 5) -> List[Dict[str, Any]]:
        """Search a repository for relevant documents"""
        print(f"Searching repository {repo_key} for: {query}")
        
        index_path = self._get_index_path(repo_key)
        if not (index_path / "docstore.json").exists():
            print(f"No index found for repository {repo_key}")
            return []
        
        try:
            # Load index
            storage_context = StorageContext.from_defaults(persist_dir=str(index_path))
            index = load_index_from_storage(storage_context)
            
            # Create retriever
            retriever = VectorIndexRetriever(
                index=index,
                similarity_top_k=top_k
            )
            
            # Retrieve relevant nodes
            nodes = retriever.retrieve(query)
            
            # Format results
            results = []
            for node in nodes:
                results.append({
                    "score": node.score if hasattr(node, "score") else 0.0,
                    "text": node.get_text(),
                    "metadata": node.metadata
                })
            
            return results
            
        except Exception as e:
            print(f"Error searching repository: {e}")
            return []