# Tasks: Sound Effects / Ambiance

**Input**: Design documents from `/specs/032-sound-effects-ambiance/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md

**Tests**: Included — test tasks verify mute toggle visibility and data attributes in templates.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Create placeholder audio files and the static/audio/ directory

- [X] T001 Create placeholder MP3 audio files in static/audio/ for all 7 categories (forest.mp3, ocean.mp3, dragon.mp3, magic.mp3, space.mp3, city.mp3, storm.mp3)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core CSS and JS module that all user stories depend on

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T002 [P] Add mute toggle button CSS styles (.ambiance-toggle, speaker icon states) in static/css/style.css
- [X] T003 [P] Create ambient audio JS module with initAmbiance(), keyword matching, Audio element management, mute toggle, and localStorage persistence in static/js/ambiance.js

**Checkpoint**: Foundation ready — template integration can now begin

---

## Phase 3: User Story 1 - Ambient Audio on Scene Load (Priority: P1) 🎯 MVP

**Goal**: Auto-play ambient audio on scene load based on keyword matching against scene content

**Independent Test**: Navigate to a scene containing "forest" or "ocean" keywords and verify ambient audio plays automatically

### Implementation for User Story 1

- [X] T004 [US1] Add mute toggle button, scene content data attribute, and ambiance.js script include + initialization to templates/scene.html

**Checkpoint**: Active story scenes now play ambient audio based on content keywords

---

## Phase 4: User Story 2 - Mute Toggle (Priority: P2)

**Goal**: Mute toggle persists preference via localStorage; bedtime mode defaults to muted

**Independent Test**: Click mute toggle, verify audio stops, navigate to next scene, verify audio stays muted, click unmute, verify audio resumes

### Implementation for User Story 2

> Mute toggle functionality is built into ambiance.js (T003) and the template button (T004). This phase validates it works end-to-end.

- [X] T005 [US2] Verify mute toggle integration works in scene.html — toggle button changes icon state and localStorage key persists across navigations (manual verification step, no code changes needed)

**Checkpoint**: Mute toggle works on active story scenes with localStorage persistence

---

## Phase 5: User Story 3 - Both Tiers + Gallery Reader (Priority: P3)

**Goal**: Ambient audio works identically on both Kids and NSFW tiers, including the gallery reader

**Independent Test**: Start a Kids tier story and an NSFW tier story with similar content, verify both play audio; open a saved story in the gallery reader and verify audio plays

### Implementation for User Story 3

- [X] T006 [US3] Add mute toggle button, scene content data attribute, and ambiance.js script include + initialization to templates/reader.html

**Checkpoint**: Both tiers and the gallery reader support ambient audio

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Tests and validation

- [X] T007 Create tests for ambiance feature (mute toggle visibility, data attributes, script inclusion) in tests/test_ambiance.py

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — create audio files first
- **Foundational (Phase 2)**: Depends on Phase 1 — CSS and JS need audio files to exist
- **US1 (Phase 3)**: Depends on Phase 2 — needs ambiance.js and CSS
- **US2 (Phase 4)**: Depends on Phase 3 — mute toggle is part of scene.html integration
- **US3 (Phase 5)**: Depends on Phase 2 — needs ambiance.js and CSS (can parallel with US1)
- **Polish (Phase 6)**: Depends on all user stories being complete

### Parallel Opportunities

- T002 and T003 can run in parallel (different files)
- T004 and T006 can run in parallel (different template files) after Phase 2

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Create placeholder audio files
2. Complete Phase 2: CSS + JS module
3. Complete Phase 3: scene.html integration
4. **STOP and VALIDATE**: Test ambient audio on active story scenes

### Incremental Delivery

1. Setup + Foundational → Audio infrastructure ready
2. Add US1 (scene.html) → Test ambient audio on active scenes (MVP!)
3. Add US2 → Verify mute persistence works
4. Add US3 (reader.html) → Test gallery reader + both tiers
5. Polish → Add automated tests

---

## Notes

- This is a purely client-side feature — no new server routes needed
- Audio files are placeholders (silent/tone) — real clips can be swapped in later
- The JS module handles all complexity: keyword matching, Audio API, localStorage, autoplay rejection
- Both templates use the same JS module with the same initialization pattern
