#!/usr/bin/env python3
import os
import sys
import time
from pathlib import Path
import json
from typing import List, Dict, Any, Optional

# Import our RAG components
from repository_manager import RepositoryManager
from document_processor import DocumentProcessor
from vector_store_manager_local import VectorStoreManager
from rag_engine import RAGEngine
from document_classifier import DocumentClassifier

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
    
    def print_header(self):
        """Print the application header"""
        os.system('cls' if os.name == 'nt' else 'clear')
        print(f"{Fore.CYAN}╔══════════════════════════════════════════╗{Style.RESET_ALL}")
        print(f"{Fore.CYAN}║{Style.BRIGHT} RAG Document Assistant {Style.RESET_ALL}{Fore.CYAN}                 ║{Style.RESET_ALL}")
        print(f"{Fore.CYAN}╚══════════════════════════════════════════╝{Style.RESET_ALL}")
        
        if self.current_repo:
            print(f"Current repository: {Fore.GREEN}{self.current_repo}{Style.RESET_ALL}\n")
        else:
            print(f"Current repository: {Fore.YELLOW}None selected{Style.RESET_ALL}\n")
    
    def print_menu(self):
        """Print the main menu"""
        self.print_header()
        
        print(f"{Fore.YELLOW}Main Menu:{Style.RESET_ALL}")
        print(f"  {Fore.WHITE}1.{Style.RESET_ALL} Repository Management")
        print(f"  {Fore.WHITE}2.{Style.RESET_ALL} Document Management")
        print(f"  {Fore.WHITE}3.{Style.RESET_ALL} Ask Questions (RAG)")
        print(f"  {Fore.WHITE}4.{Style.RESET_ALL} System Information")
        print(f"  {Fore.WHITE}0.{Style.RESET_ALL} Exit")
        
        choice = input("\nEnter your choice (0-4): ")
        
        if choice == "1":
            self.repository_menu()
        elif choice == "2":
            self.document_menu()
        elif choice == "3":
            self.query_menu()
        elif choice == "4":
            self.system_info()
        elif choice == "0":
            print("\nExiting RAG Document Assistant. Goodbye!")
            sys.exit(0)
        else:
            print(f"\n{Fore.RED}Invalid choice. Please try again.{Style.RESET_ALL}")
            input("Press Enter to continue...")
    
    def repository_menu(self):
        """Repository management menu"""
        while True:
            self.print_header()
            
            print(f"{Fore.YELLOW}Repository Management:{Style.RESET_ALL}")
            print(f"  {Fore.WHITE}1.{Style.RESET_ALL} List all repositories")
            print(f"  {Fore.WHITE}2.{Style.RESET_ALL} Create new repository")
            print(f"  {Fore.WHITE}3.{Style.RESET_ALL} Select repository")
            print(f"  {Fore.WHITE}4.{Style.RESET_ALL} View repository details")
            print(f"  {Fore.WHITE}5.{Style.RESET_ALL} Index repository")
            print(f"  {Fore.WHITE}0.{Style.RESET_ALL} Back to main menu")
            
            choice = input("\nEnter your choice (0-5): ")
            
            if choice == "1":
                self.list_repositories()
            elif choice == "2":
                self.create_repository()
            elif choice == "3":
                self.select_repository()
            elif choice == "4":
                self.view_repository_details()
            elif choice == "5":
                self.index_repository()
            elif choice == "0":
                break
            else:
                print(f"\n{Fore.RED}Invalid choice. Please try again.{Style.RESET_ALL}")
                input("Press Enter to continue...")
    
    def document_menu(self):
        """Document management menu"""
        while True:
            self.print_header()
            
            print(f"{Fore.YELLOW}Document Management:{Style.RESET_ALL}")
            print(f"  {Fore.WHITE}1.{Style.RESET_ALL} List documents in current repository")
            print(f"  {Fore.WHITE}2.{Style.RESET_ALL} Add new document")
            print(f"  {Fore.WHITE}3.{Style.RESET_ALL} View document details")
            print(f"  {Fore.WHITE}0.{Style.RESET_ALL} Back to main menu")
            
            choice = input("\nEnter your choice (0-3): ")
            
            if choice == "1":
                self.list_documents()
            elif choice == "2":
                self.add_document()
            elif choice == "3":
                self.view_document_details()
            elif choice == "0":
                break
            else:
                print(f"\n{Fore.RED}Invalid choice. Please try again.{Style.RESET_ALL}")
                input("Press Enter to continue...")
    
    def query_menu(self):
        """Query menu for RAG functionality"""
        while True:
            self.print_header()
            
            print(f"{Fore.YELLOW}Ask Questions (RAG):{Style.RESET_ALL}")
            print(f"  {Fore.WHITE}1.{Style.RESET_ALL} Ask a question")
            print(f"  {Fore.WHITE}2.{Style.RESET_ALL} View query history")
            print(f"  {Fore.WHITE}0.{Style.RESET_ALL} Back to main menu")
            
            choice = input("\nEnter your choice (0-2): ")
            
            if choice == "1":
                self.ask_question()
            elif choice == "2":
                print(f"\n{Fore.YELLOW}Query history not implemented yet.{Style.RESET_ALL}")
                input("Press Enter to continue...")
            elif choice == "0":
                break
            else:
                print(f"\n{Fore.RED}Invalid choice. Please try again.{Style.RESET_ALL}")
                input("Press Enter to continue...")
    
    def list_repositories(self):
        """List all repositories"""
        self.print_header()
        print(f"{Fore.YELLOW}Repositories:{Style.RESET_ALL}\n")
        
        repos = self.repo_manager.list_repositories()
        
        if not repos:
            print("No repositories found.")
            input("\nPress Enter to continue...")
            return
        
        for i, repo in enumerate(repos, 1):
            key = repo.get("key", "Unknown")
            desc = repo.get("description", "")
            doc_count = repo.get("document_count", 0)
            
            if key == self.current_repo:
                print(f"{Fore.GREEN}➤ {i}. {key}{Style.RESET_ALL} ({doc_count} documents)")
            else:
                print(f"  {i}. {key} ({doc_count} documents)")
            
            if desc:
                print(f"     Description: {desc}")
        
        input("\nPress Enter to continue...")
    
    def create_repository(self):
        """Create a new repository"""
        self.print_header()
        print(f"{Fore.YELLOW}Create New Repository:{Style.RESET_ALL}\n")
        
        key = input("Enter repository key (no spaces, lowercase): ").strip()
        
        if not key:
            print(f"\n{Fore.RED}Repository key cannot be empty.{Style.RESET_ALL}")
            input("\nPress Enter to continue...")
            return
        
        if " " in key:
            print(f"\n{Fore.RED}Repository key cannot contain spaces.{Style.RESET_ALL}")
            input("\nPress Enter to continue...")
            return
        
        description = input("Enter repository description (optional): ").strip()
        
        # Create repository
        try:
            self.repo_manager.create_repository(key, description)
            print(f"\n{Fore.GREEN}Repository '{key}' created successfully.{Style.RESET_ALL}")
            
            # Set as current repository
            self.current_repo = key
            print(f"Repository '{key}' is now the current repository.")
        except Exception as e:
            print(f"\n{Fore.RED}Error creating repository: {str(e)}{Style.RESET_ALL}")
        
        input("\nPress Enter to continue...")
    
    def select_repository(self):
        """Select a repository to work with"""
        self.print_header()
        print(f"{Fore.YELLOW}Select Repository:{Style.RESET_ALL}\n")
        
        repos = self.repo_manager.list_repositories()
        
        if not repos:
            print("No repositories found.")
            input("\nPress Enter to continue...")
            return
        
        for i, repo in enumerate(repos, 1):
            key = repo.get("key", "Unknown")
            doc_count = repo.get("document_count", 0)
            
            if key == self.current_repo:
                print(f"{Fore.GREEN}➤ {i}. {key}{Style.RESET_ALL} ({doc_count} documents)")
            else:
                print(f"  {i}. {key} ({doc_count} documents)")
        
        print("\nEnter the number of the repository to select, or 0 to cancel.")
        choice = input("Choice: ").strip()
        
        if choice == "0":
            return
        
        try:
            choice_idx = int(choice) - 1
            if 0 <= choice_idx < len(repos):
                self.current_repo = repos[choice_idx].get("key")
                print(f"\n{Fore.GREEN}Selected repository: {self.current_repo}{Style.RESET_ALL}")
            else:
                print(f"\n{Fore.RED}Invalid choice.{Style.RESET_ALL}")
        except ValueError:
            print(f"\n{Fore.RED}Invalid input. Please enter a number.{Style.RESET_ALL}")
        
        input("\nPress Enter to continue...")
    
    def view_repository_details(self):
        """View details of the current repository"""
        self.print_header()
        
        if not self.current_repo:
            print(f"{Fore.RED}No repository selected. Please select a repository first.{Style.RESET_ALL}")
            input("\nPress Enter to continue...")
            return
        
        print(f"{Fore.YELLOW}Repository Details:{Style.RESET_ALL}\n")
        
        repos = self.repo_manager.list_repositories()
        repo_info = next((r for r in repos if r.get("key") == self.current_repo), None)
        
        if not repo_info:
            print(f"{Fore.RED}Repository information not found.{Style.RESET_ALL}")
            input("\nPress Enter to continue...")
            return
        
        print(f"Key: {Fore.GREEN}{repo_info.get('key')}{Style.RESET_ALL}")
        print(f"Description: {repo_info.get('description', 'None')}")
        print(f"Created: {repo_info.get('created_at', 'Unknown')}")
        print(f"Last updated: {repo_info.get('last_updated', 'Unknown')}")
        print(f"Document count: {repo_info.get('document_count', 0)}")
        
        # Get repository path
        repo_path = self.repo_manager.get_repository_path(self.current_repo)
        if repo_path:
            print(f"Storage path: {repo_path}")
            
            # Check if index exists
            index_path = repo_path / "index" / "docstore.json"
            if index_path.exists():
                print(f"Index status: {Fore.GREEN}Indexed{Style.RESET_ALL}")
            else:
                print(f"Index status: {Fore.YELLOW}Not indexed{Style.RESET_ALL}")
        
        input("\nPress Enter to continue...")
    
    def index_repository(self):
        """Index the current repository"""
        self.print_header()
        
        if not self.current_repo:
            print(f"{Fore.RED}No repository selected. Please select a repository first.{Style.RESET_ALL}")
            input("\nPress Enter to continue...")
            return
        
        print(f"{Fore.YELLOW}Indexing Repository:{Style.RESET_ALL} {self.current_repo}\n")
        
        # Check if there are documents
        documents = self.doc_processor.list_documents(self.current_repo)
        if not documents:
            print(f"{Fore.RED}No documents found in repository. Please add documents first.{Style.RESET_ALL}")
            input("\nPress Enter to continue...")
            return
        
        print(f"Found {len(documents)} documents to index.")
        choice = input("Do you want to proceed with indexing? (y/n): ").strip().lower()
        
        if choice != 'y':
            print("\nIndexing cancelled.")
            input("\nPress Enter to continue...")
            return
        
        print("\nIndexing repository... This may take a while.\n")
        
        try:
            results = self.vector_store.index_repository(self.current_repo)
            
            # Count successes and failures
            successes = sum(1 for success in results.values() if success)
            failures = sum(1 for success in results.values() if not success)
            
            print(f"\n{Fore.GREEN}Indexing complete:{Style.RESET_ALL}")
            print(f"  - Successfully indexed: {successes} documents")
            
            if failures > 0:
                print(f"  - {Fore.RED}Failed to index: {failures} documents{Style.RESET_ALL}")
        except Exception as e:
            print(f"\n{Fore.RED}Error during indexing: {str(e)}{Style.RESET_ALL}")
        
        input("\nPress Enter to continue...")
    
    def list_documents(self):
        """List documents in the current repository"""
        self.print_header()
        
        if not self.current_repo:
            print(f"{Fore.RED}No repository selected. Please select a repository first.{Style.RESET_ALL}")
            input("\nPress Enter to continue...")
            return
        
        print(f"{Fore.YELLOW}Documents in Repository:{Style.RESET_ALL} {self.current_repo}\n")
        
        documents = self.doc_processor.list_documents(self.current_repo)
        
        if not documents:
            print("No documents found in repository.")
            input("\nPress Enter to continue...")
            return
        
        for i, doc in enumerate(documents, 1):
            doc_id = doc.get("id", "Unknown")
            filename = doc.get("filename", "Unknown")
            doc_type = doc.get("document_type", "standard")
            
            if doc_type == "log":
                print(f"  {i}. {Fore.CYAN}[LOG]{Style.RESET_ALL} {filename}")
            else:
                print(f"  {i}. {Fore.MAGENTA}[DOC]{Style.RESET_ALL} {filename}")
        
        input("\nPress Enter to continue...")
    
    def add_document(self):
        """Add a document to the current repository"""
        self.print_header()
        
        if not self.current_repo:
            print(f"{Fore.RED}No repository selected. Please select a repository first.{Style.RESET_ALL}")
            input("\nPress Enter to continue...")
            return
        
        print(f"{Fore.YELLOW}Add Document to Repository:{Style.RESET_ALL} {self.current_repo}\n")
        
        file_path = input("Enter the path to the document file: ").strip()
        
        if not file_path:
            print(f"\n{Fore.RED}File path cannot be empty.{Style.RESET_ALL}")
            input("\nPress Enter to continue...")
            return
        
        # Check if file exists
        file_path = Path(file_path)
        if not file_path.exists():
            print(f"\n{Fore.RED}File not found: {file_path}{Style.RESET_ALL}")
            input("\nPress Enter to continue...")
            return
        
        # Classify document
        print("\nClassifying document...")
        classification = DocumentClassifier.classify_document(str(file_path))
        doc_type = classification["type"]
        
        print(f"Document type: {Fore.CYAN if doc_type == 'log' else Fore.MAGENTA}{doc_type.upper()}{Style.RESET_ALL}")
        
        # Process document
        print("\nProcessing document... This may take a while for large files.\n")
        
        try:
            result = self.doc_processor.process_document_with_classification(
                file_path=str(file_path),
                repo_key=self.current_repo
            )
            
            if "error" in result:
                print(f"\n{Fore.RED}Error processing document: {result['error']}{Style.RESET_ALL}")
                input("\nPress Enter to continue...")
                return
            
            print(f"\n{Fore.GREEN}Document processed successfully:{Style.RESET_ALL}")
            print(f"  - ID: {result.get('id')}")
            print(f"  - Type: {result.get('document_type', 'standard')}")
            
            if doc_type == "log":
                chunks = result.get("total_chunks", 0)
                print(f"  - Chunks: {chunks}")
            else:
                pages = result.get("total_pages", 0)
                print(f"  - Pages: {pages}")
            
            # Ask if user wants to index the document now
            choice = input("\nDo you want to index this document now? (y/n): ").strip().lower()
            
            if choice == 'y':
                print("\nIndexing document...")
                success = self.vector_store.index_document(self.current_repo, result["id"])
                
                if success:
                    print(f"\n{Fore.GREEN}Document indexed successfully.{Style.RESET_ALL}")
                else:
                    print(f"\n{Fore.RED}Failed to index document.{Style.RESET_ALL}")
        except Exception as e:
            print(f"\n{Fore.RED}Error: {str(e)}{Style.RESET_ALL}")
        
        input("\nPress Enter to continue...")
    
    def view_document_details(self):
        """View details of a document"""
        self.print_header()
        
        if not self.current_repo:
            print(f"{Fore.RED}No repository selected. Please select a repository first.{Style.RESET_ALL}")
            input("\nPress Enter to continue...")
            return
        
        print(f"{Fore.YELLOW}View Document Details:{Style.RESET_ALL}\n")
        
        documents = self.doc_processor.list_documents(self.current_repo)
        
        if not documents:
            print("No documents found in repository.")
            input("\nPress Enter to continue...")
            return
        
        for i, doc in enumerate(documents, 1):
            doc_id = doc.get("id", "Unknown")
            filename = doc.get("filename", "Unknown")
            doc_type = doc.get("document_type", "standard")
            
            if doc_type == "log":
                print(f"  {i}. {Fore.CYAN}[LOG]{Style.RESET_ALL} {filename}")
            else:
                print(f"  {i}. {Fore.MAGENTA}[DOC]{Style.RESET_ALL} {filename}")
        
        print("\nEnter the number of the document to view, or 0 to cancel.")
        choice = input("Choice: ").strip()
        
        if choice == "0":
            return
        
        try:
            choice_idx = int(choice) - 1
            if 0 <= choice_idx < len(documents):
                self.display_document_details(documents[choice_idx])
            else:
                print(f"\n{Fore.RED}Invalid choice.{Style.RESET_ALL}")
                input("\nPress Enter to continue...")
        except ValueError:
            print(f"\n{Fore.RED}Invalid input. Please enter a number.{Style.RESET_ALL}")
            input("\nPress Enter to continue...")
    
    def display_document_details(self, doc_info):
        """Display detailed information about a document"""
        self.print_header()
        
        doc_id = doc_info.get("id", "Unknown")
        filename = doc_info.get("filename", "Unknown")
        doc_type = doc_info.get("document_type", "standard")
        
        print(f"{Fore.YELLOW}Document Details:{Style.RESET_ALL}\n")
        print(f"ID: {doc_id}")
        print(f"Filename: {filename}")
        print(f"Type: {Fore.CYAN if doc_type == 'log' else Fore.MAGENTA}{doc_type}{Style.RESET_ALL}")
        print(f"Processed at: {doc_info.get('processed_at', 'Unknown')}")
        
        if doc_type == "log":
            print(f"Total chunks: {doc_info.get('total_chunks', 0)}")
            print(f"Chunking strategy: {doc_info.get('chunk_strategy', 'Unknown')}")
            
            log_metadata = doc_info.get("log_metadata", {})
            if log_metadata:
                print("\nLog Metadata:")
                print(f"  Time period: {log_metadata.get('first_timestamp', 'Unknown')} to {log_metadata.get('last_timestamp', 'Unknown')}")
                print(f"  Timespan (hours): {log_metadata.get('timespan_hours', 'Unknown')}")
                print(f"  Error count: {log_metadata.get('error_count', 0)}")
                print(f"  Warning count: {log_metadata.get('warning_count', 0)}")
        else:
            print(f"Total pages: {doc_info.get('total_pages', 0)}")
        
        input("\nPress Enter to continue...")
    
    def ask_question(self):
        """Ask a question using RAG"""
        self.print_header()
        
        if not self.current_repo:
            print(f"{Fore.RED}No repository selected. Please select a repository first.{Style.RESET_ALL}")
            input("\nPress Enter to continue...")
            return
        
        print(f"{Fore.YELLOW}Ask a Question:{Style.RESET_ALL}\n")
        print(f"Repository: {Fore.GREEN}{self.current_repo}{Style.RESET_ALL}")
        
        # Check if repository is indexed
        repo_path = self.repo_manager.get_repository_path(self.current_repo)
        index_path = repo_path / "index" / "docstore.json"
        
        if not index_path.exists():
            print(f"\n{Fore.RED}Warning: Repository is not indexed. Results may be unavailable.{Style.RESET_ALL}")
            choice = input("Do you want to index the repository now? (y/n): ").strip().lower()
            
            if choice == 'y':
                print("\nIndexing repository...")
                self.vector_store.index_repository(self.current_repo)
            else:
                print("\nProceeding without indexing. Results may be limited.")
        
        # Get question
        print("\nEnter your question, or type 'exit' to return to menu:")
        query = input("> ").strip()
        
        if query.lower() == 'exit':
            return
        
        if not query:
            print(f"\n{Fore.RED}Question cannot be empty.{Style.RESET_ALL}")
            input("\nPress Enter to continue...")
            return
        
        # Configure RAG options
        print("\nRAG Options:")
        use_grading = input("Use document grading? (y/n, default: y): ").strip().lower() != 'n'
        try:
            top_k = int(input("Number of documents to retrieve (1-10, default: 5): ").strip() or 5)
            top_k = max(1, min(10, top_k))  # Limit between 1 and 10
        except ValueError:
            top_k = 5
            print("Invalid input. Using default value: 5")
        
        # Execute query
        print(f"\n{Fore.YELLOW}Searching for answer...{Style.RESET_ALL}")
        start_time = time.time()
        
        result = self.rag_engine.query(
            repo_key=self.current_repo,
            query_text=query,
            top_k=top_k,
            use_grading=use_grading
        )
        
        end_time = time.time()
        
        # Display results
        self.print_header()
        print(f"{Fore.YELLOW}Question:{Style.RESET_ALL} {query}")
        print(f"{Fore.YELLOW}Repository:{Style.RESET_ALL} {self.current_repo}")
        print(f"{Fore.YELLOW}Time:{Style.RESET_ALL} {end_time - start_time:.2f} seconds")
        print(f"{Fore.YELLOW}Confidence:{Style.RESET_ALL} {result.get('confidence', 0.0):.2f}")
        print(f"{Fore.YELLOW}Top-K documents:{Style.RESET_ALL} {top_k}")
        print(f"{Fore.YELLOW}Document grading:{Style.RESET_ALL} {'Enabled' if use_grading else 'Disabled'}")
        
        print(f"\n{Fore.GREEN}Answer:{Style.RESET_ALL}\n")
        print(result.get("answer", "No answer generated"))
        
        print(f"\n{Fore.YELLOW}Sources:{Style.RESET_ALL}")
        sources = result.get("sources", [])
        
        if not sources:
            print("No sources found.")
        else:
            for i, source in enumerate(sources, 1):
                score = source.get("score", 0.0)
                meta = source.get("metadata", {})
                
                if "filename" in meta:
                    if "page_num" in meta:
                        print(f"  {i}. {meta['filename']}, Page {meta['page_num']} (Score: {score:.2f})")
                    elif "chunk_num" in meta:
                        print(f"  {i}. {meta['filename']}, Chunk {meta['chunk_num']} (Score: {score:.2f})")
                    else:
                        print(f"  {i}. {meta['filename']} (Score: {score:.2f})")
                else:
                    print(f"  {i}. Source {i} (Score: {score:.2f})")
        
        # Ask if user wants to view source details
        choice = input("\nDo you want to view source details? (y/n): ").strip().lower()
        
        if choice == 'y' and sources:
            self.print_header()
            print(f"{Fore.YELLOW}Source Details:{Style.RESET_ALL}\n")
            
            for i, source in enumerate(sources, 1):
                score = source.get("score", 0.0)
                meta = source.get("metadata", {})
                text = source.get("text", "")
                grading = source.get("grading", {})
                
                print(f"{Fore.GREEN}Source {i}:{Style.RESET_ALL}")
                
                if "filename" in meta:
                    if "page_num" in meta:
                        print(f"  From: {meta['filename']}, Page {meta['page_num']}")
                    elif "chunk_num" in meta:
                        print(f"  From: {meta['filename']}, Chunk {meta['chunk_num']}")
                    else:
                        print(f"  From: {meta['filename']}")
                
                print(f"  Score: {score:.4f}")
                
                if grading:
                    print("  Grading details:")
                    for key, value in grading.items():
                        if isinstance(value, float):
                            print(f"    - {key}: {value:.4f}")
                        else:
                            print(f"    - {key}: {value}")
                
                print("\n  Excerpt:")
                print(f"  {text[:500]}...")
                print()
        
        input("\nPress Enter to continue...")
    
    def system_info(self):
        """Display system information"""
        self.print_header()
        
        print(f"{Fore.YELLOW}System Information:{Style.RESET_ALL}\n")
        
        print("RAG Document Assistant")
        print("----------------------")
        print("A retrieval-augmented generation system for working with documents.")
        
        print("\nComponents:")
        print("  - Repository Manager: Organizes documents in isolated repositories")
        print("  - Document Processor: Handles different document types with specialized processing")
        print("  - Vector Store: Creates embeddings and enables semantic search")
        print("  - RAG Engine: Combines retrieval and generation to answer questions")
        print("  - Document Grader: Improves retrieval quality with specialized scoring")
        
        print("\nSupported Document Types:")
        print("  - PDF Documents: Processed with LlamaParse")
        print("  - Log Files: Processed with specialized log chunking")
        
        print("\nFeatures:")
        print("  - Document Type Detection: Automatically identifies document types")
        print("  - Specialized Prompting: Different prompts for different document types")
        print("  - Document Grading: Improves retrieval relevance")
        print("  - Confidence Scoring: Estimates answer reliability")
        
        input("\nPress Enter to continue...")
    
    def run(self):
        """Run the CLI application"""
        while True:
            self.print_menu()

if __name__ == "__main__":
    cli = SimpleRAGCLI()
    cli.run()