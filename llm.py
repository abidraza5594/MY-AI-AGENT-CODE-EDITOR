"""LLM client for Ollama"""
import requests
from typing import Optional, Dict
from logger import get_logger

logger = get_logger()

class LLMClient:
    """Client for interacting with Ollama LLM"""
    
    def __init__(self, base_url: str = "http://localhost:11434"):
        self.base_url = base_url.rstrip('/')
        self.api_url = f"{self.base_url}/api/generate"
    
    def generate(self, prompt: str, model: str, 
                temperature: float = 0.7, max_tokens: int = 4000) -> str:
        """
        Generate completion from Ollama
        
        Args:
            prompt: Input prompt
            model: Model name (e.g., "qwen2.5-coder:32b")
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            
        Returns:
            Generated text
        """
        logger.debug(f"Calling LLM: {model}")
        
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens
            }
        }
        
        try:
            response = requests.post(
                self.api_url,
                json=payload,
                timeout=300
            )
            response.raise_for_status()
            
            result = response.json()
            generated_text = result.get("response", "")
            
            logger.debug(f"LLM response length: {len(generated_text)} chars")
            return generated_text
            
        except requests.exceptions.ConnectionError:
            logger.error(f"Cannot connect to Ollama at {self.base_url}")
            logger.error("Make sure Ollama is running: ollama serve")
            raise
        except requests.exceptions.Timeout:
            logger.error("LLM request timed out")
            raise
        except Exception as e:
            logger.error(f"LLM request failed: {e}")
            raise
    
    def check_connection(self) -> bool:
        """Check if Ollama is accessible"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def list_models(self) -> list:
        """List available models"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            response.raise_for_status()
            data = response.json()
            return [model["name"] for model in data.get("models", [])]
        except Exception as e:
            logger.error(f"Failed to list models: {e}")
            return []
