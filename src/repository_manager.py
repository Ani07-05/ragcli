import json
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
from config import REPOSITORIES_DIR, METADATA_FILE

class RepositoryManager:
    """Manages key-based document repositories"""
    
    def __init__(self):
        self.repos_dir = REPOSITORIES_DIR
        self.metadata_file = METADATA_FILE
        self._initialize()
    
    def _initialize(self):
        """Initialize repositories directory and metadata"""
        self.repos_dir.mkdir(parents=True, exist_ok=True)
        
        if not self.metadata_file.exists():
            # Create initial metadata structure
            metadata = {
                "repositories": {},
                "created_at": datetime.now().isoformat()
            }
            self._save_metadata(metadata)
        
        # Load existing metadata
        self.metadata = self._load_metadata()
    
    def _load_metadata(self) -> Dict:
        """Load metadata from file"""
        with open(self.metadata_file, 'r') as f:
            return json.load(f)
    
    def _save_metadata(self, metadata: Optional[Dict] = None):
        """Save metadata to file"""
        if metadata is None:
            metadata = self.metadata
        
        with open(self.metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)
    
    def _get_repo_path(self, key: str) -> Path:
        """Get repository path from key"""
        # Use hash to ensure filesystem compatibility
        hashed_key = hashlib.md5(key.encode()).hexdigest()
        return self.repos_dir / hashed_key
    
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
    
    def list_repositories(self) -> List[Dict]:
        """List all repositories with their metadata"""
        result = []
        for key, data in self.metadata["repositories"].items():
            result.append({
                "key": key,
                **data
            })
        return result
    
    def get_repository_path(self, key: str) -> Optional[Path]:
        """Get repository path if it exists"""
        if key not in self.metadata["repositories"]:
            print(f"Repository '{key}' not found")
            return None
        
        return self._get_repo_path(key)
    
    def update_document_count(self, key: str, count: int):
        """Update document count for a repository"""
        if key not in self.metadata["repositories"]:
            return
        
        self.metadata["repositories"][key]["document_count"] += count
        self.metadata["repositories"][key]["last_updated"] = datetime.now().isoformat()
        self._save_metadata()

# Test the repository manager
if __name__ == "__main__":
    repo_manager = RepositoryManager()
    
    # Create a test repository
    repo_manager.create_repository("test_repo", "A test repository")
    
    # List repositories
    repos = repo_manager.list_repositories()
    print(f"Repositories: {repos}")