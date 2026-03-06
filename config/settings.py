"""Configuration settings for the voice assistant."""

import os
from dotenv import load_dotenv

load_dotenv()

# Audio settings
AUDIO_SAMPLE_RATE = 16000
AUDIO_CHUNK_SIZE = 2048
AUDIO_DEVICE_INDEX = None  # None for default device

# Wake word settings
WAKE_WORD = "hello"
WAKE_WORD_CONFIDENCE_THRESHOLD = 0.5

# STT settings
STT_ENGINE = "google"  # options: "google", "sphinx"
STT_LANGUAGE = "en-US"

# LLM settings
# Default to demo mode (no API key needed). Set to groq/ollama/huggingface in .env to use real providers
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "demo")  # Default to "demo" for testing
LLM_ENDPOINT = os.getenv("LLM_ENDPOINT", "")
LLM_API_KEY = os.getenv("LLM_API_KEY", "")
LLM_MODEL = "mistral-7b-instruct"  # Free model from Groq
LLM_MAX_TOKENS = 256
LLM_TEMPERATURE = 0.7

# TTS settings
TTS_ENGINE = "pyttsx3"  # options: "pyttsx3", "gtts"
TTS_LANGUAGE = "en"
TTS_SPEED = 150

# Latency measurement
ENABLE_LATENCY_MEASUREMENT = True
VERBOSE_LOGGING = True

# Timeout settings (in seconds)
WAKE_WORD_TIMEOUT = 30
SPEECH_RECOGNITION_TIMEOUT = 10
LLM_RESPONSE_TIMEOUT = 30
