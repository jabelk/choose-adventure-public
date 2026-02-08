# Route Contracts: Core Story Engine

**Feature Branch**: `001-core-story-engine`
**Date**: 2026-02-07

All routes serve HTML via Jinja2 templates (server-side rendered). No separate REST API for v1.

## Pages

### GET /

**Purpose**: Home page with prompt input form.

**Response**: HTML page with:
- Text input for story prompt
- Story length selector (short / medium / long)
- Submit button

**Template**: `home.html`

---

### POST /story/start

**Purpose**: Accept prompt and length, generate the first scene, start a new story session.

**Request** (form data):
- `prompt` (string, required, non-empty)
- `length` (string, required, one of: "short", "medium", "long")

**Behavior**:
1. Validate prompt is non-empty (redirect to `/` with error message if invalid)
2. Create new StorySession with Story metadata
3. Call Claude API to generate root scene (text + choices + image prompt)
4. Call OpenAI API to generate image (async, non-blocking — scene displays with placeholder if slow)
5. Store StorySession in server-side session
6. Redirect to `GET /story/scene/{scene_id}`

**Error handling**:
- Empty prompt → redirect to `/` with flash message
- Claude API failure → auto-retry 3x, then show error page with retry button

---

### GET /story/scene/{scene_id}

**Purpose**: Display a story scene with text, image, and choices.

**Path params**:
- `scene_id` (string, required)

**Response**: HTML page with:
- Scene narrative text
- AI-generated image (or loading placeholder if still generating)
- 2-4 clickable choice buttons (if not an ending)
- "The End" indicator + "New Story" / "Go Back" buttons (if ending)
- "Go Back" navigation link
- Current depth / story length indicator

**Template**: `scene.html`

**Error handling**:
- Invalid scene_id or no active session → redirect to `/`
- Scene not in session → redirect to `/`

---

### POST /story/choose/{scene_id}/{choice_id}

**Purpose**: User selects a choice, generate the next scene.

**Path params**:
- `scene_id` (string, required) — current scene
- `choice_id` (string, required) — selected choice

**Behavior**:
1. Load StorySession from server session
2. Validate scene_id and choice_id exist
3. If choice already has a `next_scene_id` (previously explored), navigate there
4. Otherwise:
   a. Build context: full path of prior scenes + choices
   b. If context exceeds token threshold, summarize earlier scenes
   c. Call Claude API to generate next scene
   d. Call OpenAI API to generate image (async)
   e. Add new scene to StorySession.scenes
   f. Update path_history
5. Redirect to `GET /story/scene/{new_scene_id}`

**Error handling**:
- Invalid IDs → redirect to current scene with error
- Claude API failure → auto-retry 3x, show error with retry button, preserve state

---

### POST /story/back

**Purpose**: Navigate backward to the previous choice point.

**Behavior**:
1. Pop last entry from path_history
2. If path_history is now empty, redirect to `/`
3. Otherwise redirect to `GET /story/scene/{previous_scene_id}`

---

### GET /story/image/{scene_id}

**Purpose**: Check image generation status / serve image. Used for async image loading.

**Path params**:
- `scene_id` (string, required)

**Response**:
- If image status is `complete`: JSON `{"status": "complete", "url": "/static/images/{filename}"}`
- If image status is `generating` or `pending`: JSON `{"status": "generating"}`
- If image status is `failed`: JSON `{"status": "failed"}`

**Note**: This is the one JSON endpoint — used by minimal client-side JS to poll for image readiness and swap the placeholder.

---

## Static Files

### GET /static/css/*
### GET /static/js/*
### GET /static/images/*

Served by FastAPI `StaticFiles` mount. Generated images saved to `static/images/` with UUID filenames.
