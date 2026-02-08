# Tasks: Read Aloud / TTS Narration

**Input**: Design documents from `/specs/022-read-aloud-tts/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Included — the project has an existing test suite in `tests/test_all_options.py`.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

---

## Phase 1: Setup

**Purpose**: Create new files and extend existing data model for TTS support

- [X] T001 Add TTS fields to TierConfig dataclass (`tts_default_voice`, `tts_autoplay_default`, `tts_voices`) and set values for kids and nsfw tiers in `app/tiers.py`
- [X] T002 Create TTS service with `generate_speech(text, voice, instructions)` function that calls OpenAI `gpt-4o-mini-tts` API and returns MP3 bytes, including sentence-boundary text chunking for texts over 4000 chars, in `app/services/tts.py`

**Checkpoint**: TTS service ready, tier config extended — story implementation can begin

---

## Phase 2: User Story 1 — Play Button Reads Scene Aloud (Priority: P1) MVP

**Goal**: A play/stop button on every scene page (active + gallery) that reads the scene's narrative text aloud using OpenAI TTS.

**Independent Test**: Navigate to any story scene, tap the play button, verify the scene text is read aloud. Tap again to stop.

### Implementation for User Story 1

- [X] T003 [US1] Add TTS audio endpoint `GET /{prefix}/story/tts/{scene_id}` to `app/routes.py` — looks up scene content from session, calls TTS service, returns MP3 as `audio/mpeg` Response. Include `tts_available` bool (checks `settings.openai_api_key`) in scene template context.
- [X] T004 [US1] Add gallery TTS endpoint `GET /{prefix}/gallery/tts/{story_id}/{scene_id}` to `app/routes.py` — loads saved story from gallery JSON, finds scene content, calls TTS service, returns MP3.
- [X] T005 [US1] Create `static/js/tts-player.js` with TTS playback controller: `initTTSPlayer(sceneId, urlPrefix)` function that manages play/stop button state (idle/loading/playing), fetches audio from TTS endpoint, uses HTML5 Audio API for playback, stops audio on navigation (beforeunload), debounces rapid taps.
- [X] T006 [US1] Add play/stop button HTML to `templates/scene.html` — place a large speaker button below the scene text (inside `{% if tts_available %}` conditional), include `<script src="/static/js/tts-player.js">` and call `initTTSPlayer()` in the scripts block. Pass `scene.scene_id` and `url_prefix`.
- [X] T007 [US1] Add play/stop button HTML to `templates/reader.html` — same play button pattern as scene.html but use gallery TTS URL (`/{prefix}/gallery/tts/{story_id}/{scene_id}`), inside `{% if tts_available %}` conditional.
- [X] T008 [P] [US1] Add TTS button and player CSS styles to `static/css/style.css` — `.tts-controls` container, `.tts-play-btn` (large, mobile-friendly, 56px+ tap target for toddler), loading spinner state, playing state with stop icon. Kids theme: colorful/playful button. NSFW theme: subtle/dark button.

**Checkpoint**: Play button visible on all scene pages, tapping it reads the scene aloud, tapping again stops it.

---

## Phase 3: User Story 2 — Auto-Play on Kids Tier (Priority: P2)

**Goal**: Narration auto-plays when a new scene loads on the kids tier. Toggle to disable. Off by default on NSFW.

**Independent Test**: Start a story on kids tier, verify narration begins automatically. Toggle off, verify it stops auto-playing.

### Implementation for User Story 2

- [X] T009 [US2] Add auto-play data attribute to scene template — render `data-tts-autoplay="{{ tts_autoplay }}"` on the TTS controls container in `templates/scene.html`, where `tts_autoplay` is passed from route context (from session cookie or tier default).
- [X] T010 [US2] Add auto-play toggle button to TTS controls in `templates/scene.html` — small toggle switch next to play button, labeled "Auto" with on/off state.
- [X] T011 [US2] Extend `initTTSPlayer()` in `static/js/tts-player.js` to check `data-tts-autoplay` on DOMContentLoaded and auto-trigger playback if `"true"`. Add toggle button handler that POSTs to preferences endpoint to update auto-play state.
- [X] T012 [US2] Add `POST /{prefix}/tts/preferences` endpoint to `app/routes.py` — accepts JSON body with optional `voice` and `autoplay` fields, updates session cookie, returns `{"status": "ok"}`. Add `tts_autoplay` to scene template context (read from session cookie, fallback to `tier_config.tts_autoplay_default`).
- [X] T013 [P] [US2] Add auto-play toggle CSS to `static/css/style.css` — `.tts-autoplay-toggle` switch styling, on/off visual states, compact size.

**Checkpoint**: Kids tier auto-plays narration on scene load. Toggle works to disable. NSFW does not auto-play.

---

## Phase 4: User Story 3 — Voice Selection (Priority: P3)

**Goal**: User can choose from 4 voices per tier. Preference persists across scenes within a session.

**Independent Test**: Open voice selector, pick a different voice, play a scene, verify the new voice is used. Navigate away and back — verify preference persisted.

### Implementation for User Story 3

- [X] T014 [US3] Add voice selector dropdown to TTS controls in `templates/scene.html` and `templates/reader.html` — `<select>` element populated with tier-specific voices (passed as `tts_voices` in template context). Show current voice as selected.
- [X] T015 [US3] Add `GET /{prefix}/tts/voices` endpoint to `app/routes.py` — returns JSON with available voices for the tier, current selection, and auto-play state.
- [X] T016 [US3] Update `initTTSPlayer()` in `static/js/tts-player.js` to read selected voice from dropdown and pass as `?voice=` query param when fetching TTS audio. On voice change, POST to preferences endpoint to persist. Also update the auto-play toggle handler (from T011) to use the same preferences endpoint.
- [X] T017 [US3] Pass `tts_voices` (from `tier_config.tts_voices`) and `tts_current_voice` (from session cookie, fallback to `tier_config.tts_default_voice`) to scene and reader template context in `app/routes.py`.
- [X] T018 [P] [US3] Add voice selector CSS to `static/css/style.css` — `.tts-voice-select` dropdown styling, compact, fits alongside play button.

**Checkpoint**: Voice selector works on both tiers, preference persists in session, each tier shows its curated voice list.

---

## Phase 5: User Story 4 — Sentence Highlighting During Playback (Priority: P4) Stretch Goal

**Goal**: Currently spoken sentence is highlighted in the scene text as narration plays. Helps the 5-year-old follow along.

**Independent Test**: Play a scene, verify sentences highlight in sync with audio, highlighting clears on stop.

### Implementation for User Story 4

- [X] T019 [US4] Wrap scene text paragraphs in `<span>` elements with sentence-level markup in `templates/scene.html` and `templates/reader.html` — use a Jinja2 filter or inline logic to split `scene.content` into sentences and wrap each in `<span class="tts-sentence" data-index="N">`.
- [X] T020 [US4] Add sentence highlighting logic to `static/js/tts-player.js` — calculate estimated duration per sentence (~150 WPM), use `setInterval` to advance highlight class `.tts-highlight` through sentences in sync with audio `currentTime`. Clear highlighting on stop/pause/end. Auto-scroll highlighted sentence into view on mobile.
- [X] T021 [P] [US4] Add highlighting CSS to `static/css/style.css` — `.tts-sentence.tts-highlight` background color (warm yellow for kids, subtle blue for NSFW), smooth transition, `.tts-sentence` base styles.

**Checkpoint**: Sentences highlight as narration plays, highlighting clears on stop, auto-scrolls on mobile.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Tests, edge cases, and cleanup

- [X] T022 Add TTS tests to `tests/test_all_options.py` — test TTS endpoint returns 404 when no active story, test TTS endpoint with mocked OpenAI returns MP3 content-type, test `tts_available` is True/False based on API key, test voice preferences persist in session, test auto-play defaults per tier, test gallery TTS endpoint, test kids tier shows kids voices and NSFW shows NSFW voices.
- [X] T023 Run full test suite (`venv/bin/python -m pytest tests/ -v`) and verify all tests pass including new TTS tests.
- [X] T024 Add error handling for TTS failures in `static/js/tts-player.js` — show brief error toast on fetch failure, return button to idle state, allow retry. Handle network errors and 502 responses gracefully.
- [X] T025 Verify navigation stops audio — test that clicking a choice button, clicking Home link, or using browser back while audio is playing stops playback cleanly (no overlapping audio on the new page).

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — can start immediately
- **US1 (Phase 2)**: Depends on Setup (T001, T002)
- **US2 (Phase 3)**: Depends on US1 (builds on play button and TTS controls)
- **US3 (Phase 4)**: Depends on US1 (adds voice param to existing TTS fetch)
- **US4 (Phase 5)**: Depends on US1 (extends the player JS and scene template)
- **Polish (Phase 6)**: Depends on all user stories being complete

### User Story Dependencies

- **US1 (P1)**: Can start after Setup — no dependencies on other stories
- **US2 (P2)**: Depends on US1 — adds auto-play to the play button from US1
- **US3 (P3)**: Depends on US1 — adds voice selection to the TTS fetch from US1
- **US4 (P4)**: Depends on US1 — extends the player and templates from US1

### Within Each User Story

- Route/service changes before template changes
- Template changes before JS changes
- CSS can run in parallel with anything (marked [P])

### Parallel Opportunities

- T001 and T002 can run in parallel (different files)
- T008 (CSS) can run in parallel with T003-T007
- T013 (CSS) can run in parallel with T009-T012
- T018 (CSS) can run in parallel with T014-T017
- T021 (CSS) can run in parallel with T019-T020
- US3 and US4 can run in parallel after US1 is complete (different concerns)

---

## Parallel Example: User Story 1

```bash
# After Setup (T001, T002) is complete:

# Sequential (route before template before JS):
T003 → T004 → T005 → T006 → T007

# Parallel (CSS has no dependencies on routes/templates):
T008 (can run alongside T003-T007)
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001, T002)
2. Complete Phase 2: US1 — Play Button (T003-T008)
3. **STOP and VALIDATE**: Test play button on both tiers + gallery
4. Deploy — the feature is usable with just a play button

### Incremental Delivery

1. Setup + US1 → Play button works → Deploy (MVP!)
2. Add US2 → Auto-play on kids tier → Deploy
3. Add US3 → Voice selection → Deploy
4. Add US4 → Sentence highlighting → Deploy (stretch goal)
5. Polish → Tests + error handling → Deploy

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- US2, US3, US4 all build on US1 but are independently testable increments
- Commit after each phase completion
- The TTS endpoint is synchronous (no polling needed) — simpler than the image generation pattern
- Voice instructions differ per tier: warm/friendly for kids, natural/expressive for NSFW
