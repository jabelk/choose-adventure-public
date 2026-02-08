# Data Model: Voice Input

## No Persistent Entities Needed

Voice input is an ephemeral input method. Audio is captured, transcribed, and the resulting text is placed into the prompt text area. No audio data is stored on disk or in the database.

## Transient Data Flow

```text
User speaks into microphone
       │
       ▼
┌──────────────────────────────┐
│ Path A: Browser-Native       │
│ (SpeechRecognition API)      │
│                              │
│ Audio → Browser engine →     │
│ Transcript text              │
│ (never leaves the browser)   │
└──────────┬───────────────────┘
           │
           ▼
    Text placed in prompt textarea
           │
           ▼
    User edits and submits (existing flow)


┌──────────────────────────────┐
│ Path B: Server Fallback      │
│ (MediaRecorder → Whisper)    │
│                              │
│ Audio → MediaRecorder blob → │
│ HTTP POST to server →        │
│ OpenAI Whisper API →         │
│ Transcript text returned     │
│ (audio discarded after call) │
└──────────┬───────────────────┘
           │
           ▼
    Text placed in prompt textarea
           │
           ▼
    User edits and submits (existing flow)
```

## Configuration

The only new configuration needed is a server-side flag indicating whether the Whisper transcription endpoint is available. This is derived from the existing `OPENAI_API_KEY` environment variable — if the key is configured, the transcription endpoint is available.

No new environment variables are required.
