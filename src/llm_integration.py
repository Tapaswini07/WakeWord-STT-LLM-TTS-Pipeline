"""LLM integration module supporting multiple free providers."""

import requests
import json
from typing import Optional
from config.settings import (
    LLM_PROVIDER, LLM_ENDPOINT, LLM_API_KEY, 
    LLM_MODEL, LLM_MAX_TOKENS, LLM_TEMPERATURE
)
from utils.latency_tracker import tracker


class LLMClient:
    """Base class for LLM clients."""
    
    def __init__(self, provider: str = LLM_PROVIDER):
        self.provider = provider
        self.model = LLM_MODEL
        self.max_tokens = LLM_MAX_TOKENS
        self.temperature = LLM_TEMPERATURE
    
    def generate_response(self, prompt: str) -> Optional[str]:
        """
        Generate response from LLM.
        
        Args:
            prompt: User prompt.
        
        Returns:
            Generated response or None if failed.
        """
        raise NotImplementedError


class GroqLLMClient(LLMClient):
    """Groq LLM Client - Free API with fast inference."""
    
    def __init__(self):
        super().__init__()
        self.api_key = LLM_API_KEY or self._get_groq_key()
        self.endpoint = "https://api.groq.com/openai/v1/chat/completions"
        self.model = "mixtral-8x7b-32768"  # Free model from Groq
    
    def _get_groq_key(self) -> str:
        """Get Groq API key from environment."""
        import os
        key = os.getenv("GROQ_API_KEY", "")
        if not key:
            print("⚠️  GROQ_API_KEY not found. Get free key from https://console.groq.com")
        return key
    
    def generate_response(self, prompt: str) -> Optional[str]:
        """Generate response using Groq API."""
        tracker.start("llm_inference")
        
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": self.model,
                "messages": [
                    {
                        "role": "system",
                        "content": "You are a helpful voice assistant. Keep responses concise and conversational."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "temperature": self.temperature,
                "max_tokens": self.max_tokens,
                "top_p": 1.0,
                "frequency_penalty": 0.0,
                "presence_penalty": 0.0
            }
            
            response = requests.post(self.endpoint, headers=headers, json=payload, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                text = result['choices'][0]['message']['content']
                
                duration = tracker.end("llm_inference")
                print(f"⏱️  LLM inference: {duration:.2f}ms")
                
                return text
            else:
                tracker.end("llm_inference")
                print(f"❌ Groq API error: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            tracker.end("llm_inference")
            print(f"❌ Error calling Groq API: {e}")
            return None


class OllamaLLMClient(LLMClient):
    """Ollama Local LLM Client - Completely offline."""
    
    def __init__(self):
        super().__init__()
        self.endpoint = LLM_ENDPOINT or "http://localhost:11434/api/generate"
        self.model = "neural-chat"  # Lightweight model
    
    def generate_response(self, prompt: str) -> Optional[str]:
        """Generate response using Ollama."""
        tracker.start("llm_inference")
        
        try:
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "temperature": self.temperature
            }
            
            response = requests.post(self.endpoint, json=payload, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                text = result.get('response', '').strip()
                
                duration = tracker.end("llm_inference")
                print(f"⏱️  LLM inference: {duration:.2f}ms")
                
                return text
            else:
                tracker.end("llm_inference")
                print(f"❌ Ollama error: {response.status_code}")
                return None
                
        except Exception as e:
            tracker.end("llm_inference")
            print(f"❌ Error calling Ollama: {e}")
            return None


class GeminiLLMClient(LLMClient):
    """Google Gemini LLM Client - Fast and efficient for voice assistants."""
    
    def __init__(self):
        super().__init__()
        self.api_key = LLM_API_KEY or self._get_gemini_key()
        self.model_name = "gemini-2.0-flash"  # Gemini Flash model
        
        # Initialize Gemini with new package
        try:
            from google import genai
            self.client = genai.Client(api_key=self.api_key)
        except Exception as e:
            print(f"❌ Failed to initialize Gemini: {e}")
            self.client = None
    
    def _get_gemini_key(self) -> str:
        """Get Gemini API key from environment."""
        import os
        key = os.getenv("GEMINI_API_KEY", "")
        if not key:
            print("⚠️  GEMINI_API_KEY not found. Get free key from https://makersuite.google.com/app/apikey")
        return key
    
    def generate_response(self, prompt: str) -> Optional[str]:
        """Generate response using Gemini API."""
        if not self.client:
            return None
            
        tracker.start("llm_inference")
        
        try:
            # Create the full prompt with system context
            full_prompt = f"You are a helpful voice assistant. Keep responses concise and conversational (2-3 sentences max).\n\nUser: {prompt}\nAssistant:"
            
            # Generate response using new API
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=full_prompt,
                config={
                    'temperature': self.temperature,
                    'max_output_tokens': self.max_tokens,
                }
            )
            
            text = response.text.strip()
            
            duration = tracker.end("llm_inference")
            print(f"⏱️  LLM inference: {duration:.2f}ms")
            
            return text
            
        except Exception as e:
            tracker.end("llm_inference")
            print(f"❌ Error calling Gemini API: {e}")
            return None


class HuggingFaceLLMClient(LLMClient):
    """Hugging Face Inference API Client."""
    
    def __init__(self):
        super().__init__()
        self.api_key = LLM_API_KEY or self._get_hf_key()
        self.endpoint = "https://api-inference.huggingface.co/models"
        self.model = "mistralai/Mistral-7B-Instruct-v0.1"
    
    def _get_hf_key(self) -> str:
        """Get HuggingFace API key."""
        import os
        key = os.getenv("HF_API_KEY", "")
        if not key:
            print("⚠️  HF_API_KEY not found. Get free key from https://huggingface.co/settings/tokens")
        return key
    
    def generate_response(self, prompt: str) -> Optional[str]:
        """Generate response using Hugging Face API."""
        tracker.start("llm_inference")
        
        try:
            headers = {"Authorization": f"Bearer {self.api_key}"}
            endpoint = f"{self.endpoint}/{self.model}"
            
            payload = {
                "inputs": prompt,
                "parameters": {
                    "max_length": self.max_tokens,
                    "temperature": self.temperature
                }
            }
            
            response = requests.post(endpoint, headers=headers, json=payload, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                text = result[0].get('generated_text', prompt).replace(prompt, '').strip()
                
                duration = tracker.end("llm_inference")
                print(f"⏱️  LLM inference: {duration:.2f}ms")
                
                return text
            else:
                tracker.end("llm_inference")
                print(f"❌ Hugging Face API error: {response.status_code}")
                return None
                
        except Exception as e:
            tracker.end("llm_inference")
            print(f"❌ Error calling Hugging Face API: {e}")
            return None


class DemoLLMClient(LLMClient):
    """Demo LLM Client for testing without API keys."""
    
    def __init__(self):
        super().__init__()
        self.responses = {
            "hello": "Hi there! I'm a voice assistant. How can I help you today?",
            "how are you": "I'm doing great! Thanks for asking. How about you?",
            "kya haal chaal": "Main bilkul theek hoon! Aapka din kaisa chal raha hai?",
            "what is machine learning": "Machine learning is a subset of artificial intelligence that enables systems to learn and improve from experience without being explicitly programmed.",
            "tell me a joke": "Why did the AI go to school? Because it wanted to improve its learning model! 😄",
            "what's the weather": "I don't have access to real-time weather data, but you can check your weather app for that!",
            "what time is it": "I don't have access to the current time, but you can check your system clock!",
        }
    
    def generate_response(self, prompt: str) -> Optional[str]:
        """Generate demo response."""
        tracker.start("llm_inference")
        
        try:
            prompt_lower = prompt.lower()
            
            # Try to find a matching response
            for key, response in self.responses.items():
                if key in prompt_lower:
                    duration = tracker.end("llm_inference")
                    print(f"⏱️  LLM inference: {duration:.2f}ms")
                    return response
            
            # Default response
            default_response = f"That's an interesting question about '{prompt}'. I'm a demo assistant, so I have limited responses. In production, I would use a real LLM to answer more comprehensively!"
            
            duration = tracker.end("llm_inference")
            print(f"⏱️  LLM inference: {duration:.2f}ms")
            
            return default_response
            
        except Exception as e:
            tracker.end("llm_inference")
            print(f"❌ Error in demo LLM: {e}")
            return None


def get_llm_client(provider: str = LLM_PROVIDER) -> Optional[LLMClient]:
    """Factory function to get appropriate LLM client."""
    if provider.lower() == "groq":
        return GroqLLMClient()
    elif provider.lower() == "ollama":
        return OllamaLLMClient()
    elif provider.lower() == "huggingface":
        return HuggingFaceLLMClient()
    elif provider.lower() == "demo":
        return DemoLLMClient()
    elif provider.lower() == "gemini":
        return GeminiLLMClient()
    else:
        # Default to demo if no valid provider found
        print(f"⚠️  Provider '{provider}' not configured. Using demo mode.")
        return DemoLLMClient()
