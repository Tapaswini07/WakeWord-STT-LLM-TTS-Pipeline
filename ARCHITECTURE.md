# System Architecture & Design

## Overview

The Voice Assistant is built on a modular pipeline architecture where each component handles a specific responsibility. This separation of concerns enables easy testing, maintenance, and optimization.

## High-Level Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                     VOICE ASSISTANT PROTOTYPE                     │
├──────────────────────────────────────────────────────────────────┤
│                                                                    │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │                  VoiceAssistant Orchestrator                 │ │
│  │  • Manages lifecycle of all components                       │ │
│  │  • Handles error recovery and retries                        │ │
│  │  • Coordinates component I/O                                 │ │
│  │  • Measures total end-to-end latency                         │ │
│  └─────────────┬──────────────┬──────────────┬─────────────────┘ │
│                │              │              │                    │
│        ┌───────▼──┐    ┌──────▼──┐    ┌─────▼─────┐              │
│        │  Wake    │    │  STT    │    │    LLM    │              │
│        │  Word    │    │ Pipeline│    │ Integration│              │
│        │Detector  │    │         │    │           │              │
│        └───────┬──┘    └──────┬──┘    └─────┬─────┘              │
│                │              │              │                    │
│        ┌───────▼──────────────▼──────────────▼─────────┐         │
│        │         Latency Tracker & Metrics System      │         │
│        │  • Component-level timing                     │         │
│        │  • Aggregate statistics                       │         │
│        │  • Performance reporting                      │         │
│        └───────┬──────────────────────────────────────┘         │
│                │                                                  │
│        ┌───────▼──────────────────────────┐                     │
│        │      Text-to-Speech (TTS)        │                     │
│        │  • pyttsx3 (Default, Fast)       │                     │
│        │  • gTTS (Natural Sound)          │                     │
│        │  • Multiple voice support        │                     │
│        └───────┬──────────────────────────┘                     │
│                │                                                  │
│        ┌───────▼──────────────────────────┐                     │
│        │        System Output (Speaker)   │                     │
│        └────────────────────────────────────┘                     │
│                                                                    │
└──────────────────────────────────────────────────────────────────┘
                              ▲
                          System Start
```

## Component Details

### 1. Wake Word Detector (`wake_word_detector.py`)

**Purpose**: Continuously listens for activation phrase

**Key Features**:
- Uses Google Speech Recognition API
- Configurable wake word matching
- Adaptive noise filtering
- Timeout and retry handling
- Energy-based voice activity detection

**Configuration**:
```python
WAKE_WORD = "hey assistant"
WAKE_WORD_CONFIDENCE_THRESHOLD = 0.5
WAKE_WORD_TIMEOUT = 30  # seconds
```

**Latency Profile**:
- Single recognition: 600-1500ms
- With retries (3x): 1800-4500ms
- Factors: Network latency, speech clarity, background noise

### 2. Speech-to-Text Pipeline (`speech_to_text.py`)

**Purpose**: Convert spoken words to text after wake word

**Supported Engines**:

| Engine | Speed | Accuracy | Offline | Best For |
|--------|-------|----------|---------|----------|
| Google | 800-2000ms | Very High | No | General use, accents |
| Sphinx | 1000-3000ms | Medium | Yes | Privacy-sensitive |

**Key Methods**:
- `transcribe_audio()`: Convert microphone or file input
- `stream_transcribe()`: Real-time streaming (experimental)
- Automatic ambient noise adjustment
- Language support: 100+ languages

**Configuration**:
```python
STT_ENGINE = "google"
STT_LANGUAGE = "en-US"
SPEECH_RECOGNITION_TIMEOUT = 10
```

### 3. LLM Integration (`llm_integration.py`)

**Purpose**: Process user queries and generate intelligent responses

**Supported Providers**:

#### Groq (Recommended)
```python
class GroqLLMClient:
    • Speed: ~350ms average
    • Model: Mixtral-8x7b-32768
    • Free tier: Very generous (>9000 req/day)
    • Best for: Real-time applications
    • Setup: Get key from https://console.groq.com
```

#### HuggingFace
```python
class HuggingFaceLLMClient:
    • Speed: ~1000-3000ms
    • Models: 100,000+ options
    • Free tier: 30,000 req/month
    • Best for: Experimentation
    • Setup: Get key from https://huggingface.co/settings/tokens
```

#### Ollama (Offline)
```python
class OllamaLLMClient:
    • Speed: ~500-2000ms (depends on model)
    • Models: Local, fully offline
    • Cost: Free (self-hosted)
    • Best for: Privacy, zero latency
    • Setup: Install from https://ollama.ai
```

**Factory Pattern**:
```python
llm = get_llm_client("groq")  # Returns appropriate client
response = llm.generate_response(user_prompt)
```

### 4. Text-to-Speech (`text_to_speech.py`)

**Purpose**: Convert text to natural speech

**Engines**:

| Engine | Speed | Quality | Offline | Voices |
|--------|-------|---------|---------|--------|
| pyttsx3 | 100-400ms | Good | Yes | 2-10 |
| gTTS | 200-500ms | Excellent | No | 14+ |

**Features**:
- Rate control (80-200 wpm)
- Volume adjustment (0.0-1.0)
- Async and sync modes
- Save to file support
- Multiple voice selection

### 5. Latency Tracker (`latency_tracker.py`)

**Purpose**: Measure and report performance metrics

**Features**:
```python
tracker.start("component_name")
# ... do work ...
duration_ms = tracker.end("component_name")

tracker.print_report()  # Show formatted report
stats = tracker.get_stats("component_name")  # Get raw stats
```

**Metrics Collected**:
- Component name
- Start/end timestamps
- Duration in milliseconds
- Statistical aggregates (min, max, avg)

## Data Flow Diagram

```
User spoken input
    │
    ├─ Microphone → PyAudio
    │
    └─ WakeWordDetector
       │ Uses Google Speech Recognition
       │ Checks if "hey assistant" detected
       │
       ├─ NO → Retry (max 3x)
       │        If still NO → Back to listening
       │
       └─ YES → Emit activation signal
                 │
                 └─ CommandListener
                    │ Uses Google STT
                    │ Records next 10 seconds
                    │ Converts to text
                    │
                    └─ Text available
                       │
                       └─ LLM Processor
                          │ Send to Groq/HF/Ollama API
                          │ Get response (usually 1-3 sentences)
                          │
                          └─ Response text
                             │
                             └─ TextToSpeech
                                │ Use pyttsx3 or gTTS
                                │ Convert to audio
                                │ Send to speakers
                                │
                                └─ User hears response

(Then repeat if in continuous mode)
```

## Latency Analysis

### Critical Path Components

```
Total End-to-End Latency = STT_Wake + STT_Command + LLM + TTS

Where:
  • STT_Wake: 600-1500ms (wake word detection)
  • STT_Command: 800-2000ms (command listening)
  • LLM: 200-3000ms (depends on provider)
    - Groq: 200-500ms ✓ Fastest
    - Ollama: 500-2000ms
    - HuggingFace: 1000-3000ms
  • TTS: 100-500ms (text-to-speech)

Total: ~2.5-7.5 seconds end-to-end
```

### Optimization Strategy

1. **Parallel Processing**: Start listening for command BEFORE wake word confidence fully confirmed
2. **Model Selection**: Use Groq for minimal latency
3. **Response Length**: Cap max tokens to reduce TTS time
4. **Caching**: Cache common responses

## Error Handling & Recovery

```
Try:
  1. Wake word detection with retries (3x)
  2. Command listening with timeout (10s)
  3. LLM API call with timeout (30s)
  4. TTS generation
Except:
  • Network error → Retry with backoff
  • Timeout → Friendly error message
  • API error → Fallback to cached response
  • Audio error → Recalibrate and retry
```

## Configuration Management

```python
# config/settings.py
├── Audio settings
│   ├── AUDIO_SAMPLE_RATE = 16000
│   ├── AUDIO_CHUNK_SIZE = 2048
│   └── AUDIO_DEVICE_INDEX = None
├── Wake word settings
│   └── WAKE_WORD = "hey assistant"
├── STT settings
│   ├── STT_ENGINE = "google"
│   └── STT_LANGUAGE = "en-US"
├── LLM settings
│   ├── LLM_PROVIDER = "groq"
│   ├── LLM_MODEL = "mistral-7b-instruct"
│   └── LLM_MAX_TOKENS = 256
├── TTS settings
│   └── TTS_ENGINE = "pyttsx3"
└── Timeout settings
    ├── WAKE_WORD_TIMEOUT = 30
    ├── SPEECH_RECOGNITION_TIMEOUT = 10
    └── LLM_RESPONSE_TIMEOUT = 30
```

## Scalability Considerations

### Vertical Scaling
- Use faster hardware (SSD, CPU-GPU)
- Allocate more memory for audio buffering
- Use local Ollama instead of cloud LLM

### Horizontal Scaling
- Run multiple assistants instances
- Use load balancer (Redis, RabbitMQ)
- Implement session management
- Cache responses globally

### Cloud Deployment
```
┌─────────────────┐
│  Load Balancer  │
└────────┬────────┘
    ┌────┴──────┐
    │    │      │
┌───▼──┐ │ ┌───▼──┐
│Voice │ │ │Voice │
│Asst 1│ │ │Asst 2│
└──────┘ │ └──────┘
       ┌─▼──┐
       │Asst3│
       └─────┘

Database/Cache Layer:
├─ Redis (sessions, cache)
├─ PostgreSQL (user data)
└─ S3 (audio logs)
```

## Security Architecture

```
┌──────────────────────────────┐
│   API Key Management         │
├──────────────────────────────┤
│ • Load from .env (not code)  │
│ • Rotate regularly           │
│ • Use specific scopes        │
│ • Rate limit per key         │
└──────────────────────────────┘

┌──────────────────────────────┐
│   Audio Data Handling        │
├──────────────────────────────┤
│ • Don't log raw audio        │
│ • Encrypt in transit         │
│ • Delete after processing    │
└──────────────────────────────┘

┌──────────────────────────────┐
│   API Credentials            │
├──────────────────────────────┤
│ • Use OAuth2 where available │
│ • Store securely             │
│ • Monitor usage              │
└──────────────────────────────┘
```

## Testing Strategy

```
Unit Tests:
  ├─ STT engine mock
  ├─ LLM API mock
  ├─ TTS output validation
  └─ Latency calculation

Integration Tests:
  ├─ Full pipeline (text input)
  ├─ Component interactions
  ├─ Error recovery
  └─ Timeout handling

Performance Tests:
  ├─ Latency benchmarks
  ├─ Memory profiling
  ├─ Concurrent requests
  └─ Long-running stability
```

## Future Enhancements

1. **Multi-modal**: Support video + voice
2. **Context awareness**: Remember conversation history
3. **Custom wake word**: ML-based detection
4. **Language detection**: Auto-detect user language
5. **Emotion recognition**: Adjust tone based on user emotion
6. **Multi-user**: Speaker identification
7. **Device integration**: Control IoT devices
8. **Analytics**: Conversation insights

---

**Architecture designed for production deployment, scalability, and maintainability.**
