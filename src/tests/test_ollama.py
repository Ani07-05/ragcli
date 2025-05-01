import requests
import json

def test_ollama_api():
    try:
        # Test connection to Ollama API
        response = requests.get("http://localhost:11434/api/tags")
        if response.status_code == 200:
            models = response.json().get("models", [])
            print("✅ Connected to Ollama API successfully!")
            print(f"Available models: {[model['name'] for model in models]}")
            
            # Check if Llama 3 is available
            llama3_models = [model for model in models if "llama3" in model['name'].lower()]
            if llama3_models:
                print(f"✅ Found Llama 3 models: {[model['name'] for model in llama3_models]}")
            else:
                print("❌ Llama 3 model not found. Please run 'ollama pull llama3'")
            
            return True
        else:
            print(f"❌ Ollama API returned status code {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error connecting to Ollama API: {e}")
        print("Is Ollama running? Start it with 'ollama serve' command.")
        return False

def test_llama3_generation():
    try:
        # Simple test prompt for Llama 3
        data = {
            "model": "llama3",
            "prompt": "Hello, I'm testing if you're working correctly. Please respond with a brief greeting.",
            "stream": False
        }
        
        response = requests.post("http://localhost:11434/api/generate", json=data)
        
        if response.status_code == 200:
            result = response.json()
            print("\n✅ Successfully generated text with Llama 3!")
            print(f"Response: {result.get('response')[:100]}...")
            return True
        else:
            print(f"❌ Error generating text with Llama 3: {response.status_code}")
            print(response.text)
            return False
    except Exception as e:
        print(f"❌ Error calling Llama 3: {e}")
        return False

if __name__ == "__main__":
    print("Testing Ollama API and Llama 3...")
    if test_ollama_api():
        test_llama3_generation()