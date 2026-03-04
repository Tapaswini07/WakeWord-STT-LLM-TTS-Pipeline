"""
Voice Assistant Package
A production-ready wake word activated voice assistant with STT, LLM, and TTS integration.
"""

__version__ = "1.0.0"
__author__ = "AI Engineer"
__description__ = "Wake word activated voice assistant with latency measurement"

from src.voice_assistant import VoiceAssistant
from src.wake_word_detector import WakeWordDetector
from src.speech_to_text import SpeechToText, RealTimeSpeechToText
from src.text_to_speech import TextToSpeech, GoogleTTS
from src.llm_integration import get_llm_client, GroqLLMClient, OllamaLLMClient, HuggingFaceLLMClient, DemoLLMClient
from utils.latency_tracker import LatencyTracker, LatencyMetric, tracker

__all__ = [
    'VoiceAssistant',
    'WakeWordDetector',
    'SpeechToText',
    'RealTimeSpeechToText',
    'TextToSpeech',
    'GoogleTTS',
    'get_llm_client',
    'GroqLLMClient',
    'OllamaLLMClient',
    'HuggingFaceLLMClient',
    'LatencyTracker',
    'LatencyMetric',
    'tracker',
]
