import requests
import json
from typing import Dict, List, Optional, Union
from config import OLLAMA_BASE_URL, OLLAMA_MODEL

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
    
    def generate_with_context(self, 
                             query: str, 
                             context_chunks: List[str],
                             temperature: float = 0.7) -> str:
        """Generate RAG response with context chunks"""
        
        system_prompt = """You are a helpful assistant that answers questions based only on the provided context.
If the context doesn't contain the information needed to answer the question, say 'I don't have enough information to answer this question.'
Do not use information outside of the provided context."""
        
        context_text = "\n\n".join([f"Chunk {i+1}:\n{chunk}" for i, chunk in enumerate(context_chunks)])
        
        prompt = f"""Context information:
{context_text}

Question: {query}

Answer:"""
        
        return self.generate(prompt=prompt, system_prompt=system_prompt, temperature=temperature)

# Test the client
if __name__ == "__main__":
    client = Llama3Client()
    response = client.generate("Hello, what can you do?")
    print(f"Response: {response}")