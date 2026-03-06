"""Text-to-speech conversion module."""

import pyttsx3
from typing import Optional
from config.settings import TTS_ENGINE, TTS_LANGUAGE, TTS_SPEED
from utils.latency_tracker import tracker


class TextToSpeech:
    """Converts text to speech using various engines."""
    
    def __init__(self, engine: str = TTS_ENGINE, language: str = TTS_LANGUAGE):
        self.engine_name = engine
        self.language = language
        self.speed = TTS_SPEED
        
        if engine == "pyttsx3":
            self.engine = pyttsx3.init()
            self._configure_pyttsx3()
        else:
            print(f"⚠️  TTS engine '{engine}' not fully configured, using pyttsx3")
            self.engine = pyttsx3.init()
            self._configure_pyttsx3()
    
    def _configure_pyttsx3(self) -> None:
        """Configure pyttsx3 engine."""
        self.engine.setProperty('rate', self.speed)
        self.engine.setProperty('volume', 0.9)
        
        # Set voice based on language
        voices = self.engine.getProperty('voices')
        if voices:
            self.engine.setProperty('voice', voices[0].id)
    
    def speak(self, text: str, save_to_file: Optional[str] = None) -> bool:
        """
        Convert text to speech and play/save it.
        
        Args:
            text: Text to convert to speech.
            save_to_file: Optional file path to save audio. If None, plays directly.
        
        Returns:
            True if successful, False otherwise.
        """
        if not text or not text.strip():
            print("⚠️  Empty text provided for TTS")
            return False
        
        tracker.start("text_to_speech")
        
        try:
            print(f"🔊 Speaking: {text[:100]}...")
            
            if save_to_file:
                self.engine.save_to_file(text, save_to_file)
                self.engine.runAndWait()
                print(f"✅ Audio saved to {save_to_file}")
            else:
                self.engine.say(text)
                self.engine.runAndWait()
            
            duration = tracker.end("text_to_speech")
            print(f"⏱️  Text-to-speech: {duration:.2f}ms")
            
            return True
            
        except Exception as e:
            tracker.end("text_to_speech")
            print(f"❌ Error in text-to-speech: {e}")
            return False
    
    def speak_async(self, text: str) -> bool:
        """Speak without waiting for completion."""
        if not text or not text.strip():
            return False
        
        try:
            self.engine.say(text)
            return True
        except Exception as e:
            print(f"❌ Error in async TTS: {e}")
            return False
    
    def stop(self) -> None:
        """Stop current speech."""
        try:
            self.engine.stop()
        except Exception as e:
            print(f"⚠️  Error stopping TTS: {e}")


class GoogleTTS:
    """Google Text-to-Speech using gTTS."""
    
    def __init__(self, language: str = "en"):
        try:
            from gtts import gTTS
            self.gtts = gTTS
            self.language = language
        except ImportError:
            print("⚠️  gTTS not installed. Install with: pip install gtts")
            self.gtts = None
    
    def speak(self, text: str, save_to_file: Optional[str] = None) -> bool:
        """
        Convert text to speech using Google TTS.
        
        Args:
            text: Text to convert.
            save_to_file: Optional file path to save audio.
        
        Returns:
            True if successful.
        """
        if not self.gtts:
            print("❌ gTTS not available")
            return False
        
        tracker.start("text_to_speech")
        
        try:
            tts = self.gtts(text=text, lang=self.language, slow=False)
            
            if save_to_file:
                tts.save(save_to_file)
                print(f"✅ Audio saved to {save_to_file}")
            else:
                # Play audio
                import tempfile
                import os
                with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as tmp:
                    tts.save(tmp.name)
                    os.system(f'start {tmp.name}')  # Windows
                    # For Linux: os.system(f'play {tmp.name}')
                    # For Mac: os.system(f'open {tmp.name}')
            
            duration = tracker.end("text_to_speech")
            print(f"⏱️  Text-to-speech: {duration:.2f}ms")
            
            return True
            
        except Exception as e:
            tracker.end("text_to_speech")
            print(f"❌ Error in Google TTS: {e}")
            return False
