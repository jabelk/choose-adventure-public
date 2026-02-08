# Research: Voice Input

## Decision 1: Primary Speech Recognition Approach

**Decision**: Use the Web Speech API (`SpeechRecognition` / `webkitSpeechRecognition`) as the primary voice input method, with `continuous: false` and `interimResults: true`.

**Rationale**: Web Speech API is free, requires no server round-trip, and works on Chrome, Edge, Safari (desktop + iOS), and Android Chrome — covering ~85% of users. Using `continuous: false` avoids known bugs with Safari result duplication and Chrome's 60-second session timeout. `interimResults: true` provides real-time feedback as the user speaks.

**Alternatives considered**:
- `continuous: true` mode: More complex, prone to bugs on Safari (isFinal always false, duplicated results) and Chrome (60s timeout requiring restart with audible sounds on Android). Overkill for short story prompts.
- Server-only approach (always record + Whisper): Adds latency and API cost for every user, even when the browser can do it natively for free.

## Decision 2: Fallback for Unsupported Browsers

**Decision**: Use MediaRecorder API to capture audio, then send to a server-side endpoint that proxies to OpenAI Whisper API. MediaRecorder output (webm/opus from Chrome/Firefox, mp4/AAC from Safari) is sent directly to Whisper with no format conversion.

**Rationale**: Firefox has Web Speech API behind a flag (unusable for end users). MediaRecorder is Baseline Widely Available since 2021 — works in all major browsers. Whisper natively accepts webm, ogg, and mp4 formats, so no server-side audio conversion is needed. This keeps the architecture simple.

**Alternatives considered**:
- Client-side audio conversion to WAV before upload: Adds complexity and increases file size. Unnecessary since Whisper accepts native MediaRecorder formats.
- AssemblyAI or Deepgram as transcription provider: Requires a new API key and account. OpenAI is already integrated for image generation.

## Decision 3: Whisper Model Selection

**Decision**: Use `whisper-1` model with `response_format="text"`, `language="en"`, `temperature=0.0`.

**Rationale**: `whisper-1` is battle-tested and costs $0.006/minute (a 30-second prompt costs ~$0.003). Specifying `language="en"` improves accuracy and reduces latency by skipping auto-detection. `response_format="text"` returns just the transcript string — no JSON parsing needed. `temperature=0.0` gives deterministic output.

**Alternatives considered**:
- `gpt-4o-transcribe`: Higher quality but same price. Could upgrade later if `whisper-1` quality is insufficient for short prompts.
- `gpt-4o-mini-transcribe`: Half the cost ($0.003/min) but newer and less tested. Not worth the risk savings of fractions of a cent per use.

## Decision 4: Feature Detection Strategy

**Decision**: Feature-detect `window.SpeechRecognition || window.webkitSpeechRecognition` at runtime. If present, use browser-native path. If absent, check if server-side transcription is available (via a config flag from the server) and use MediaRecorder fallback. If neither is available, hide the microphone button entirely.

**Rationale**: Feature detection is more reliable than browser sniffing. It correctly handles Edge instability (where SpeechRecognition may exist but fail) by catching errors and falling back transparently.

**Alternatives considered**:
- User-agent sniffing: Brittle, breaks with new browser versions, doesn't handle Edge's intermittent failures.
- Always showing both options: Confusing UX. Users shouldn't need to choose a transcription backend.

## Decision 5: Audio Recording Constraints

**Decision**: Limit recording to 60 seconds maximum. Stop automatically after 10 seconds of silence (for server-side path; browser-native handles silence automatically). Use `audio/webm;codecs=opus` as preferred MIME type, falling back to `audio/mp4` for Safari.

**Rationale**: 60 seconds is more than enough for a story prompt (typically 1-3 sentences). The 25MB Whisper limit won't be hit for 60 seconds of compressed audio. Detecting MIME type at runtime via `MediaRecorder.isTypeSupported()` ensures compatibility across browsers.

**Alternatives considered**:
- Longer recording limits: Unnecessary for story prompts and would increase upload time/cost.
- Fixed MIME type: Would break on Safari which may not support webm in older versions.

## Decision 6: Server Endpoint Design

**Decision**: Add a `POST /{tier}/voice/transcribe` endpoint that accepts multipart audio upload, forwards to Whisper, and returns the transcript as JSON. The endpoint reuses the existing `AsyncOpenAI` client.

**Rationale**: Keeping the endpoint tier-scoped follows the existing router pattern. Reusing the OpenAI client means no new API key configuration — the same key used for DALL-E image generation works for Whisper. The endpoint is simple: receive audio bytes, call Whisper, return text.

**Alternatives considered**:
- A global `/api/transcribe` endpoint outside the tier router: Breaks the consistent `/{tier}/` URL pattern.
- WebSocket-based streaming: Over-engineered for short audio clips. Standard HTTP POST is sufficient.

## Browser Support Matrix

| Browser | SpeechRecognition | MediaRecorder | Voice Input Works? |
|---------|-------------------|---------------|-------------------|
| Chrome (desktop) | Yes (webkit prefix) | Yes | Yes (native) |
| Chrome (Android) | Yes | Yes | Yes (native) |
| Edge (desktop) | Fragile | Yes | Yes (native, fallback if fails) |
| Safari (desktop) | Yes (requires Siri) | Yes | Yes (native) |
| Safari (iOS) | Yes (requires Siri) | Yes | Yes (native, slower) |
| Firefox (all) | No (behind flag) | Yes | Yes (server fallback) |
