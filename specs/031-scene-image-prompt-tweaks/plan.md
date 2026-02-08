# Implementation Plan: Scene Image Prompt Tweaks

**Branch**: `031-scene-image-prompt-tweaks` | **Date**: 2026-02-08 | **Spec**: [spec.md](spec.md)

## Summary

Add an edit icon overlay on scene images that reveals the image prompt in an editable text field. Users can modify the prompt and regenerate the image. For active stories, a new route accepts the updated prompt and triggers regeneration. For gallery reader stories, a similar route updates the saved JSON file. Purely additive — CSS for the edit UI, a JS module for the interaction, two new server routes, and template updates.

## Technical Context

**Language/Version**: Python 3 with FastAPI, Jinja2 templates
**Primary Dependencies**: Vanilla JavaScript (client-side), existing ImageService (server-side)
**Storage**: Existing `static/images/` for images, `data/stories/` for gallery JSON
**Testing**: pytest with FastAPI TestClient

## Constitution Check

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Content Isolation | PASS | Routes inside `create_tier_router()`, tier-scoped. |
| II. Local-First | PASS | Uses existing local image generation service. |
| III. Iterative Simplicity | PASS | Small addition: 1 JS file, CSS, 2 routes, template edits. |
| IV. Archival by Design | PASS | Gallery regeneration persists updated images and prompts to archive. |
| V. Fun Over Perfection | PASS | Quick creative control feature, minimal code. |

## Design

### Active Story Route

New POST route: `/story/image/{scene_id}/regenerate`
- Accepts JSON body: `{ "prompt": "updated prompt text" }`
- Updates `scene.image.prompt` with the new prompt
- Resets image status to PENDING, clears URL
- Calls `image_service.generate_image()` as background task
- Saves progress
- Returns `{ "status": "generating" }`

This is distinct from the existing `/story/image/{scene_id}/retry` which reuses the original prompt.

### Gallery Reader Route

New POST route: `/gallery/{story_id}/{scene_id}/regenerate-image`
- Accepts JSON body: `{ "prompt": "updated prompt text" }`
- Loads the SavedStory from disk
- Updates `saved_scene.image_prompt` with the new prompt
- Generates a new image using `image_service.generate_image()` (awaited, not background — gallery stories don't have live polling)
- Updates `saved_scene.image_url` with the new image path
- Writes updated SavedStory back to disk
- Returns `{ "status": "complete", "image_url": "/static/images/..." }` on success
- Returns `{ "status": "failed", "error": "..." }` on failure

### Client-Side JS Module

New file: `static/js/prompt-edit.js`
- `initPromptEdit(config)` accepting `{ editBtnSelector, imageSelector, prompt, regenerateUrl }`
- Click edit icon → shows textarea with current prompt + Regenerate/Cancel buttons
- Regenerate → POST to regenerateUrl with `{ prompt }` → show loading → replace image src on success
- Cancel → hide editor, restore original state

### Template Changes

**scene.html** (active story): Add edit icon overlay on scene image, pass `scene.image.prompt` as data attribute, include `prompt-edit.js`

**reader.html** (gallery reader): Add edit icon overlay on scene image, pass `scene.image_prompt` as data attribute, include `prompt-edit.js`

### Image File Naming

Regenerated images overwrite the same path: `static/images/{scene_id}.png`. A cache-busting query parameter (`?t=timestamp`) is appended to the image URL in the response to force browser reload.

## Project Structure

### Source Code (repository root)

```text
app/
├── routes.py              # Add 2 new route handlers
├── services/
│   ├── image.py           # No changes (reuse existing generate_image)
│   └── gallery.py         # Add update_scene_image() helper

static/
├── css/style.css          # Add prompt-edit overlay styles
└── js/prompt-edit.js      # New: prompt editing JS module

templates/
├── scene.html             # Add edit icon + data attributes
└── reader.html            # Add edit icon + data attributes

tests/
└── test_prompt_tweaks.py  # New: test edit icon visibility, route responses
```
