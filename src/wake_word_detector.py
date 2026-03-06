"""Wake word detection module."""

import speech_recognition as sr
from typing import Optional, Callable
from config.settings import WAKE_WORD, WAKE_WORD_CONFIDENCE_THRESHOLD
from utils.latency_tracker import tracker


class WakeWordDetector:
    """Detects wake words from audio stream."""
    
    def __init__(self, wake_word: str = WAKE_WORD):
        self.wake_word = wake_word.lower()
        self.recognizer = sr.Recognizer()
        
        # Try to initialize microphone
        try:
            self.microphone = sr.Microphone()
            self.audio_available = True
        except Exception as e:
            print(f"⚠️  Audio input not available: {e}")
            self.microphone = None
            self.audio_available = False
        
        # Adjust recognizer settings for better recognition
        self.recognizer.energy_threshold = 4000
        self.recognizer.dynamic_energy_threshold = True
    
    def is_available(self) -> bool:
        """Check if microphone is available."""
        return self.audio_available
    
    def listen_for_wake_word(self, timeout: Optional[int] = None) -> bool:
        """
        Listen for the wake word from the microphone.
        
        Args:
            timeout: Timeout in seconds. None for indefinite.
        
        Returns:
            True if wake word is detected, False otherwise.
        """
        if not self.audio_available:
            print("❌ Audio input not available")
            return False
            
        tracker.start("wake_word_detection")
        
        try:
            with self.microphone as source:
                print(f"🎤 Listening for '{self.wake_word}'...")
                
                # Calibrate for ambient noise
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                
                # Listen for audio
                audio = self.recognizer.listen(
                    source,
                    timeout=timeout,
                    phrase_time_limit=10
                )
            
            # Recognize speech
            text = self.recognizer.recognize_google(audio).lower()
            print(f"Detected: {text}")
            
            # Check if wake word is in the detected text
            is_wake_word = self.wake_word in text
            
            duration = tracker.end("wake_word_detection")
            print(f"⏱️  Wake word detection: {duration:.2f}ms")
            
            return is_wake_word
            
        except sr.UnknownValueError:
            tracker.end("wake_word_detection")
            print("❌ Could not understand audio")
            return False
        except sr.RequestError as e:
            tracker.end("wake_word_detection")
            print(f"❌ Error with speech recognition service: {e}")
            return False
        except Exception as e:
            print(f"❌ Error in wake word detection: {e}")
            return False
    
    def listen_for_command(self, timeout: int = 10) -> Optional[str]:
        """
        Listen for a command after wake word is detected.
        
        Args:
            timeout: Timeout in seconds.
        
        Returns:
            Recognized command text or None if recognition failed.
        """
        if not self.audio_available:
            print("❌ Audio input not available")
            return None
            
        tracker.start("command_listening")
        
        try:
            with self.microphone as source:
                print("🎤 Listening for your command...")
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                
                audio = self.recognizer.listen(
                    source,
                    timeout=timeout,
                    phrase_time_limit=10
                )
            
            text = self.recognizer.recognize_google(audio)
            
            duration = tracker.end("command_listening")
            print(f"⏱️  Command listening: {duration:.2f}ms")
            
            return text
            
        except sr.UnknownValueError:
            tracker.end("command_listening")
            print("❌ Could not understand the command")
            return None
        except sr.RequestError as e:
            tracker.end("command_listening")
            print(f"❌ Error with speech recognition service: {e}")
            return None
        except Exception as e:
            tracker.end("command_listening")
            print(f"❌ Error listening for command: {e}")
            return None
