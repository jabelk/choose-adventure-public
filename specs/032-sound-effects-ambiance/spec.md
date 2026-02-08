# Feature Specification: Sound Effects / Ambiance

**Feature Branch**: `032-sound-effects-ambiance`
**Created**: 2026-02-08
**Status**: Draft
**Input**: User description: "Sound Effects / Ambiance — Short ambient audio clips per scene type: forest sounds, ocean waves, dragon roar, magical sparkle, spaceship hum. Simple audio tags with a handful of stock clips mapped by scene keywords. Auto-play on scene load with a mute toggle. Both tiers."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Ambient Audio on Scene Load (Priority: P1)

When a user navigates to a new story scene, a short ambient audio clip automatically plays in the background based on the scene's content. The system analyzes scene keywords (e.g., "forest," "ocean," "dragon," "magic," "spaceship") and selects an appropriate audio clip from a curated library. The audio loops softly, creating atmosphere without distracting from the story.

**Why this priority**: This is the core feature — without automatic ambient audio, the feature has no purpose. It delivers the primary value of immersive atmosphere during story reading.

**Independent Test**: Start a story, navigate to a scene that contains a keyword like "forest" or "ocean," and verify that the corresponding ambient audio clip plays automatically.

**Acceptance Scenarios**:

1. **Given** a user navigates to a scene containing the word "forest" or "trees", **When** the scene loads, **Then** a forest-themed ambient audio clip begins playing automatically.
2. **Given** a user navigates to a scene containing the word "ocean" or "sea" or "beach", **When** the scene loads, **Then** an ocean-themed ambient audio clip begins playing.
3. **Given** a user navigates to a scene with no matching keywords, **When** the scene loads, **Then** no audio plays (silence is the default).
4. **Given** a user navigates from one scene to another, **When** the new scene loads with a different ambient category, **Then** the previous audio stops and the new audio begins.

---

### User Story 2 - Mute Toggle (Priority: P2)

A visible mute/unmute toggle button allows the user to silence ambient audio at any time. The mute preference persists across scenes within the same session — if the user mutes audio on one scene, it stays muted on subsequent scenes until they unmute.

**Why this priority**: Essential for user control — some users (or situations like bedtime) require silence. Without a mute toggle, auto-playing audio would be annoying.

**Independent Test**: Navigate to a scene with ambient audio, click the mute toggle, verify audio stops, navigate to the next scene, verify audio does not play, click unmute, verify audio resumes.

**Acceptance Scenarios**:

1. **Given** a scene with ambient audio playing, **When** the user clicks the mute toggle, **Then** the audio stops immediately and the toggle shows a "muted" state.
2. **Given** the user has muted audio, **When** they navigate to a new scene, **Then** the new scene's audio does not play and the toggle remains in "muted" state.
3. **Given** the user has muted audio, **When** they click the toggle again, **Then** the audio resumes and the toggle shows an "unmuted" state.

---

### User Story 3 - Both Tiers (Priority: P3)

Ambient audio works identically on both Kids and NSFW tiers, using the same audio library and mute toggle. The same keyword mapping and audio clips apply across tiers.

**Why this priority**: Feature scope requirement — both tiers need it. Lower priority since the implementation is shared via the router factory pattern.

**Independent Test**: Start a Kids tier story and an NSFW tier story with similar scene content, verify both play ambient audio and the mute toggle works on each.

**Acceptance Scenarios**:

1. **Given** a Kids tier scene with forest content, **When** the scene loads, **Then** the forest ambient clip plays.
2. **Given** an NSFW tier scene with ocean content, **When** the scene loads, **Then** the ocean ambient clip plays.

---

### Edge Cases

- What happens when a scene matches multiple ambient categories (e.g., "a forest near the ocean")? The system picks the first matching category in priority order (the keyword list is checked top to bottom).
- What happens when the browser blocks autoplay? The audio is silenced gracefully; the mute toggle shows as "muted" and the user can click to enable audio (browsers allow playback after user interaction).
- What happens during bedtime mode? Ambient audio respects bedtime mode — if bedtime mode is active, audio defaults to muted to avoid disturbing sleep routines.
- What happens in the gallery reader? Ambient audio also plays in the gallery reader for saved stories, using the same keyword matching on the displayed scene's content.
- What happens when audio files fail to load? The scene displays normally without audio — no error messages, no broken UI. Audio is a non-essential enhancement.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST automatically play an ambient audio clip when a scene loads, if the scene content matches a known keyword category.
- **FR-002**: System MUST include at least 5 ambient audio categories: forest, ocean, dragon/fire, magic/sparkle, and space/sci-fi.
- **FR-003**: Each audio category MUST map to a set of keywords used to match against scene content (case-insensitive).
- **FR-004**: System MUST loop ambient audio continuously while the user is on the scene.
- **FR-005**: System MUST NOT play audio when no keywords match — silence is the default.
- **FR-006**: System MUST display a visible mute/unmute toggle on scenes where audio could play.
- **FR-007**: The mute preference MUST persist across scene navigation within the same story session.
- **FR-008**: System MUST stop the current audio and start the new audio when navigating between scenes with different ambient categories.
- **FR-009**: System MUST work on both Kids and NSFW tiers with identical behavior.
- **FR-010**: System MUST default to muted when bedtime mode is active.
- **FR-011**: System MUST play ambient audio in the gallery reader when viewing saved story scenes.
- **FR-012**: System MUST gracefully handle browsers that block autoplay by showing the mute toggle in a "muted" state.

### Key Entities

- **Ambient Category**: A named grouping (e.g., "forest", "ocean") with a list of trigger keywords and an associated audio file. The system ships with a fixed set of categories and their audio clips.

### Assumptions

- Audio clips are bundled as static files shipped with the application — no external audio APIs or CDN dependencies.
- Audio clips are short (5-30 second) loops, kept small in file size for fast loading.
- The keyword matching is simple substring matching on scene content text — no AI or NLP required.
- A fixed set of 5-8 ambient categories is sufficient for the initial release.
- Volume is set at a low, unobtrusive level — no volume slider is needed for the initial release.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Ambient audio plays automatically on at least 60% of story scenes (assuming typical adventure content contains matching keywords).
- **SC-002**: Users can mute and unmute audio within one click, with the preference persisting across all subsequent scenes.
- **SC-003**: Audio transitions between scenes are seamless — no overlapping audio, no gaps longer than the page load time.
- **SC-004**: The feature works identically on both Kids and NSFW tiers with zero tier-specific code paths.
