# Feature Specification: Voice Input

**Feature Branch**: `010-voice-input`
**Created**: 2026-02-07
**Status**: Draft
**Input**: User description: "Voice Input - Add voice input for story prompts so users can speak their adventure idea instead of typing. Support both browser-native Web Speech API and OpenAI Whisper API as backends. The voice input should work from the home page prompt form, with a microphone button that records speech and fills in the text area. Should work on both desktop and mobile browsers."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Speak a Story Prompt via Browser Speech Recognition (Priority: P1)

A user visits the home page and wants to describe their adventure idea by speaking instead of typing. They tap a microphone button next to the prompt text area. The browser listens to their speech, and the transcribed text appears in the text area in real time. When they stop speaking (or tap the button again to stop), the final transcription is in the text area, ready to edit or submit. This uses the browser's built-in speech recognition — no server round-trip needed.

**Why this priority**: This delivers the core voice input experience with zero additional infrastructure. Browser-native speech recognition works immediately on Chrome, Edge, Safari, and most mobile browsers without any API keys or server costs. It covers the majority use case.

**Independent Test**: Tap the microphone button on the home page, speak a story prompt, verify the text appears in the text area, then submit normally.

**Acceptance Scenarios**:

1. **Given** the user is on the home page, **When** they tap the microphone button, **Then** the browser requests microphone permission and begins listening (button shows active/recording state)
2. **Given** speech recognition is active, **When** the user speaks, **Then** transcribed text appears in the prompt text area in real time
3. **Given** speech recognition is active, **When** the user taps the microphone button again (or stops speaking for a few seconds), **Then** recognition stops, the final text remains in the text area, and the button returns to its idle state
4. **Given** the text area already has typed text, **When** the user activates voice input, **Then** the spoken text is appended to the existing text (not replaced)
5. **Given** transcribed text is in the text area, **When** the user edits the text and clicks "Begin Adventure", **Then** the story starts normally using the edited text

---

### User Story 2 - Speak a Story Prompt via Server-Side Transcription (Priority: P2)

A user's browser does not support the native speech recognition capability (e.g., Firefox, or an older mobile browser). The system falls back to recording audio in the browser and sending it to a server-side transcription service. The user taps the microphone button, speaks, and the recorded audio is sent to the server for transcription. The transcribed text is returned and placed in the text area.

**Why this priority**: This extends voice input to browsers that lack native speech recognition support. It requires a server endpoint and an external transcription service API key, but ensures voice input works universally.

**Independent Test**: Using a browser without native speech recognition (e.g., Firefox), tap the microphone button, speak a prompt, verify the audio is sent to the server and transcribed text appears in the text area.

**Acceptance Scenarios**:

1. **Given** the user's browser does not support native speech recognition, **When** they tap the microphone button, **Then** the system records audio using the browser's media recording capabilities
2. **Given** audio recording is active, **When** the user taps the microphone button again to stop, **Then** the recorded audio is sent to the server for transcription
3. **Given** audio has been sent to the server, **When** transcription completes, **Then** the transcribed text appears in the text area and the user can edit or submit it
4. **Given** audio has been sent to the server, **When** transcription is in progress, **Then** a loading indicator shows the user that processing is happening
5. **Given** the server transcription fails (network error, API error), **When** the error occurs, **Then** the user sees a friendly error message and can retry or type manually

---

### Edge Cases

- What happens when the user denies microphone permission? The microphone button shows an error state and a message explaining that microphone access is needed. The user can still type normally.
- What happens when the user speaks for a very long time? Speech recognition should handle continuous speech up to a reasonable limit (60 seconds). After the limit, recognition stops automatically and the captured text is preserved.
- What happens in a noisy environment with poor recognition? The transcribed text appears in the editable text area, so the user can correct any errors before submitting.
- What happens if no speech is detected? After a timeout period (10 seconds of silence), recognition stops and the button returns to idle. If no text was captured, the text area remains unchanged.
- What happens if the server-side transcription service API key is not configured? The system only offers browser-native voice input. The server fallback is hidden if the service is unavailable.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST display a microphone button adjacent to the story prompt text area on the home page
- **FR-002**: System MUST request microphone permission from the browser when the user activates voice input for the first time
- **FR-003**: System MUST show a clear visual indicator (button state change, pulsing animation) when voice recording is active
- **FR-004**: System MUST transcribe speech and place the resulting text into the prompt text area
- **FR-005**: System MUST append transcribed text to any existing text in the prompt area rather than replacing it
- **FR-006**: System MUST allow the user to stop recording by tapping the microphone button again
- **FR-007**: System MUST automatically stop recording after 60 seconds of continuous input or 10 seconds of silence
- **FR-008**: System MUST support browser-native speech recognition as the primary input method
- **FR-009**: System MUST fall back to server-side audio transcription when browser-native speech recognition is unavailable
- **FR-010**: System MUST show a loading indicator while server-side transcription is in progress
- **FR-011**: System MUST display a user-friendly error message if voice input fails (permission denied, transcription error, network failure)
- **FR-012**: System MUST work on both desktop and mobile browsers
- **FR-013**: System MUST hide the server-side fallback option if no transcription service is configured on the server
- **FR-014**: The microphone button MUST be accessible (keyboard focusable, screen-reader labeled)

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can speak a story prompt and see transcribed text in the text area within 3 seconds of finishing speaking (browser-native mode)
- **SC-002**: Users can speak a story prompt and see transcribed text within 10 seconds of stopping recording (server-side mode, including upload and processing time)
- **SC-003**: Voice input works on at least 3 major browser families (Chrome/Edge, Safari, Firefox via fallback)
- **SC-004**: Voice input is functional on mobile devices (iOS Safari, Android Chrome) with no additional user steps beyond tapping the microphone button
- **SC-005**: 90% of spoken prompts produce usable text that requires only minor edits before submission

## Assumptions

- Users have a working microphone on their device (built-in or external)
- The app is accessed over HTTPS (required for microphone access in browsers) or localhost
- Browser-native speech recognition is available on Chrome, Edge, and Safari (covers ~85% of users)
- For server-side fallback, the OpenAI API key already configured for image generation can also be used for the Whisper transcription endpoint
- Audio recording quality from device microphones is sufficient for accurate transcription
- The feature is available on all tiers (kids and nsfw) since it's just an input method
