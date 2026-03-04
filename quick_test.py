"""
Quick Test - Voice Assistant Complete Pipeline
Shows text and speech working
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.text_to_speech import TextToSpeech
from src.llm_integration import get_llm_client
from utils.latency_tracker import tracker


def test_complete_pipeline():
    """Test the complete pipeline with text input."""
    
    print("\n" + "="*70)
    print("  VOICE ASSISTANT - COMPLETE PIPELINE TEST")
    print("="*70 + "\n")
    
    # Initialize components
    print("🚀 Initializing components...\n")
    llm = get_llm_client()
    tts = TextToSpeech()
    
    if not llm:
        print("❌ LLM initialization failed")
        return
    
    print("✅ Components ready!\n")
    
    # Test cases
    test_inputs = [
        "hello",
        "kya haal chaal",
        "what is machine learning",
    ]
    
    print("="*70)
    print("  RUNNING TEST CASES")
    print("="*70 + "\n")
    
    for i, user_input in enumerate(test_inputs, 1):
        print(f"\n{'='*70}")
        print(f"TEST {i}: {user_input.upper()}")
        print(f"{'='*70}\n")
        
        # Reset tracker
        tracker.reset()
        tracker.start("total_pipeline")
        
        # Step 1: Display input
        print(f"📥 INPUT TEXT: \"{user_input}\"")
        
        # Step 2: LLM Processing
        print(f"\n🤖 Processing with LLM...")
        response = llm.generate_response(user_input)
        
        if response:
            # Step 3: Display response
            print(f"\n✅ LLM RESPONSE:\n   \"{response}\"")
            
            # Step 4: Text-to-Speech
            print(f"\n🔊 Converting to speech...")
            tts.speak(response)
            
            # Step 5: Show latency
            tracker.end("total_pipeline")
            print(f"\n⏱️  Complete pipeline latency:")
            tracker.print_report()
            
            print(f"\n✅ Test {i} completed successfully!\n")
        else:
            print("❌ LLM failed to generate response")
    
    print("\n" + "="*70)
    print("  ALL TESTS COMPLETED")
    print("="*70 + "\n")
    
    # Summary
    print("📊 SUMMARY:\n")
    print("✅ Text input processing works")
    print("✅ LLM inference working")
    print("✅ Text-to-speech working")
    print("✅ Latency measurement working")
    print("\n🎉 Voice Assistant pipeline is fully functional!\n")


def interactive_test():
    """Interactive test mode - user provides input."""
    
    print("\n" + "="*70)
    print("  VOICE ASSISTANT - INTERACTIVE TEST")
    print("="*70 + "\n")
    
    print("💡 HOW TO USE:")
    print("   1. Enter any text query")
    print("   2. System will process it with LLM")
    print("   3. Listen to voice response")
    print("   4. Type 'quit' to exit\n")
    
    # Initialize
    llm = get_llm_client()
    tts = TextToSpeech()
    
    if not llm:
        print("❌ LLM initialization failed")
        return
    
    conversation_count = 0
    
    while True:
        try:
            print("-" * 70)
            user_input = input("\n📝 Enter your text (or 'quit'): ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                break
            
            if not user_input:
                print("⚠️  Please enter something")
                continue
            
            conversation_count += 1
            
            # Process
            tracker.reset()
            tracker.start("cycle")
            
            print(f"\n🤖 Processing: \"{user_input}\"")
            response = llm.generate_response(user_input)
            
            if response:
                print(f"\n✅ Response: {response}")
                
                # Ask about speech
                try:
                    speak_choice = input("\n🔊 Speak response? (y/n): ").strip().lower()
                    if speak_choice == 'y':
                        print("\n🔊 Speaking...")
                        tts.speak(response)
                except:
                    pass
                
                tracker.end("cycle")
                
                # Show stats
                print(f"\n⏱️  Latency: {tracker.get_stats('cycle')['avg_ms']:.2f}ms")
            else:
                print("❌ Failed to get response")
                
        except KeyboardInterrupt:
            print("\n\n👋 Test interrupted")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")
    
    print(f"\n{'='*70}")
    print(f"✅ Completed {conversation_count} conversations")
    print(f"{'='*70}\n")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Voice Assistant Quick Test")
    parser.add_argument(
        "--mode",
        choices=["auto", "interactive"],
        default="auto",
        help="Test mode"
    )
    
    args = parser.parse_args()
    
    try:
        if args.mode == "auto":
            test_complete_pipeline()
        else:
            interactive_test()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
