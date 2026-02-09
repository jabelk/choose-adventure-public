# Implementation Plan: Cover Art Generator

**Branch**: `045-cover-art-generator` | **Date**: 2026-02-08 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/045-cover-art-generator/spec.md`

## Summary

Add AI-generated book cover images for completed stories in the gallery. When a story is saved to the gallery, an async background task generates a cover-style image using the story's title, prompt, tier styling, and art style. The cover becomes the gallery thumbnail, falling back to the first scene image if generation fails. A regenerate option is available from the gallery detail view.

## Technical Context

**Language/Version**: Python 3.11+ (matches existing project)
**Primary Dependencies**: FastAPI, Jinja2, Pydantic, anthropic SDK, openai SDK, google-genai SDK (all existing — no new dependencies)
**Storage**: JSON flat files in `data/stories/`, images in `static/images/`
**Testing**: pytest (existing test suite)
**Target Platform**: Linux server (NUC) + local dev on macOS
**Project Type**: Web application (FastAPI + Jinja2 templates)
**Performance Goals**: Cover generation must not block gallery save; gallery page load time unchanged
**Constraints**: Cover art generated asynchronously; graceful fallback on failure
**Scale/Scope**: ~50-200 gallery stories per tier

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Content Isolation | PASS | Cover prompts are tier-specific; no cross-tier content |
| II. Local-First | PASS | Images stored locally; AI APIs used for generation only; gallery works without covers |
| III. Iterative Simplicity | PASS | Minimal changes: one new field on SavedStory, one async task, template update |
| IV. Archival by Design | PASS | Cover images stored as local files, URL persisted in story JSON |
| V. Fun Over Perfection | PASS | Simple implementation; no over-engineering |

## Design Decisions

### DD-001: Cover prompt built from story metadata, not scene content
The cover prompt uses the story's title, original prompt (theme/genre), tier styling, and art style. It does NOT read individual scene content. This keeps it fast (no context assembly) and produces a thematic "book cover" rather than a scene illustration.

### DD-002: Async background task after gallery save
Use `asyncio.create_task()` to generate the cover after `gallery_service.save_story()` completes. The cover task writes the image to disk and updates the gallery JSON file. This matches the existing pattern used for scene image generation and chat anchor images.

### DD-003: Cover stored as fields on SavedStory
Add `cover_art_url: Optional[str]` and `cover_art_status: str` to `SavedStory`. The cover generation task updates the JSON file on disk after the image is ready. Default values (`None` and `"none"`) ensure backward compatibility.

### DD-004: Gallery template shows cover or falls back to first scene
The gallery card template checks `story.cover_art_url` first. If present and status is `"complete"`, it shows the cover. Otherwise, it falls back to the existing first-scene-image logic. No polling needed — the cover will appear on next gallery page load.

### DD-005: Title/author text in HTML, not in the AI image
AI image generators are unreliable at rendering text. The cover image is a thematic illustration only. Title and author text are overlaid via CSS in the gallery card HTML. This is more reliable and allows styling per tier.

### DD-006: Regenerate via POST endpoint
A `POST /{tier}/gallery/{story_id}/regenerate-cover` endpoint triggers a new cover generation. It sets status to `"generating"`, kicks off the async task, and redirects back to the gallery detail page.

### DD-007: Cover file naming convention
Cover images are saved as `{story_id}_cover.png` in `static/images/`. This avoids collision with scene images (which use `{scene_id}.png`).

## Project Structure

### Documentation (this feature)

```text
specs/045-cover-art-generator/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
└── tasks.md
```

### Source Code (repository root)

```text
app/
├── models.py              # Add cover_art_url, cover_art_status to SavedStory
├── routes.py              # Add regenerate-cover endpoint, update gallery save flow
└── services/
    ├── gallery.py         # Add generate_cover_art() method, update save_story()
    └── image.py           # (unchanged — reuse existing generate_image)

templates/
├── gallery.html           # Show cover art as thumbnail with CSS text overlay
└── reader.html            # Add "Regenerate Cover" button

static/
├── css/style.css          # Cover art card styling, title/author overlay
└── images/                # Cover art files: {story_id}_cover.png
```

**Structure Decision**: Follows existing project structure. Cover art generation logic lives in `gallery.py` since it's tied to the gallery save flow. Reuses `ImageService.generate_image()` for actual image generation.
