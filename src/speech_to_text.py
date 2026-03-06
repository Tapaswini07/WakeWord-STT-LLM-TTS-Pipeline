"""Speech-to-text conversion module."""

import speech_recognition as sr
from typing import Optional
from config.settings import STT_ENGINE, STT_LANGUAGE
from utils.latency_tracker import tracker


class SpeechToText:
    """Converts speech to text using various engines."""
    
    def __init__(self, engine: str = STT_ENGINE, language: str = STT_LANGUAGE):
        self.engine = engine
        self.language = language
        self.recognizer = sr.Recognizer()
        
        # Optimize recognizer settings
        self.recognizer.energy_threshold = 4000
        self.recognizer.dynamic_energy_threshold = True
    
    def transcribe_audio(self, audio_file: Optional[str] = None) -> Optional[str]:
        """
        Transcribe audio from file or microphone.
        
        Args:
            audio_file: Path to audio file. If None, uses microphone.
        
        Returns:
            Transcribed text or None if recognition failed.
        """
        tracker.start("speech_to_text")
        
        try:
            if audio_file:
                # Transcribe from file
                with sr.AudioFile(audio_file) as source:
                    audio = self.recognizer.record(source)
            else:
                # Transcribe from microphone (quick alternative)
                microphone = sr.Microphone()
                with microphone as source:
                    self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                    audio = self.recognizer.listen(source, timeout=10)
            
            # Use the specified engine
            if self.engine == "google":
                text = self._recognize_google(audio)
            elif self.engine == "sphinx":
                text = self._recognize_sphinx(audio)
            else:
                text = self._recognize_google(audio)  # Default to Google
            
            duration = tracker.end("speech_to_text")
            print(f"⏱️  Speech-to-text: {duration:.2f}ms")
            
            return text
            
        except Exception as e:
            tracker.end("speech_to_text")
            print(f"❌ Error in speech-to-text: {e}")
            return None
    
    def _recognize_google(self, audio) -> Optional[str]:
        """Recognize speech using Google Speech Recognition API."""
        try:
            text = self.recognizer.recognize_google(audio, language=self.language)
            return text
        except sr.UnknownValueError:
            print("❌ Google Speech Recognition could not understand audio")
            return None
        except sr.RequestError as e:
            print(f"❌ Error with Google Speech Recognition service: {e}")
            return None
    
    def _recognize_sphinx(self, audio) -> Optional[str]:
        """Recognize speech using PocketSphinx (offline)."""
        try:
            text = self.recognizer.recognize_sphinx(audio)
            return text
        except sr.UnknownValueError:
            print("❌ PocketSphinx could not understand audio")
            return None
        except Exception as e:
            print(f"❌ Error with PocketSphinx: {e}")
            return None


class RealTimeSpeechToText:
    """Streaming speech-to-text for real-time transcription."""
    
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.recognizer.energy_threshold = 4000
    
    def stream_transcribe(self, duration: int = 5) -> Optional[str]:
        """
        Stream transcription from microphone.
        
        Args:
            duration: Max duration in seconds.
        
        Returns:
            Transcribed text.
        """
        try:
            microphone = sr.Microphone()
            with microphone as source:
                print(f"🎤 Streaming transcription for {duration}s...")
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                
                audio = self.recognizer.listen(
                    source,
                    timeout=duration,
                    phrase_time_limit=duration
                )
            
            text = self.recognizer.recognize_google(audio)
            return text
            
        except Exception as e:
            print(f"❌ Error in streaming transcription: {e}")
            return None
