"""Demo and testing script for the voice assistant."""

import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.voice_assistant import VoiceAssistant
from src.wake_word_detector import WakeWordDetector
from src.speech_to_text import SpeechToText
from src.text_to_speech import TextToSpeech
from src.llm_integration import get_llm_client


def demo_basic():
    """Run a basic demo of the voice assistant."""
    print("="*70)
    print("VOICE ASSISTANT - BASIC DEMO")
    print("="*70 + "\n")
    
    assistant = VoiceAssistant()
    assistant.test_components()
    assistant.run(continuous=False)


def demo_continuous():
    """Run the voice assistant in continuous mode."""
    print("="*70)
    print("VOICE ASSISTANT - CONTINUOUS MODE")
    print("="*70 + "\n")
    
    assistant = VoiceAssistant()
    assistant.run(continuous=True)


def demo_component_test():
    """Test individual components."""
    print("="*70)
    print("COMPONENT TESTING")
    print("="*70 + "\n")
    
    # Test Wake Word Detection
    print("1. Testing Wake Word Detection...")
    print("-" * 50)
    detector = WakeWordDetector()
    print("Ready to listen. Say 'hey assistant' or similar...\n")
    result = detector.listen_for_wake_word(timeout=15)
    print(f"Result: {'Wake word detected!' if result else 'No wake word detected.'}\n")
    
    # Test TTS
    print("2. Testing Text-to-Speech...")
    print("-" * 50)
    tts = TextToSpeech()
    tts.speak("Hello! This is a text to speech test. How are you today?")
    print()
    
    # Test LLM
    print("3. Testing LLM Integration...")
    print("-" * 50)
    llm = get_llm_client()
    if llm:
        response = llm.generate_response("What is the capital of France?")
        print(f"LLM Response: {response}\n")
    else:
        print("LLM client not available\n")


def demo_pipeline():
    """Test the complete pipeline with a sample input."""
    print("="*70)
    print("COMPLETE PIPELINE DEMO")
    print("="*70 + "\n")
    
    print("This demo will simulate a complete pipeline:")
    print("Wake Word → Listen → Process → Respond\n")
    
    # Step 1: Text input (simulating STT)
    print("Step 1: User Input")
    print("-" * 50)
    user_input = input("Enter your question (or press Enter for default): ").strip()
    if not user_input:
        user_input = "What is machine learning?"
    print(f"Input: {user_input}\n")
    
    # Step 2: LLM Processing
    print("Step 2: LLM Processing")
    print("-" * 50)
    llm = get_llm_client()
    if llm:
        response = llm.generate_response(user_input)
        print(f"LLM Response: {response}\n")
        
        # Step 3: TTS
        print("Step 3: Text-to-Speech")
        print("-" * 50)
        tts = TextToSpeech()
        tts.speak(response)
        
        # Show latency report
        from utils.latency_tracker import tracker
        print("\nLatency Metrics:")
        tracker.print_report()
    else:
        print("LLM client not available - configure API keys first\n")


def interactive_menu():
    """Show interactive menu."""
    while True:
        print("\n" + "="*70)
        print("VOICE ASSISTANT - DEMO MENU")
        print("="*70)
        print("1. Basic Demo (Single cycle)")
        print("2. Continuous Mode (Multiple cycles)")
        print("3. Component Testing")
        print("4. Pipeline Test (Text input)")
        print("5. Exit")
        print("-"*70)
        
        choice = input("Select option (1-5): ").strip()
        
        if choice == "1":
            demo_basic()
        elif choice == "2":
            demo_continuous()
        elif choice == "3":
            demo_component_test()
        elif choice == "4":
            demo_pipeline()
        elif choice == "5":
            print("Goodbye!")
            break
        else:
            print("Invalid option. Please try again.")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Voice Assistant Demo")
    parser.add_argument(
        "--mode",
        choices=["basic", "continuous", "test", "pipeline", "menu"],
        default="menu",
        help="Demo mode to run"
    )
    
    args = parser.parse_args()
    
    try:
        if args.mode == "basic":
            demo_basic()
        elif args.mode == "continuous":
            demo_continuous()
        elif args.mode == "test":
            demo_component_test()
        elif args.mode == "pipeline":
            demo_pipeline()
        elif args.mode == "menu":
            interactive_menu()
    except KeyboardInterrupt:
        print("\n\nDemo interrupted by user.")
    except Exception as e:
        print(f"Error: {e}")
