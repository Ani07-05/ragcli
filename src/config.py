import os
from pathlib import Path
from dotenv import load_dotenv
from pathlib import Path

# Ensure these settings are in your config.py
BASE_DIR = Path(__file__).parent.parent
REPOSITORIES_DIR = BASE_DIR / "data" / "repositories"
METADATA_FILE = BASE_DIR / "data" / "metadata.json"

# Embedding model - local
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

# Chunking settings
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200

# Ollama settings
OLLAMA_BASE_URL = "http://localhost:11434"
OLLAMA_MODEL = "llama3"  # Use "llama3:70b" for the larger model if available

# Ensure directories exist
REPOSITORIES_DIR.mkdir(parents=True, exist_ok=True)

load_dotenv()

# API Keys
LLAMA_CLOUD_API_KEY = os.getenv("LLAMA_CLOUD_API_KEY")

# Ensure directories exist

# Model settings
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"  # Efficient embedding model
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200

# Ollama settings
OLLAMA_BASE_URL = "http://localhost:11434"
OLLAMA_MODEL = "llama3"  # Use "llama3:70b" for the larger model if available

# Test the configuration
if __name__ == "__main__":
    print(f"LLAMA_CLOUD_API_KEY configured: {'Yes' if LLAMA_CLOUD_API_KEY else 'No'}")
    print(f"BASE_DIR: {BASE_DIR}")
    print(f"REPOSITORIES_DIR: {REPOSITORIES_DIR}")
    print(f"REPOSITORIES_DIR exists: {REPOSITORIES_DIR.exists()}")
    print(f"OLLAMA_MODEL: {OLLAMA_MODEL}")