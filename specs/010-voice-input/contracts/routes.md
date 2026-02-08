# Route Contracts: Voice Input

## New Routes

### POST `/{tier}/voice/transcribe` (new)

**Purpose**: Accept an audio recording from the browser and return a text transcription via server-side speech-to-text.

**Request**: Multipart form data with a single audio file field.

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| audio | file (binary) | Yes | Audio blob from MediaRecorder. Accepted formats: webm, mp4, ogg. Max 25 MB. |

**Behavior**:
1. Validate the upload is present and under 25 MB
2. Forward the audio bytes to the OpenAI Whisper transcription API
3. Return the transcription text

**Response**: JSON

```json
{
  "text": "A brave knight sets out on a quest to find a magical dragon"
}
```

**Error responses**:

| Status | Body | When |
|--------|------|------|
| 400 | `{"error": "No audio file provided"}` | Missing audio field |
| 400 | `{"error": "Audio file too large (max 25 MB)"}` | File exceeds 25 MB |
| 500 | `{"error": "Transcription failed"}` | Whisper API error or network failure |
| 503 | `{"error": "Transcription service unavailable"}` | OpenAI API key not configured |

### GET `/{tier}/voice/status` (new)

**Purpose**: Let the frontend know whether server-side transcription is available, so the JS can decide whether to show the MediaRecorder fallback path.

**Request**: No body or parameters.

**Response**: JSON

```json
{
  "available": true
}
```

Returns `"available": false` if no transcription service API key is configured.

## Modified Templates

### home.html

- Add a microphone button (icon) adjacent to the prompt text area
- The button triggers voice input via JavaScript
- Button has three visual states: idle, recording (pulsing), processing (spinner)
- Error messages appear inline below the text area when voice input fails

## New JavaScript

### static/js/voice-input.js (new)

**Purpose**: Client-side JavaScript module that handles both voice input paths.

**Behavior**:
1. On page load, feature-detect `SpeechRecognition` / `webkitSpeechRecognition`
2. If available: use browser-native path
3. If not available: check `/{tier}/voice/status` endpoint
4. If server transcription available: use MediaRecorder + POST path
5. If neither available: hide the microphone button
6. Handle microphone permission request on first click
7. Show real-time transcription feedback (browser-native path)
8. Show loading state during server transcription
9. Append transcribed text to existing textarea content
10. Handle errors with user-friendly inline messages
