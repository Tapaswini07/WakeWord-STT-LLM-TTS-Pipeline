# Quick Start Guide

Get the voice assistant running in 5 minutes!

## Step 1: Install Dependencies (1 minute)

```bash
cd voice_assistant
pip install -r requirements.txt
```

## Step 2: Get a Free LLM API Key (2 minutes)

### Option A: Groq (Recommended - Fastest)

1. Go to https://console.groq.com
2. Sign up for free account
3. Copy your API key
4. Create `.env` file:
   ```
   GROQ_API_KEY=your_key_here
   LLM_PROVIDER=groq
   ```

### Option B: Ollama (Local - No Key Needed)

1. Download from https://ollama.ai
2. Install and run: `ollama run neural-chat`
3. Create `.env` file:
   ```
   LLM_PROVIDER=ollama
   LLM_ENDPOINT=http://localhost:11434/api/generate
   ```

### Option C: HuggingFace (More Models Available)

1. Go to https://huggingface.co/settings/tokens
2. Create read-only API token
3. Create `.env` file:
   ```
   HF_API_KEY=your_key_here
   LLM_PROVIDER=huggingface
   ```

## Step 3: Test Components (1 minute)

```bash
python demo.py --mode test
```

This will verify:
- ✅ Microphone access
- ✅ Text-to-speech working
- ✅ LLM API connected
- ✅ Latency measurement

## Step 4: Run the Assistant (1 minute)

```bash
# Interactive menu
python demo.py

# Or direct commands:
python demo.py --mode basic        # Single conversation
python demo.py --mode continuous   # Keep listening
python demo.py --mode pipeline     # Text input (no voice)
```

## First Interaction Example

```
Assistant: 🎤 Voice Assistant Ready!
Assistant: Say 'hey assistant' to activate...

You:       "Hey assistant"
System:    ✅ Wake word detected!
System:    🎤 Listening for your command...

You:       "Kya haal chaal?" (How are you?)
System:    📝 Command received: 'kya haal chaal'
System:    🤖 Processing with LLM
System:    ✅ LLM Response: Main bilkul theek hoon! Aapka din kaisa chal raha hai?
System:    🔊 Speaking: Main bilkul theek hoon! Aapka din kaisa chal raha hai?
System:    [System speaks response]

⏱️  Latency Report:
    - Wake word detection: 850ms
    - Command listening: 1200ms
    - LLM inference: 350ms
    - Text-to-speech: 210ms
    - Total: 2610ms
```

## Troubleshooting Quick Fixes

### "ModuleNotFoundError: No module named 'speech_recognition'"
```bash
pip install --upgrade SpeechRecognition
```

### "Microphone not found"
- Ensure microphone is plugged in and unmuted
- Check volume isn't muted at system level
- For USB mics: Re-seat the connection

### "LLM API Error - 401 Unauthorized"
- Verify API key is correct in `.env`
- Check you copied entire key (no extra spaces)
- For Groq: Visit https://console.groq.com to confirm quota

### "Could not understand audio"
- Speak more clearly and louder
- Reduce background noise
- Increase `energy_threshold` in `config/settings.py`

### "TTS not working"
- Ensure speakers are connected and unmuted
- Try: `python demo.py --mode pipeline` (text input only)

## Performance Tips

### Make it Faster ⚡
```python
# In config/settings.py
LLM_MAX_TOKENS = 128      # Shorter responses
LLM_TEMPERATURE = 0.5     # Faster, more deterministic
AUDIO_CHUNK_SIZE = 4096   # Larger chunks
```

### Make it More Accurate 🎯
```python
# In config/settings.py
LLM_MAX_TOKENS = 512      # Longer responses
LLM_TEMPERATURE = 0.7     # More creative
WAKE_WORD_CONFIDENCE_THRESHOLD = 0.8  # Stricter
```

### Make it Private 🔒
```
# Use Ollama (local, offline)
LLM_PROVIDER=ollama
LLM_ENDPOINT=http://localhost:11434/api/generate
```

## Next Steps

1. **Customize wake word**: Edit `WAKE_WORD` in `config/settings.py`
2. **Change voice**: Edit TTS settings for different voices
3. **Add custom logic**: Extend `VoiceAssistant` class
4. **Deploy**: Use Docker for production

## Full Documentation

- 📖 [README.md](README.md) - Complete guide
- 🏗️ [ARCHITECTURE.md](ARCHITECTURE.md) - System design
- ⏱️ [LATENCY_BENCHMARK.md](LATENCY_BENCHMARK.md) - Performance data
- 💻 Source code with detailed comments

---

**Ready to go! Happy voice assisting! 🎉**
