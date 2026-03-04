"""
Simple Interactive Voice Assistant Demo
Works immediately - no API keys needed!
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.text_to_speech import TextToSpeech
from src.llm_integration import get_llm_client
from utils.latency_tracker import tracker


def print_header(title):
    """Print a formatted header."""
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70 + "\n")


def demo_text_only():
    """Interactive text-based conversation."""
    print_header("TEXT-ONLY MODE (No microphone needed)")
    
    llm = get_llm_client()
    tts = TextToSpeech()
    
    if not llm:
        print("❌ LLM client failed to initialize")
        return
    
    print("💬 Chat with the AI (type 'quit' to exit)\n")
    
    while True:
        try:
            user_input = input("You: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("\n👋 Goodbye!")
                break
            
            if not user_input:
                print("Please enter something.\n")
                continue
            
            # Process with LLM
            tracker.reset()
            tracker.start("total_cycle")
            
            print("\n🤖 AI is thinking...")
            response = llm.generate_response(user_input)
            
            if response:
                print(f"\nAI: {response}\n")
                
                # Optional: Speak the response
                try:
                    speak = input("Speak response? (y/n): ").strip().lower()
                    if speak == 'y':
                        print("🔊 Speaking response...")
                        tts.speak(response)
                except:
                    pass
                
                tracker.end("total_cycle")
                tracker.print_report()
            else:
                print("❌ Failed to get response\n")
                
        except KeyboardInterrupt:
            print("\n\n👋 Demo interrupted. Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}\n")


def demo_speech_only():
    """Speech-based conversation (requires microphone)."""
    print_header("SPEECH MODE (Microphone required)")
    
    try:
        from src.wake_word_detector import WakeWordDetector
    except Exception as e:
        print(f"❌ Speech recognition not available: {e}")
        print("\n💡 FALLBACK: Use text mode instead (option 1)\n")
        return
    
    detector = WakeWordDetector()
    
    # Check if audio is available
    if not detector.is_available():
        print("❌ Microphone not detected")
        print("\n💡 FALLBACK: Use text mode instead (option 1)")
        print("💡 SOLUTION: Install PyAudio or use Ollama on Windows\n")
        return
    
    llm = get_llm_client()
    tts = TextToSpeech()
    
    if not llm:
        print("❌ LLM client failed")
        return
    
    print("🎤 Speech mode active")
    print("Say 'hey assistant' to activate, or 'quit' to exit\n")
    
    try:
        while True:
            # Listen for wake word
            print("Listening for wake word...\n")
            if detector.listen_for_wake_word(timeout=10):
                print("✅ Wake word detected!\n")
                
                # Listen for command
                command = detector.listen_for_command(timeout=10)
                
                if command:
                    print(f"📝 You said: {command}\n")
                    
                    # Process with LLM
                    tracker.reset()
                    tracker.start("total_cycle")
                    
                    print("🤖 Processing...")
                    response = llm.generate_response(command)
                    
                    if response:
                        print(f"🔊 Response: {response}\n")
                        tts.speak(response)
                        tracker.end("total_cycle")
                        tracker.print_report()
                    else:
                        print("❌ Failed to get response\n")
                        
            else:
                print("⏱️  Timeout waiting for wake word\n")
                
    except KeyboardInterrupt:
        print("\n👋 Speech mode stopped")


def demo_mixed_mode():
    """Text and speech combined."""
    print_header("INTERACTIVE MODE (Choose input method)")
    
    llm = get_llm_client()
    tts = TextToSpeech()
    
    if not llm:
        print("❌ LLM client failed")
        return
    
    print("Choose how to interact (type 'quit' to exit):\n")
    print("1. Type text input")
    print("2. Use voice input")
    print("3. Mix both\n")
    
    while True:
        try:
            choice = input("Choose input method (1/2/3/quit): ").strip().lower()
            
            if choice in ['quit', 'q', 'exit']:
                print("\n👋 Goodbye!")
                break
            
            if choice == '1':
                # Text input
                user_input = input("You: ").strip()
                if not user_input:
                    continue
                input_type = "text"
                
            elif choice == '2':
                # Speech input
                try:
                    from src.wake_word_detector import WakeWordDetector
                    detector = WakeWordDetector()
                    print("🎤 Listening...")
                    user_input = detector.listen_for_command(timeout=10)
                    if not user_input:
                        print("❌ Could not understand speech\n")
                        continue
                    input_type = "speech"
                except Exception as e:
                    print(f"❌ Speech input not available: {e}\n")
                    continue
                    
            elif choice == '3':
                # Mix
                mode = input("Text (t) or Speech (s)? ").strip().lower()
                if mode == 't':
                    user_input = input("You: ").strip()
                    if not user_input:
                        continue
                    input_type = "text"
                elif mode == 's':
                    try:
                        from src.wake_word_detector import WakeWordDetector
                        detector = WakeWordDetector()
                        print("🎤 Listening...")
                        user_input = detector.listen_for_command(timeout=10)
                        if not user_input:
                            print("❌ Could not understand speech\n")
                            continue
                        input_type = "speech"
                    except:
                        print("❌ Speech not available\n")
                        continue
                else:
                    continue
            else:
                print("Invalid choice\n")
                continue
            
            # Process request
            tracker.reset()
            tracker.start("total_cycle")
            
            print(f"\n📥 Processing {input_type} input...")
            response = llm.generate_response(user_input)
            
            if response:
                print(f"\n✅ Response: {response}\n")
                
                # Ask if user wants speech output
                speak_choice = input("Speak response? (y/n): ").strip().lower()
                if speak_choice == 'y':
                    print("🔊 Speaking...")
                    tts.speak(response)
                
                tracker.end("total_cycle")
                tracker.print_report()
            else:
                print("❌ Failed to get response\n")
                
        except KeyboardInterrupt:
            print("\n👋 Demo stopped. Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}\n")


def main_menu():
    """Main menu for selecting demo mode."""
    while True:
        print_header("VOICE ASSISTANT DEMO")
        
        print("SELECT A MODE:\n")
        print("1️⃣  Text-Only Mode (Type your questions)")
        print("2️⃣  Speech-Only Mode (Use microphone + wake word)")
        print("3️⃣  Interactive Mode (Choose text or speech for each message)")
        print("4️⃣  Component Test (Test individual components)")
        print("5️⃣  Exit\n")
        
        choice = input("Choose mode (1-5): ").strip()
        
        if choice == '1':
            demo_text_only()
        elif choice == '2':
            demo_speech_only()
        elif choice == '3':
            demo_mixed_mode()
        elif choice == '4':
            test_components()
        elif choice == '5':
            print("\n👋 Thank you for using Voice Assistant!")
            break
        else:
            print("❌ Invalid choice. Please try again.\n")


def test_components():
    """Test individual components."""
    print_header("COMPONENT TESTING")
    
    print("Testing components...\n")
    
    # Test TTS
    print("1️⃣  Testing Text-to-Speech...")
    tts = TextToSpeech()
    success = tts.speak("Hello! Text to speech is working correctly!")
    if success:
        print("✅ TTS working\n")
    else:
        print("⚠️  TTS test completed\n")
    
    # Test LLM
    print("2️⃣  Testing LLM Integration...")
    llm = get_llm_client()
    if llm:
        response = llm.generate_response("say hello")
        if response:
            print(f"✅ LLM Response: {response}\n")
        else:
            print("⚠️  LLM returned no response\n")
    else:
        print("❌ LLM failed\n")
    
    # Test latency tracking
    print("3️⃣  Testing Latency Measurement...")
    tracker.start("test_component")
    import time
    time.sleep(0.5)
    duration = tracker.end("test_component")
    print(f"✅ Latency tracking working: {duration:.2f}ms\n")
    
    print("✅ Component testing completed!\n")
    input("Press Enter to return to menu...")


if __name__ == "__main__":
    try:
        main_menu()
    except KeyboardInterrupt:
        print("\n\n👋 Application stopped by user")
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
