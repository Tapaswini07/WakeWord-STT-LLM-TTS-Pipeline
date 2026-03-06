"""Main voice assistant orchestration module."""

from typing import Optional
from src.wake_word_detector import WakeWordDetector
from src.speech_to_text import SpeechToText
from src.text_to_speech import TextToSpeech
from src.llm_integration import get_llm_client
from config.settings import (
    WAKE_WORD, WAKE_WORD_TIMEOUT, 
    VERBOSE_LOGGING, ENABLE_LATENCY_MEASUREMENT
)
from utils.latency_tracker import tracker


class VoiceAssistant:
    """Main voice assistant orchestrating all components."""
    
    def __init__(self):
        """Initialize all components."""
        print("🚀 Initializing Voice Assistant...")
        
        self.wake_word_detector = WakeWordDetector(wake_word=WAKE_WORD)
        self.speech_to_text = SpeechToText()
        self.text_to_speech = TextToSpeech()
        self.llm_client = get_llm_client()
        
        self.is_running = False
        self.verbose = VERBOSE_LOGGING
        
        if not self.llm_client:
            print("⚠️  WARNING: LLM client initialization failed. Check API keys.")
        
        print("✅ Voice Assistant initialized successfully!\n")
    
    def run(self, continuous: bool = False) -> None:
        """
        Run the voice assistant.
        
        Args:
            continuous: If True, keeps listening for wake word. If False, runs once.
        """
        self.is_running = True
        
        try:
            if continuous:
                self._run_continuous()
            else:
                self._run_once()
        except KeyboardInterrupt:
            self.stop()
        except Exception as e:
            print(f"❌ Error in voice assistant: {e}")
            self.stop()
    
    def _run_once(self) -> None:
        """Run the assistant once (listen for wake word, then process command)."""
        print("🎤 Voice Assistant Ready!")
        print(f"Say '{WAKE_WORD}' to activate...\n")
        
        # Step 1: Listen for wake word
        tracker.start("total_cycle")
        
        if self._listen_for_activation():
            # Step 2: Listen for command
            command = self._listen_for_command()
            
            if command:
                # Step 3: Process with LLM
                response = self._process_with_llm(command)
                
                if response:
                    # Step 4: Speak response
                    self._speak_response(response)
            else:
                self.text_to_speech.speak("I couldn't hear your command. Please try again.")
        else:
            print("Wake word not detected. Exiting.")
        
        if ENABLE_LATENCY_MEASUREMENT:
            tracker.end("total_cycle")
            tracker.print_report()
    
    def _run_continuous(self) -> None:
        """Run the assistant in continuous mode."""
        print("🎤 Voice Assistant Ready (Continuous Mode)!")
        print(f"Say '{WAKE_WORD}' to start, press Ctrl+C to stop...\n")
        
        cycle_count = 0
        
        while self.is_running:
            cycle_count += 1
            print(f"--- Cycle {cycle_count} ---")
            tracker.reset()
            tracker.start("total_cycle")
            
            if self._listen_for_activation():
                command = self._listen_for_command()
                
                if command:
                    response = self._process_with_llm(command)
                    
                    if response:
                        self._speak_response(response)
                else:
                    self.text_to_speech.speak("I didn't catch that. Try again.")
            
            if ENABLE_LATENCY_MEASUREMENT:
                tracker.end("total_cycle")
                tracker.print_report()
            
            print()
    
    def _listen_for_activation(self) -> bool:
        """Listen for wake word activation."""
        try:
            timeout = WAKE_WORD_TIMEOUT
            
            # Retry logic for robustness
            max_retries = 3
            for attempt in range(max_retries):
                if self.verbose:
                    print(f"🎙️  Activation attempt {attempt + 1}/{max_retries}...")
                
                if self.wake_word_detector.listen_for_wake_word(timeout=10):
                    print("✅ Wake word detected!\n")
                    return True
            
            print("❌ Wake word not detected after retries.\n")
            return False
            
        except Exception as e:
            print(f"❌ Error listening for activation: {e}")
            return False
    
    def _listen_for_command(self) -> Optional[str]:
        """Listen for user command after activation."""
        try:
            command = self.wake_word_detector.listen_for_command(timeout=10)
            
            if command:
                print(f"📝 Command received: '{command}'\n")
                return command
            
            return None
            
        except Exception as e:
            print(f"❌ Error listening for command: {e}")
            return None
    
    def _process_with_llm(self, user_input: str) -> Optional[str]:
        """Process user input with LLM."""
        try:
            if not self.llm_client:
                error_msg = "LLM client not initialized"
                print(f"❌ {error_msg}")
                return error_msg
            
            if self.verbose:
                print(f"🤖 Processing with LLM: '{user_input}'")
            
            response = self.llm_client.generate_response(user_input)
            
            if response:
                print(f"✅ LLM Response: {response}\n")
                return response
            else:
                error_msg = "Failed to get LLM response"
                print(f"❌ {error_msg}")
                return error_msg
                
        except Exception as e:
            error_msg = f"LLM processing error: {str(e)}"
            print(f"❌ {error_msg}")
            return error_msg
    
    def _speak_response(self, text: str) -> None:
        """Speak the response."""
        try:
            self.text_to_speech.speak(text)
            print()
        except Exception as e:
            print(f"❌ Error speaking response: {e}")
    
    def stop(self) -> None:
        """Stop the voice assistant."""
        self.is_running = False
        self.text_to_speech.stop()
        print("\n✅ Voice Assistant stopped.")
    
    def set_verbose(self, verbose: bool) -> None:
        """Set verbose logging."""
        self.verbose = verbose
    
    def test_components(self) -> None:
        """Test all components individually."""
        print("🧪 Testing Voice Assistant Components...\n")
        
        # Test microphone access
        print("1️⃣  Testing microphone access...")
        try:
            import speech_recognition as sr
            mic = sr.Microphone()
            with mic as source:
                print("✅ Microphone access OK\n")
        except Exception as e:
            print(f"❌ Microphone error: {e}\n")
        
        # Test TTS
        print("2️⃣  Testing text-to-speech...")
        if self.text_to_speech.speak("Hello, voice assistant is ready"):
            print("✅ TTS OK\n")
        else:
            print("❌ TTS error\n")
        
        # Test LLM connection
        print("3️⃣  Testing LLM connection...")
        if self.llm_client:
            test_response = self.llm_client.generate_response("Say 'hello'")
            if test_response:
                print(f"✅ LLM OK - Response: {test_response}\n")
            else:
                print("❌ LLM failed\n")
        else:
            print("❌ LLM client not initialized\n")
        
        print("✅ Component testing completed!\n")


if __name__ == "__main__":
    assistant = VoiceAssistant()
    
    # Test components first
    assistant.test_components()
    
    # Run in continuous mode
    assistant.run(continuous=True)
