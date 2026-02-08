# Tasks: Voice Input

**Input**: Design documents from `/specs/010-voice-input/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: No tests requested in the feature specification. Manual testing via quickstart.md.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2)
- Include exact file paths in descriptions

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: No new dependencies needed — OpenAI SDK already installed. Create the voice input JS module skeleton and CSS.

- [X] T001 [P] Create static/js/voice-input.js with module skeleton: `initVoiceInput(textareaId, urlPrefix)` entry point, feature detection for `SpeechRecognition`/`webkitSpeechRecognition`, and constants for MAX_RECORDING_SECONDS (60) and SILENCE_TIMEOUT_MS (10000)
- [X] T002 [P] Add microphone button and voice input CSS styles to static/css/style.css — `.btn-mic` with three states (idle, recording with pulse animation, processing with spinner), `.voice-error` inline message style, and `.voice-status` indicator

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Add the microphone button to the home page template and wire up the JS module. Both user stories depend on the button being present in the DOM.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T003 Add microphone button to templates/home.html — place a `<button class="btn-mic">` with SVG microphone icon adjacent to the prompt textarea, add `aria-label="Voice input"` for accessibility, and include a `<span class="voice-error">` for inline error messages
- [X] T004 Add `<script src="/static/js/voice-input.js">` to templates/home.html and call `initVoiceInput('prompt', urlPrefix)` passing the textarea ID and tier URL prefix
- [X] T005 Add `GET /{tier}/voice/status` route to app/routes.py inside `create_tier_router()` — returns JSON `{"available": true}` if `settings.openai_api_key` is configured, `{"available": false}` otherwise (FR-013)

**Checkpoint**: Microphone button visible on home page, voice/status endpoint responds — ready for both user stories

---

## Phase 3: User Story 1 — Browser-Native Speech Recognition (Priority: P1) 🎯 MVP

**Goal**: Users can tap the microphone button, speak their adventure prompt, and see transcribed text appear in the text area in real time using the browser's built-in speech recognition. No server needed.

**Independent Test**: Open Chrome or Safari, tap mic button, speak a prompt, verify text appears in textarea, submit normally. (Quickstart steps 2-4)

### Implementation for User Story 1

- [X] T006 [US1] Implement browser-native speech recognition path in static/js/voice-input.js — on mic button click: check for `SpeechRecognition`/`webkitSpeechRecognition`, create instance with `lang='en-US'`, `interimResults=true`, `continuous=false`, handle `onresult` to append transcript to textarea (FR-004, FR-005), handle `onend` to reset button state
- [X] T007 [US1] Implement mic button state management in static/js/voice-input.js — toggle between idle/recording/processing states on click (FR-003, FR-006), update button CSS class and aria-label, prevent double-start by tracking recognition state
- [X] T008 [US1] Implement auto-stop and timeout logic in static/js/voice-input.js — set a 60-second maximum recording timer (FR-007), handle `onerror` event for `no-speech` to stop after silence, handle `not-allowed` error to show permission denied message (FR-011)
- [X] T009 [US1] Implement error handling and permission flow in static/js/voice-input.js — catch `not-allowed` error to display "Microphone access is needed" in `.voice-error` span (FR-002, FR-011), catch `network` error for offline scenarios, catch `audio-capture` for missing microphone

**Checkpoint**: Browser-native voice input fully functional — users can speak prompts on Chrome/Safari/Edge with no server dependency

---

## Phase 4: User Story 2 — Server-Side Transcription Fallback (Priority: P2)

**Goal**: Users on browsers without native speech recognition (Firefox) can still use voice input via MediaRecorder + server-side Whisper transcription.

**Independent Test**: Open Firefox, tap mic button, speak a prompt, verify audio is sent to server and transcribed text appears in textarea. (Quickstart step 5)

### Implementation for User Story 2

- [X] T010 [US2] Create app/services/voice.py with `transcribe_audio(audio_bytes, filename)` function — use existing `AsyncOpenAI` client to call `client.audio.transcriptions.create()` with model `whisper-1`, `response_format="text"`, `language="en"`, wrap audio bytes in `BytesIO` with `.name` set to filename for format detection
- [X] T011 [US2] Add `POST /{tier}/voice/transcribe` route to app/routes.py inside `create_tier_router()` — accept `UploadFile` named `audio`, validate file is present and under 25 MB, call `transcribe_audio()`, return JSON `{"text": "..."}`, handle errors with appropriate status codes per contracts/routes.md
- [X] T012 [US2] Implement MediaRecorder fallback path in static/js/voice-input.js — on mic button click when SpeechRecognition is unavailable: call `navigator.mediaDevices.getUserMedia({audio: true})`, detect best MIME type via `MediaRecorder.isTypeSupported()` (prefer `audio/webm;codecs=opus`, fall back to `audio/mp4`), record audio chunks, on stop assemble into Blob
- [X] T013 [US2] Implement server upload and response handling in static/js/voice-input.js — on recording stop: set button to processing state, create `FormData` with audio Blob, POST to `/{tier}/voice/transcribe`, on success append returned text to textarea (FR-005), on error show message in `.voice-error` span (FR-011), show loading indicator during upload (FR-010)
- [X] T014 [US2] Implement fallback detection flow in static/js/voice-input.js — on page load: if SpeechRecognition unavailable, fetch `/{tier}/voice/status`, if `available: true` enable MediaRecorder path, if `available: false` hide mic button entirely (FR-013)

**Checkpoint**: Server-side transcription fully functional — Firefox users can speak prompts via Whisper fallback

---

## Phase 5: Polish & Cross-Cutting Concerns

**Purpose**: Edge cases, accessibility, and end-to-end validation

- [X] T015 Verify microphone button is keyboard-focusable and has proper ARIA attributes in templates/home.html — test with Tab key navigation and screen reader (FR-014)
- [X] T016 Verify voice input works with existing typed text — type partial prompt, speak additional text, confirm append behavior (FR-005)
- [X] T017 Verify graceful degradation when OpenAI API key is missing — unset key, restart server, confirm mic button hidden on Firefox and visible on Chrome (FR-013)
- [X] T018 Run full quickstart.md validation (all 8 steps) to confirm end-to-end functionality

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion — BLOCKS all user stories
- **User Story 1 (Phase 3)**: Depends on Foundational phase (T003, T004, T005)
- **User Story 2 (Phase 4)**: Depends on Foundational phase (T003, T004, T005)
- **Polish (Phase 5)**: Depends on both user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) — no dependencies on US2
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) — no dependencies on US1, but shares voice-input.js

### Within Each User Story

- Feature detection logic before event handlers
- Core recognition/recording logic before error handling
- Client-side before server-side (US2)

### Parallel Opportunities

- T001 and T002 can run in parallel (different files: JS vs CSS)
- T006 and T007 affect the same file but are logically sequential
- T010 (service) and T012 (JS MediaRecorder) can be developed concurrently (different files)

---

## Parallel Example: User Story 1

```bash
# Setup tasks run in parallel (different files):
Task: "Create voice-input.js skeleton"                    # T001
Task: "Add mic button CSS styles"                         # T002

# Foundational tasks are sequential (same template file):
Task: "Add mic button to home.html"                       # T003
Task: "Wire up voice-input.js in home.html"               # T004
Task: "Add voice/status route"                            # T005

# US1 tasks are sequential (same JS file, building on each other):
Task: "Implement SpeechRecognition path"                  # T006
Task: "Implement button state management"                 # T007
Task: "Implement auto-stop/timeout"                       # T008
Task: "Implement error handling"                          # T009
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (JS skeleton, CSS)
2. Complete Phase 2: Foundational (mic button in template, voice/status route)
3. Complete Phase 3: User Story 1 (browser-native SpeechRecognition)
4. **STOP and VALIDATE**: Test voice input on Chrome and Safari
5. Voice input is functional for ~85% of users — no server cost

### Incremental Delivery

1. Setup + Foundational → Mic button visible, no functionality yet
2. Add User Story 1 → Browser-native voice input → Works on Chrome/Safari/Edge
3. Add User Story 2 → Server fallback → Works on Firefox too
4. Each story adds browser coverage without breaking the other

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- No new pip dependencies needed — OpenAI SDK already has Whisper support
- voice-input.js is a single file modified by both stories — US2 builds on US1's button/state management
- The voice/status endpoint reuses existing `settings.openai_api_key` check — no new env vars
- Commit after each phase completion
- Stop at any checkpoint to validate independently
