# Tasks: Core Story Engine

**Input**: Design documents from `/specs/001-core-story-engine/`
**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, contracts/routes.md

**Tests**: Not explicitly requested in spec. Tests omitted per Principle V (Fun Over Perfection).

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Single project**: `app/`, `templates/`, `static/` at repository root

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization, directory structure, and dependency installation

- [x] T001 Create project directory structure per plan.md: `app/`, `app/services/`, `templates/`, `static/css/`, `static/js/`, `static/images/`
- [x] T002 Create `requirements.txt` with dependencies: fastapi, uvicorn[standard], jinja2, anthropic, openai, python-dotenv, python-multipart
- [x] T003 [P] Create `.env.example` with placeholder API keys: ANTHROPIC_API_KEY, OPENAI_API_KEY
- [x] T004 [P] Create `app/__init__.py` (empty package init)
- [x] T005 [P] Create `app/services/__init__.py` (empty package init)

**Checkpoint**: Project skeleton exists, `pip install -r requirements.txt` succeeds in a fresh venv.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T006 Implement `app/config.py` — Pydantic `Settings` class loading ANTHROPIC_API_KEY and OPENAI_API_KEY from environment variables via python-dotenv. Include defaults for host (0.0.0.0), port (8000). Validate keys are non-empty on startup.
- [x] T007 Implement all Pydantic models in `app/models.py` per data-model.md: ImageStatus enum, StoryLength enum, Image, Choice, Scene, Story, StorySession. Include validation constraints (2-4 choices for non-terminal scenes, depth >= 0). Include helper methods on StorySession: `current_scene`, `navigate_forward()`, `navigate_backward()`, `get_full_context()`.
- [x] T008 Implement `app/session.py` — In-memory session store: a dict mapping session_id (UUID string) to StorySession. Functions: `create_session()` returns new session_id + cookie, `get_session(session_id)` returns StorySession or None, `update_session(session_id, story_session)` saves state. Use UUID4 for session IDs.
- [x] T009 Implement `app/main.py` — Create FastAPI app instance. Mount `StaticFiles` on `/static` pointing to `static/` directory. Configure `Jinja2Templates` pointing to `templates/` directory. Load settings from `app/config.py`. Ensure `static/images/` directory exists on startup. Include CORS middleware if needed for local dev.
- [x] T010 Create `templates/base.html` — Base Jinja2 layout with HTML5 doctype, meta viewport, link to `static/css/style.css`, script tag for `static/js/app.js`, content block for child templates. Simple, clean design suitable for reading stories.
- [x] T011 [P] Create `static/css/style.css` — Basic styling: centered content container (max-width ~800px), readable typography for story text, styled choice buttons (large, clickable, hover states), image display area, loading spinner animation, responsive for mobile browsers on LAN.
- [x] T012 [P] Create `static/js/app.js` — Minimal JavaScript: `pollImageStatus(sceneId)` function that polls `GET /story/image/{scene_id}` every 2 seconds, swaps placeholder with actual image when status is "complete", stops polling on "complete" or "failed". Show/hide loading spinner.

**Checkpoint**: Foundation ready — FastAPI app starts with `uvicorn app.main:app --reload`, serves home page template, session management works, static files served. User story implementation can now begin.

---

## Phase 3: User Story 1 — Play a Branching Story (Priority: P1) 🎯 MVP

**Goal**: User enters a prompt, selects story length, plays through an on-demand branching story with text scenes and clickable choices, can navigate backward, reaches an ending.

**Independent Test**: Start the app, enter "A knight discovers a hidden cave", select Medium length, verify first scene appears with text and choices. Click through choices to reach an ending. Use "Go Back" to try a different branch. Start a new story from the ending screen.

### Implementation for User Story 1

- [x] T013 [US1] Implement `app/services/story.py` — StoryService class with AsyncAnthropic client. Methods: `generate_scene(prompt, story_length, context_scenes, current_depth, target_depth)` that calls Claude API with a system prompt instructing it to generate a JSON response containing: scene title, narrative text, image_prompt (description for image generation), is_ending boolean, and 2-4 choices (each with text). System prompt must include: narrative consistency instructions, story length pacing (write toward ending as depth approaches target), choice count constraints (2-4), and JSON output format. Include `build_context(path_scenes)` method that assembles the full conversation history from prior scenes and choices taken. Include `summarize_context(scenes)` method that calls Claude to produce a narrative summary when context exceeds a configurable token threshold (default 50000 chars as rough proxy). Include auto-retry logic: retry up to 3 times on API failure with exponential backoff. Parse and validate the JSON response, ensuring choices count is within 2-4 range.
- [x] T014 [US1] Implement `app/services/image.py` — ImageService class with AsyncOpenAI client. Methods: `generate_image(image_prompt, scene_id)` that calls OpenAI gpt-image-1 API with the image prompt, saves the returned image data to `static/images/{scene_id}.png`, returns the local URL path. Handle failures gracefully: catch exceptions, set image status to FAILED, log the error. Run image generation as a background task (asyncio.create_task) so scene text displays immediately without waiting for the image.
- [x] T015 [US1] Create `templates/home.html` extending `base.html` — Prompt input form with: textarea for story prompt (placeholder text with example prompts), radio buttons or styled selector for story length (Short / Medium / Long with descriptions), submit button ("Start Adventure"). Form POSTs to `/story/start`. Display flash error message if present (for empty prompt validation). Clean, inviting design.
- [x] T016 [US1] Create `templates/scene.html` extending `base.html` — Scene display page with: story title, scene narrative text (rendered with line breaks preserved), image area (shows image if loaded, or loading placeholder with spinner + "Generating image..." text if pending/generating, or fallback placeholder if failed), choice buttons (2-4 styled buttons, each POSTs to `/story/choose/{scene_id}/{choice_id}`), "Go Back" button (POSTs to `/story/back`). If `is_ending` is true: show "The End" header, hide choice buttons, show "Start New Story" link (to `/`) and "Go Back" button. Show story progress indicator (e.g., "Chapter {depth + 1}"). Include JS call to `pollImageStatus(sceneId)` if image status is not "complete".
- [x] T017 [US1] Create `templates/error.html` extending `base.html` — Error display page with: error message text, "Try Again" button (re-submits the last action), "Start Over" link (to `/`). Used when Claude API fails after all retries.
- [x] T018 [US1] Implement all route handlers in `app/routes.py` per contracts/routes.md:
  - `GET /` — Render `home.html`. Pass any flash error message from session.
  - `POST /story/start` — Validate prompt non-empty (redirect to `/` with error if empty). Create Story with UUID, user prompt, selected length, target_depth from length enum. Call `StoryService.generate_scene()` for root scene (depth=0). Create Scene from response with UUID. Kick off `ImageService.generate_image()` as background task. Create StorySession, store in session via `session.py`. Redirect to `/story/scene/{root_scene_id}`.
  - `GET /story/scene/{scene_id}` — Load StorySession from session. Look up scene by ID. If not found or no session, redirect to `/`. Render `scene.html` with scene data.
  - `POST /story/choose/{scene_id}/{choice_id}` — Load StorySession. Find the choice. If `next_scene_id` already exists (revisiting), just navigate there and update path_history. Otherwise: build context from full path, summarize if needed, call `StoryService.generate_scene()`, create new Scene, kick off image generation, add to StorySession, update path_history. On Claude API failure after retries, render `error.html` with retry button. Redirect to `/story/scene/{new_scene_id}`.
  - `POST /story/back` — Load StorySession. Call `navigate_backward()`. If path_history empty, redirect to `/`. Otherwise redirect to `/story/scene/{previous_id}`.
  - `GET /story/image/{scene_id}` — Load StorySession. Return JSON with image status and URL if complete.
  - Register all routes with the FastAPI app in `app/main.py`.

**Checkpoint**: At this point, the full story play loop works: enter prompt → select length → read scene → click choice → new scene generates → navigate back → reach ending → start new story. Images may show as placeholders if OpenAI API key is not configured, but the text story flow is complete. This is the MVP.

---

## Phase 4: User Story 2 — Generate Story from Custom Prompt (Priority: P2)

**Goal**: Story generation accurately reflects the user's prompt — theme, tone, setting, and characters match what was requested. Short prompts still produce coherent stories. Empty prompts are rejected with a helpful message.

**Independent Test**: Enter "A detective investigates a haunted mansion" → verify detective/mystery themes in text. Enter "space pirates" → verify sci-fi pirate themes. Submit empty prompt → verify error message appears.

**Note**: US1 already implements the basic prompt flow. US2 focuses on **prompt engineering quality** and **input validation UX**.

### Implementation for User Story 2

- [x] T019 [US2] Enhance system prompt in `app/services/story.py` — Update the Claude system prompt to: explicitly instruct the AI to closely follow the user's prompt theme, tone, and setting throughout all scenes; generate character names and settings consistent with the prompt genre; maintain narrative voice matching the genre (e.g., noir for detective, whimsical for fantasy); include the user's original prompt as a grounding reference in every generation call; generate an image_prompt that captures the visual style matching the genre (e.g., "dark noir illustration" for detective stories, "colorful fantasy art" for fantasy).
- [x] T020 [US2] Enhance prompt validation UX in `app/routes.py` and `templates/home.html` — Add client-side validation (HTML required attribute, minlength). Improve server-side empty prompt error message to be friendly and helpful: "Please describe your adventure! Try something like 'A detective investigates a haunted mansion' or even just 'space pirates'." Display example prompts as clickable suggestions on the home page that pre-fill the textarea.

**Checkpoint**: Stories feel personalized to the prompt. Short prompts like "space pirates" produce coherent themed stories. Empty prompts show a helpful message with examples.

---

## Phase 5: User Story 3 — View AI-Generated Images for Each Scene (Priority: P3)

**Goal**: Every scene displays an AI-generated image that visually represents the narrative content. Images load asynchronously without blocking story text. Failed images degrade gracefully.

**Independent Test**: Play through a story with valid OpenAI API key → verify every scene gets a unique image matching the narrative. Disconnect internet mid-story → verify text still appears, image shows graceful fallback. Check that images are saved to `static/images/`.

**Note**: US1 already implements the basic image generation and async loading infrastructure. US3 focuses on **image quality, visual consistency, and graceful degradation**.

### Implementation for User Story 3

- [x] T021 [US3] Enhance image prompt generation in `app/services/story.py` — Update the Claude system prompt to generate more detailed, visually descriptive image_prompt fields. Image prompts should: describe the scene composition, lighting, and mood; include consistent character descriptions across scenes (e.g., "a tall knight with red armor" should persist); specify an art style consistent with the story genre; avoid text in images (DALL-E struggles with text).
- [x] T022 [US3] Enhance image generation in `app/services/image.py` — Add retry logic for image generation (up to 2 retries on failure). Add proper error logging with the failed prompt for debugging. Ensure image status transitions are atomic: PENDING → GENERATING → COMPLETE/FAILED. Handle rate limiting from OpenAI API with appropriate backoff. Verify saved image files are valid (non-zero size).
- [x] T023 [US3] Enhance image display UX in `templates/scene.html` and `static/js/app.js` — Improve loading placeholder: show an attractive animated skeleton/shimmer placeholder sized to the expected image dimensions. On failure: show a styled fallback (e.g., subtle gradient with the story title, not a broken image icon). Add smooth fade-in transition when image loads via JS. Ensure image is responsive and looks good on different screen sizes.
- [x] T024 [US3] Enhance image polling in `static/js/app.js` — Add timeout to polling (stop after 60 seconds and show fallback). Add visual feedback during polling (pulsing animation on placeholder). Handle network errors in polling gracefully (don't crash, just show fallback).

**Checkpoint**: Every scene shows an image that matches the narrative. Images load smoothly with attractive placeholders. Failed images show a tasteful fallback. The visual experience is polished.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [x] T025 [P] Validate quickstart.md — Follow the quickstart steps in `specs/001-core-story-engine/quickstart.md` from scratch in a fresh venv: clone, install, configure .env, run, play a story end-to-end. Fix any issues found.
- [x] T026 [P] Add favicon and page titles — Add a simple favicon to `static/` and reference in `templates/base.html`. Set dynamic page titles (story title on scene pages, "Choose Your Own Adventure" on home).
- [x] T027 Code cleanup — Review all files for: unused imports, inconsistent naming, missing error handling edge cases, hardcoded values that should be in config. Keep it light per Principle V.
- [x] T028 Manual end-to-end test — Play through 3 complete stories with different prompts and lengths (short fantasy, medium mystery, long sci-fi). Verify: narrative coherence, image relevance, back navigation, ending detection, error recovery. Note any issues for follow-up.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — can start immediately
- **Foundational (Phase 2)**: Depends on Phase 1 completion — BLOCKS all user stories
- **US1 (Phase 3)**: Depends on Phase 2 completion — this is the MVP
- **US2 (Phase 4)**: Depends on Phase 3 (US1) completion — enhances prompt handling built in US1
- **US3 (Phase 5)**: Depends on Phase 3 (US1) completion — enhances image handling built in US1
- **Polish (Phase 6)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Phase 2. No dependencies on other stories. **This is the MVP.**
- **User Story 2 (P2)**: Depends on US1 (enhances prompt engineering and validation built in US1). Cannot run in parallel with US1.
- **User Story 3 (P3)**: Depends on US1 (enhances image pipeline built in US1). Can run in parallel with US2 (different files: story.py prompt vs image.py + templates).

### Within Each Phase

- Models (T007) before services (T013, T014)
- Services before routes (T018)
- Templates (T015-T017) can be built in parallel with services
- Routes depend on both services and templates being ready

### Parallel Opportunities

- **Phase 1**: T003, T004, T005 can all run in parallel
- **Phase 2**: T011, T012 can run in parallel (CSS and JS are independent files)
- **Phase 3**: T013 and T014 can be developed in parallel (different service files). T015, T016, T017 can be developed in parallel (different template files). T018 depends on all of T013-T017.
- **Phase 4 & 5**: US2 and US3 can run in parallel after US1 is complete (different files)
- **Phase 6**: T025 and T026 can run in parallel

---

## Parallel Example: Phase 2 (Foundational)

```bash
# These can run in parallel (different files):
Task: "Create static/css/style.css"
Task: "Create static/js/app.js"

# These are sequential (dependencies):
Task: "Implement app/config.py"       # First: settings
Task: "Implement app/models.py"       # Second: models use config
Task: "Implement app/session.py"      # Third: sessions use models
Task: "Implement app/main.py"         # Fourth: app ties it all together
```

## Parallel Example: Phase 3 (User Story 1)

```bash
# Services can run in parallel (different files):
Task: "Implement app/services/story.py"
Task: "Implement app/services/image.py"

# Templates can run in parallel (different files):
Task: "Create templates/home.html"
Task: "Create templates/scene.html"
Task: "Create templates/error.html"

# Routes depend on both services and templates:
Task: "Implement app/routes.py"  # AFTER services + templates
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (~5 min)
2. Complete Phase 2: Foundational (~30 min)
3. Complete Phase 3: User Story 1 (~2-3 hours)
4. **STOP and VALIDATE**: Enter a prompt, play through a full story, test back navigation, reach an ending
5. You now have a working choose-your-own-adventure app!

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → **MVP is playable!**
3. Add User Story 2 → Test prompt quality → Stories feel more personalized
4. Add User Story 3 → Test image quality → Visual experience is polished
5. Polish → Final cleanup and validation

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Commit after each task or logical group (per CLAUDE.md branching strategy)
- Stop at any checkpoint to validate story independently
- No tests were generated (not requested in spec, per Principle V — Fun Over Perfection)
- US2 and US3 enhance infrastructure built in US1; they modify existing files rather than creating new ones
