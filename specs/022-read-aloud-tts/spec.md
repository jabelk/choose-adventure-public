# Feature Specification: Read Aloud / TTS Narration

**Feature Branch**: `022-read-aloud-tts`
**Created**: 2026-02-07
**Status**: Draft
**Input**: User description: "Read Aloud / TTS Narration — Auto-read each scene aloud using text-to-speech. Play button per scene on both tiers. Uses OpenAI TTS API (already have the API key configured). Huge for the 2.5-year-old who can't read yet — lets her use the app more independently. Could also highlight words as they're read for the 5-year-old learning to read. Both tiers should get this feature. Scene text is already available in the template. Add a speaker/play button on each scene page that reads the scene content aloud. Auto-play option for kids tier so it reads automatically when a new scene loads. Voice selection (at least a couple of options). Persist voice preference per tier/profile."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Play Button Reads Scene Aloud (Priority: P1)

The user views a story scene and sees a speaker/play button. When they tap the button, the scene's text content is read aloud through their device speakers. The button toggles between play and stop states. While audio is playing, the user can stop it at any time. This works on both the kids tier and the NSFW tier.

The primary user is a 2.5-year-old who cannot read — tapping a single big play button lets her experience the story independently. The secondary user is an adult who may want hands-free narration.

**Why this priority**: This is the core feature. Without a play button that reads text aloud, none of the other enhancements (auto-play, word highlighting, voice selection) have value. A single play button on the scene page is a complete, usable MVP.

**Independent Test**: Navigate to any story scene, tap the play button, and verify the scene text is read aloud through the device speakers. Tap again to stop.

**Acceptance Scenarios**:

1. **Given** the user is viewing a story scene, **When** they see the scene page, **Then** a speaker/play button is visible near the scene text.
2. **Given** the user taps the play button, **When** audio generation completes, **Then** the scene's narrative text is read aloud through device speakers.
3. **Given** the audio is currently playing, **When** the user taps the button again, **Then** playback stops immediately.
4. **Given** the audio is currently playing, **When** the user navigates to a different scene, **Then** playback stops automatically.
5. **Given** the scene text contains choices at the end, **When** the text is read aloud, **Then** only the narrative content is read — not the choice button labels.
6. **Given** the user is on a scene in the gallery reader (completed story), **When** they tap play, **Then** the scene is read aloud (works in both active stories and gallery).

---

### User Story 2 - Auto-Play on Kids Tier (Priority: P2)

When a new scene loads on the kids tier, the narration automatically begins playing without requiring any tap. This makes the experience completely hands-free for a toddler — each scene reads itself as the story progresses. Auto-play can be toggled off by the parent if desired. Auto-play is off by default on the NSFW tier but can be turned on.

**Why this priority**: Auto-play transforms the kids tier from "parent reads each scene" to "child can experience the story solo." This is the biggest quality-of-life improvement for the target user (2.5-year-old). However, it builds on the play button from US1.

**Independent Test**: Start a story on the kids tier, verify narration begins automatically on each scene load. Toggle auto-play off and verify it stops auto-playing.

**Acceptance Scenarios**:

1. **Given** the user is on the kids tier, **When** a new scene loads (start or after a choice), **Then** narration begins automatically without user interaction.
2. **Given** auto-play is active, **When** the user taps the stop button, **Then** narration stops and auto-play is paused for this scene only (resumes on next scene).
3. **Given** auto-play is active on the kids tier, **When** the user navigates to the home page or gallery, **Then** auto-play does not trigger (only activates on story scene pages).
4. **Given** the user is on the NSFW tier, **When** a new scene loads, **Then** narration does NOT auto-play by default.
5. **Given** the user toggles auto-play on or off, **When** they navigate to a new scene, **Then** their preference is remembered for the session.

---

### User Story 3 - Voice Selection (Priority: P3)

The user can choose from multiple voice options for the narration. Different voices suit different story moods — a warm, friendly voice for kids stories vs. a more dramatic voice for adult stories. The voice preference persists so the user doesn't have to re-select each time.

**Why this priority**: Voice selection personalizes the experience and avoids a voice that might not suit the tier's tone. However, the default voice works fine as an MVP — this is a polish feature.

**Independent Test**: Open the voice selector, pick a different voice, play a scene, and verify the new voice is used. Navigate away and come back — verify the preference persisted.

**Acceptance Scenarios**:

1. **Given** the user views a scene page, **When** they look for voice options, **Then** they see a voice selector (dropdown or small picker) near the play button.
2. **Given** the user selects a different voice, **When** they play a scene, **Then** the narration uses the newly selected voice.
3. **Given** the user has selected a voice preference, **When** they start a new story or return later in the same session, **Then** the same voice is used without re-selecting.
4. **Given** the kids tier and NSFW tier, **When** the user views voice options, **Then** each tier shows voices appropriate to its tone (warm/friendly for kids, varied for adult).

---

### User Story 4 - Word Highlighting During Playback (Priority: P4)

As the narration plays, the currently spoken word or sentence is visually highlighted in the scene text. This helps the 5-year-old who is learning to read follow along and connect spoken words with written text. Highlighting advances in sync with the audio.

**Why this priority**: Word highlighting is a significant educational enhancement for the older child but adds substantial complexity. The narration feature is fully usable without it. This is a stretch goal.

**Independent Test**: Play a scene with highlighting enabled, verify words/sentences highlight in sync with the spoken audio.

**Acceptance Scenarios**:

1. **Given** narration is playing, **When** the audio progresses, **Then** the currently spoken sentence is visually highlighted in the scene text.
2. **Given** the user stops narration mid-sentence, **When** playback stops, **Then** the highlighting is cleared.
3. **Given** the scene has multiple paragraphs, **When** narration plays through, **Then** highlighting advances paragraph by paragraph, scrolling the text into view if needed.
4. **Given** the user is on a mobile device, **When** highlighting is active, **Then** the text auto-scrolls smoothly to keep the highlighted portion visible.

---

### Edge Cases

- What happens when the device has no speakers or audio is muted? The play button still works (triggers audio playback), but no sound is heard. The button state still toggles correctly.
- What happens if audio generation fails (network error, service error)? The play button shows a brief error state and returns to the ready state. The user can retry.
- What happens on very long scenes? The full scene text is narrated. For scenes exceeding the text-to-speech service's character limit, the text is split into chunks and played sequentially.
- What happens when the user makes a choice while audio is still playing? Audio stops immediately, and the new scene loads (with auto-play if enabled).
- What happens in the gallery reader? Read aloud works the same way — play button available on each saved scene.
- What happens if the audio service is unavailable (no API key configured)? The play button does not appear. No error shown — feature is silently absent.
- What happens on multiple rapid play/stop taps? The system debounces — only the most recent action takes effect. No overlapping audio.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Each story scene page MUST display a play/stop button that triggers text-to-speech narration of the scene's narrative content.
- **FR-002**: The play button MUST toggle between play and stop states, stopping audio immediately when tapped during playback.
- **FR-003**: Only the scene's narrative text MUST be read aloud — choice labels, UI elements, and metadata MUST be excluded from narration.
- **FR-004**: Audio playback MUST stop automatically when the user navigates away from the current scene.
- **FR-005**: The kids tier MUST auto-play narration when a new scene loads (auto-play on by default).
- **FR-006**: The NSFW tier MUST NOT auto-play narration by default.
- **FR-007**: The user MUST be able to toggle auto-play on or off, and the preference MUST persist for the session.
- **FR-008**: The user MUST be able to select from at least 4 voice options for narration.
- **FR-009**: The selected voice preference MUST persist across scenes within a session.
- **FR-010**: The play button MUST be available on both active story scenes and gallery reader scenes.
- **FR-011**: If the text-to-speech service is unavailable (no API key), the play button MUST NOT appear — the feature is silently absent.
- **FR-012**: If a scene's text exceeds the service's per-request character limit, the system MUST split the text and play segments sequentially.
- **FR-013**: During narration, the currently spoken sentence MUST be visually highlighted in the scene text (P4 stretch goal).
- **FR-014**: The play button MUST work on mobile devices with touch interaction.

### Key Entities

- **Audio Narration**: A generated audio rendition of a scene's narrative text, associated with a specific scene and voice selection. May be cached to avoid re-generation on replay.
- **Voice Preference**: The user's selected voice for narration, stored per session. Includes voice identifier and auto-play toggle state.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can hear a scene read aloud within 3 seconds of tapping the play button on a typical scene (under 500 words).
- **SC-002**: Auto-play narration begins within 3 seconds of a new scene loading on the kids tier.
- **SC-003**: 100% of story scenes (active and gallery) display the play button when the audio service is available.
- **SC-004**: Audio playback stops within 500ms of the user tapping stop or navigating away.
- **SC-005**: Voice preference persists across all scenes within a single story session without re-selection.
- **SC-006**: The kids tier is fully usable by a non-reading child (can tap play or have auto-play, hear the story, and tap choices to continue).

## Assumptions

- The text-to-speech service is accessed via the same API key already configured for image generation and voice transcription.
- Audio is generated server-side and streamed/returned to the client as a playable audio file.
- Audio is not permanently stored — it is generated on demand each time the play button is tapped. Caching within a session is acceptable but not required for MVP.
- The scene's narrative text is available as plain text (stripped of any markup) for TTS input.
- Auto-play preference is session-scoped (not persisted to disk). If the user closes the browser and returns, auto-play returns to the tier default.
- Voice options are provided by the TTS service — the app surfaces whichever voices the service offers. A reasonable default is pre-selected per tier.
- Word-level highlighting (US4) requires timing data from the TTS service. If timing data is not available, sentence-level highlighting based on estimated reading speed is an acceptable fallback.
- The play button should be large and easy to tap on mobile, especially on the kids tier where the user is a toddler.
- Gallery reader scenes also get the play button — narration works on completed stories, not just active ones.

## Scope Boundaries

**In scope**:
- Play/stop button on scene pages (both tiers, active and gallery)
- Server-side TTS audio generation
- Auto-play toggle (on by default for kids, off for NSFW)
- Voice selection with session persistence
- Sentence highlighting during playback (stretch goal)
- Mobile-friendly play button

**Out of scope**:
- Narrating choice labels or UI elements
- Permanent audio storage or audio gallery
- Background music or sound effects
- Reading the scene text in multiple languages
- Offline TTS (requires network for service calls)
- Custom voice training or voice cloning
- Narration speed control (use default speed)
