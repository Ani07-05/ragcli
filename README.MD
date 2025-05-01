# RAG Document Assistant

A system that helps you ask questions about your documents and get accurate answers based on their content. This system works with PDFs, logs, and text files to provide information extraction through natural language queries.

## Table of Contents

- [Introduction](#introduction)
- [System Components](#system-components)
- [Step-by-Step Installation](#step-by-step-installation)
- [Running the Project](#running-the-project)
- [Components with Code Snippets](#components-with-code-snippets)
- [CLI Usage Guide](#cli-usage-guide)
- [Common Workflows](#common-workflows)
- [Adding More Documents](#adding-more-documents)
- [Improving the Knowledge Base](#improving-the-knowledge-base)
- [Troubleshooting](#troubleshooting)

## Introduction

The RAG Document Assistant lets you upload documents, organize them into repositories, and ask questions about them using natural language. The system processes your documents, creates searchable indexes, and uses Llama 3 to generate answers based on the content of your documents.

A **repository** is simply a collection of related documents (like a folder). For example, you might have a "technical_manuals" repository for equipment documentation or a "system_logs" repository for application logs.

## System Components

The system consists of these main components:

1. **Repository Manager**: Organizes document collections
2. **Document Processor**: Handles document upload and processing
3. **Document Classifier**: Identifies document types automatically
4. **Vector Store Manager**: Creates and searches document embeddings
5. **Document Grader**: Improves retrieval quality
6. **RAG Engine**: Generates answers from retrieved contexts
7. **CLI Interface**: Provides user-friendly access to all features

## Step-by-Step Installation

### 1. Set Up Your Environment

First, create a project directory and navigate to it:
```bash
mkdir rag-document-assistant
cd rag-document-assistant
```

Create a virtual environment:
```bash
# For Windows
python -m venv venv
venv\Scripts\activate

# For Mac/Linux
python -m venv venv
source venv/bin/activate
```

### 2. Create Project Structure

Create the necessary directories and files:
```bash
mkdir -p src data/repositories
```

### 3. Install Dependencies

Create a `requirements.txt` file with these contents:
```
llama-index>=0.9.0
llama-cloud-services>=0.0.7
sentence-transformers>=2.2.2
faiss-cpu>=1.7.4
python-dotenv>=1.0.0
colorama>=0.4.6
tqdm>=4.66.1
```

Install the dependencies:
```bash
pip install -r requirements.txt
```

### 4. Set Up Ollama for Llama 3

Install Ollama from [https://ollama.com/download](https://ollama.com/download)

After installation, pull the Llama 3 model:
```bash
# Start Ollama server
ollama serve

# In another terminal, pull the Llama 3 model
ollama pull llama3
```

### 5. Get LlamaCloud API Key

Register at [LlamaIndex Cloud](https://cloud.llamaindex.ai/) to get your API key for LlamaParse.

Create a `.env` file in your project root:
```
LLAMA_CLOUD_API_KEY=your_llama_cloud_api_key_here
```

### 6. Download Project Files

Create the project files as described in the [Components with Code Snippets](#components-with-code-snippets) section below, or download the project files from the repository.

## Running the Project

### 1. Start Ollama Server

Make sure the Ollama server is running:
```bash
ollama serve
```

### 2. Launch the CLI Interface

Run the CLI interface:
```bash
python rag_cli.py
```

### 3. Basic Workflow

Follow this sequence to get started:

1. Create a repository: Main Menu > 1 > 2
2. Add documents to the repository: Main Menu > 2 > 2
3. Index the repository: Main Menu > 1 > 5
4. Ask questions about your documents: Main Menu > 3 > 1

## Components with Code Snippets

### Repository Manager (`src/repository_manager.py`)

Manages document repositories - creates, lists, and organizes collections of documents.

```python
import json
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

class RepositoryManager:
    def __init__(self, base_dir: str = "./data/repositories"):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(exist_ok=True, parents=True)
        self.metadata_file = Path("./data/metadata.json")
        self._initialize()
    
    def _initialize(self):
        """Initialize repositories directory and metadata"""
        if not self.metadata_file.exists():
            # Create initial metadata structure
            metadata = {
                "repositories": {},
                "created_at": datetime.now().isoformat()
            }
            self._save_metadata(metadata)
        
        # Load existing metadata
        self.metadata = self._load_metadata()
    
    def create_repository(self, key: str, description: str = "") -> str:
        """Create a new repository"""
        if key in self.metadata["repositories"]:
            print(f"Repository '{key}' already exists")
            return key
        
        # Create repository directory
        repo_path = self._get_repo_path(key)
        repo_path.mkdir(parents=True, exist_ok=True)
        
        # Create subdirectories
        (repo_path / "documents").mkdir(exist_ok=True)
        (repo_path / "index").mkdir(exist_ok=True)
        
        # Update metadata
        timestamp = datetime.now().isoformat()
        self.metadata["repositories"][key] = {
            "description": description,
            "created_at": timestamp,
            "last_updated": timestamp,
            "document_count": 0
        }
        self._save_metadata()
        
        print(f"Created repository: {key}")
        return key
    
    # Additional methods omitted for brevity
```

### Document Processor (`src/document_processor.py`)

Processes uploaded documents, extracts content, and stores them in repositories.

```python
import os
import json
import uuid
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
from llama_cloud_services import LlamaParse

class DocumentProcessor:
    def __init__(self):
        self.repo_manager = RepositoryManager()
        self.parser = LlamaParse(
            api_key=os.getenv("LLAMA_CLOUD_API_KEY"),
            result_type="markdown",
            verbose=True
        )
    
    def process_document_with_classification(self, 
                                           file_path: str, 
                                           repo_key: str, 
                                           document_metadata: Optional[Dict[str, Any]] = None) -> Dict:
        """Process a document with automatic classification"""
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
    
    # Additional methods omitted for brevity
```

### Document Classifier (`src/document_classifier.py`)

Identifies document types automatically to enable specialized processing.

```python
import os
import re
from pathlib import Path
from typing import Dict, Any

class DocumentClassifier:
    """Classifies documents by type for specialized processing"""
    
    @staticmethod
    def classify_document(file_path: str) -> Dict[str, Any]:
        """Classify a document by analyzing its content and extension"""
        file_name = os.path.basename(file_path)
        _, extension = os.path.splitext(file_name)
        extension = extension.lower()
        
        # Check file extension first
        if extension in ['.log']:
            doc_type = "log"
        elif extension in ['.pdf']:
            doc_type = "pdf"
        elif extension in ['.txt', '.md', '.rst']:
            # For text files, check if it's a log file
            doc_type = DocumentClassifier._analyze_text_content(file_path)
        else:
            # Default to standard document type
            doc_type = "document"
        
        return {
            "type": doc_type,
            "extension": extension,
            "specifics": DocumentClassifier._get_specifics(file_path, doc_type)
        }
    
    # Additional methods omitted for brevity
```

### Vector Store Manager (`src/vector_store_manager_local.py`)

Creates embeddings from document chunks and enables semantic search.

```python
import os
import json
from typing import List, Dict, Optional, Any
from pathlib import Path

from llama_index.core import VectorStoreIndex, Document, Settings
from llama_index.core import StorageContext, load_index_from_storage
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core.retrievers import VectorIndexRetriever
from llama_index.core.embeddings import resolve_embed_model

from src.repository_manager import RepositoryManager
from src.config import CHUNK_SIZE, CHUNK_OVERLAP, EMBEDDING_MODEL

class VectorStoreManager:
    """Manages vector stores for document repositories using embeddings"""
    
    def __init__(self):
        self.repo_manager = RepositoryManager()
        
        # Set up the embedding model as default in Settings
        embed_model = resolve_embed_model("local:" + EMBEDDING_MODEL)
        Settings.embed_model = embed_model
    
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
            return False
    
    # Additional methods omitted for brevity
```

### Document Grader (`src/document_grader.py`)

Improves retrieval quality by scoring and reranking documents.

```python
import re
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime

class DocumentGrader:
    """Provides document grading functionality to improve retrieval quality"""
    
    @staticmethod
    def grade_retrieved_documents(
        query: str,
        retrieved_docs: List[Dict[str, Any]],
        doc_type: str = "standard"
    ) -> List[Dict[str, Any]]:
        """Grade and rerank retrieved documents based on relevance to query"""
        if not retrieved_docs:
            return []
        
        # Select appropriate grading method based on document type
        if doc_type == "log":
            return DocumentGrader._grade_log_documents(query, retrieved_docs)
        else:
            return DocumentGrader._grade_standard_documents(query, retrieved_docs)
    
    @staticmethod
    def _grade_standard_documents(
        query: str,
        retrieved_docs: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Grade standard documents"""
        
        # Extract query keywords (remove common words)
        query_keywords = DocumentGrader._extract_keywords(query)
        
        for doc in retrieved_docs:
            # Start with base vector similarity score
            base_score = doc.get("score", 0.0)
            
            # Get document text
            text = doc.get("text", "")
            
            # 1. Keyword presence boost
            keyword_matches = sum(1 for keyword in query_keywords if keyword.lower() in text.lower())
            keyword_score = min(keyword_matches / max(len(query_keywords), 1), 1.0) * 0.3
            
            # Calculate final score (base + boosts)
            # (additional calculations omitted for brevity)
            final_score = (base_score * 0.5) + keyword_score + length_score + structure_score
            
            # Update document score
            doc["score"] = min(final_score, 1.0)  # Cap at 1.0
            
            # Add grading explanation
            doc["grading"] = {
                "base_score": base_score,
                "keyword_score": keyword_score,
                "length_score": length_score,
                "structure_score": structure_score,
                "final_score": doc["score"]
            }
        
        # Sort by score in descending order
        return sorted(retrieved_docs, key=lambda x: x["score"], reverse=True)
    
    # Additional methods omitted for brevity
```

### RAG Engine (`src/rag_engine.py`)

Combines retrieval and generation to answer questions based on document content.

```python
from typing import List, Dict, Any, Optional
from src.vector_store_manager_local import VectorStoreManager
from src.llama3_client import Llama3Client
from src.document_grader import DocumentGrader

class RAGEngine:
    """Retrieval-Augmented Generation engine using Llama 3 with specialized prompting"""
    
    def __init__(self, temperature: float = 0.7):
        self.vector_store = VectorStoreManager()
        self.llm = Llama3Client()
        self.temperature = temperature
        self.document_grader = DocumentGrader()
    
    def query(self, 
             repo_key: str, 
             query_text: str, 
             top_k: int = 5,
             use_grading: bool = True) -> Dict[str, Any]:
        """Query a repository using RAG"""
        # Step 1: Retrieve relevant documents
        retrieved_docs = self.vector_store.search_repository(
            repo_key=repo_key,
            query=query_text,
            top_k=top_k * 2 if use_grading else top_k
        )
        
        # Step 2: Apply document grading if enabled
        if use_grading and retrieved_docs:
            # Determine document type
            doc_type = "standard"
            if retrieved_docs and "metadata" in retrieved_docs[0]:
                doc_type = retrieved_docs[0]["metadata"].get("document_type", "standard")
            
            # Grade and rerank documents
            retrieved_docs = self.document_grader.grade_retrieved_documents(
                query_text, retrieved_docs, doc_type
            )
            
            # Take top k after grading
            retrieved_docs = retrieved_docs[:top_k]
        
        # Step 3: Generate response based on retrieved documents
        if not retrieved_docs:
            return {
                "answer": "I couldn't find any relevant information in the repository to answer your question.",
                "sources": [],
                "confidence": 0.0
            }
        
        # Extract text from retrieved documents
        context_chunks = [doc["text"] for doc in retrieved_docs]
        
        # Determine document type to use specialized prompting
        doc_type = "standard"
        if retrieved_docs and "metadata" in retrieved_docs[0]:
            doc_type = retrieved_docs[0]["metadata"].get("document_type", "standard")
        
        # Step 4: Generate answer using appropriate template
        if doc_type == "log":
            answer = self._generate_log_answer(query_text, context_chunks, retrieved_docs)
        else:
            answer = self._generate_standard_answer(query_text, context_chunks, retrieved_docs)
        
        # Additional steps omitted for brevity
        
        return {
            "answer": answer,
            "sources": sources,
            "confidence": confidence
        }
    
    # Additional methods omitted for brevity
```

### Llama 3 Client (`src/llama3_client.py`)

Connects to Ollama to generate text using Llama 3.

```python
import requests
import json
from typing import Dict, List, Optional, Union
from src.config import OLLAMA_BASE_URL, OLLAMA_MODEL

class Llama3Client:
    """Simple client for interacting with Llama 3 via Ollama"""
    
    def __init__(self, 
                 base_url: str = OLLAMA_BASE_URL, 
                 model: str = OLLAMA_MODEL):
        self.base_url = base_url
        self.model = model
        self.generate_url = f"{base_url}/api/generate"
        
    def generate(self, 
                prompt: str, 
                system_prompt: Optional[str] = None,
                temperature: float = 0.7, 
                max_tokens: int = 1000) -> str:
        """Generate text using Llama 3"""
        
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens
            }
        }
        
        if system_prompt:
            payload["system"] = system_prompt
            
        try:
            response = requests.post(self.generate_url, json=payload)
            response.raise_for_status()
            return response.json().get("response", "")
        except Exception as e:
            print(f"Error generating text: {e}")
            return f"Error: {str(e)}"
    
    # Additional methods omitted for brevity
```

### Configuration (`src/config.py`)

Stores system configuration and settings.

```python
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# API Keys
LLAMA_CLOUD_API_KEY = os.getenv("LLAMA_CLOUD_API_KEY")

# Directories
BASE_DIR = Path(__file__).parent.parent
REPOSITORIES_DIR = BASE_DIR / "data" / "repositories"
METADATA_FILE = BASE_DIR / "data" / "metadata.json"

# Ensure directories exist
REPOSITORIES_DIR.mkdir(parents=True, exist_ok=True)

# Model settings
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"  # Efficient embedding model
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200

# Ollama settings
OLLAMA_BASE_URL = "http://localhost:11434"
OLLAMA_MODEL = "llama3"  # Use "llama3:70b" for the larger model if available
```

### CLI Interface (`rag_cli.py`)

Provides a user-friendly menu-driven interface to interact with the system.

```python
#!/usr/bin/env python3
import os
import sys
import time
from pathlib import Path
import json
from typing import List, Dict, Any, Optional

# Import our RAG components
from src.repository_manager import RepositoryManager
from src.document_processor import DocumentProcessor
from src.vector_store_manager_local import VectorStoreManager
from src.rag_engine import RAGEngine
from src.document_classifier import DocumentClassifier

# Try to import colorama for colored output
try:
    from colorama import init, Fore, Back, Style
    init()  # Initialize colorama
    COLORS_AVAILABLE = True
except ImportError:
    COLORS_AVAILABLE = False
    # Define dummy color constants
    class DummyFore:
        def __getattr__(self, name):
            return ""
    Fore = DummyFore()
    Style = DummyFore()

class SimpleRAGCLI:
    """A simple menu-driven CLI for the RAG system"""
    
    def __init__(self):
        self.repo_manager = RepositoryManager()
        self.doc_processor = DocumentProcessor()
        self.vector_store = VectorStoreManager()
        self.rag_engine = RAGEngine()
        self.current_repo = None
    
    def run(self):
        """Run the CLI application"""
        while True:
            self.print_menu()
    
    # Additional methods omitted for brevity

if __name__ == "__main__":
    cli = SimpleRAGCLI()
    cli.run()
```

## CLI Usage Guide

### Main Menu Navigation

After running `python rag_cli.py`, you'll see the main menu:

```
╔══════════════════════════════════════════╗
║ RAG Document Assistant                  ║
╚══════════════════════════════════════════╝

Main Menu:
  1. Repository Management
  2. Document Management
  3. Ask Questions (RAG)
  4. System Information
  0. Exit
```

Use number keys to select menu options and follow the prompts.

### Creating a Repository

```
[Main Menu] > 1 (Repository Management)
[Repository Management] > 2 (Create new repository)
Enter repository key: my_docs
Enter repository description: My documents collection
```

### Adding a Document

```
[Main Menu] > 2 (Document Management)
[Document Management] > 2 (Add new document)
Enter the path to the document file: C:\Users\me\Documents\report.pdf
```

### Indexing a Repository

```
[Main Menu] > 1 (Repository Management)
[Repository Management] > 5 (Index repository)
```

### Asking a Question

```
[Main Menu] > 3 (Ask Questions)
[Ask Questions] > 1 (Ask a question)
Enter your question: What are the main findings in the report?
```

## Common Workflows

### Process for Adding Documents and Querying

1. **Create a Repository**
   - Main Menu > 1 > 2
   - Enter repository key (e.g., "technical_manuals")
   - Enter description (optional)

2. **Add Documents to Repository**
   - Main Menu > 2 > 2
   - Enter path to document file
   - Repeat for all documents you want to add

3. **Index the Repository**
   - Main Menu > 1 > 5
   - Confirm indexing operation

4. **Ask Questions**
   - Main Menu > 3 > 1
   - Enter your question
   - Review answer and sources

### Working with Multiple Repositories

1. **Create Different Repositories for Different Topics**
   - Create a repository for technical documents
   - Create another for logs
   - Create another for research papers

2. **Select Repository Before Operations**
   - Main Menu > 1 > 3
   - Choose the repository you want to work with

3. **Switch Between Repositories as Needed**
   - Main Menu > 1 > 3
   - Select a different repository

## Adding More Documents

### Supported Document Types

- **PDF Files** (*.pdf): Research papers, manuals, books
- **Log Files** (*.log): System logs, application logs, event logs
- **Text Files** (*.txt, *.md): Plain text documents, notes

### Adding Documents to Repositories

1. **Through the CLI**:
   - Main Menu > 2 > 2
   - Enter path to document
   - Optionally index after adding

2. **For Multiple Documents**:
   - Add documents one by one
   - Index the repository after adding all documents

### Tips for Document Organization

- Group related documents in the same repository
- Use descriptive repository names
- Index repositories after adding or updating documents

## Improving the Knowledge Base

### Document Quality Tips

1. **Use High-Quality Documents**
   - More detailed documents provide better answers
   - Ensure documents contain the information you're interested in

2. **Organize Documents by Topic**
   - Create separate repositories for different subjects
   - This helps focus the search and improves answer quality

3. **Add a Variety of Document Types**
   - Include different perspectives
   - Mix detailed technical documents with summarized information

### Query Optimization

1. **Be Specific in Your Questions**
   - "What are the error codes in the system log?" works better than "Tell me about errors"

2. **Adjust Retrieval Settings**
   - Try different "top_k" values when asking questions
   - Enable document grading for better results

3. **Check Source Documents**
   - Review the source documents to verify information
   - Look at confidence scores to gauge reliability

## Troubleshooting

### Common Issues

1. **"No repository selected"**
   - Solution: Select a repository from Main Menu > 1 > 3

2. **"No documents found in repository"**
   - Solution: Add documents to the repository from Main Menu > 2 > 2

3. **"Repository is not indexed"**
   - Solution: Index the repository from Main Menu > 1 > 5

4. **Document processing fails**
   - Check file format and permissions
   - Ensure LLAMA_CLOUD_API_KEY is set correctly in .env file

5. **Poor answer quality**
   - Add more comprehensive documents
   - Try reformulating your question
   - Make sure you're querying the right repository