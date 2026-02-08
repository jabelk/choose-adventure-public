# Implementation Plan: Picture Book Mode

**Branch**: `020-picture-book-mode` | **Date**: 2026-02-07 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/020-picture-book-mode/spec.md`

## Summary

Add picture book mode for toddler/young-child protagonist ages that generates 3 images per scene (1 main + 2 extra variations: character close-up and environment wide shot). Extra images use the fastest available image model (gpt-image-1-mini) regardless of the user's main image model selection. Each image has independent loading, polling, retry, and gallery persistence.

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**: FastAPI, Jinja2, Pydantic, anthropic SDK, openai SDK
**Storage**: JSON flat files in `data/stories/`, images in `static/images/`
**Testing**: pytest with httpx AsyncClient
**Target Platform**: Linux (Intel NUC) + macOS (dev laptop), served via Docker/Caddy
**Project Type**: Web application (server-rendered with async JS polling)
**Performance Goals**: Extra images appear within 30 seconds; no image blocks another
**Constraints**: LAN-only serving; external APIs for generation only
**Scale/Scope**: Single-user personal app, ~1-5 concurrent story sessions

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Content Isolation | PASS | Picture book mode only activates in kids tier for toddler/young-child ages. No cross-tier access. |
| II. Local-First | PASS | Extra images stored locally in static/images/. External APIs used only for generation. |
| III. Iterative Simplicity | PASS | Extends existing image generation — no new abstractions. Extra images use same ImageService. |
| IV. Archival by Design | PASS | Extra images persisted in gallery JSON and browsable in reader view. |
| V. Fun Over Perfection | PASS | Straightforward extension of existing patterns. No over-engineering. |

**Gate Result**: PASS — no violations.

## Project Structure

### Documentation (this feature)

```text
specs/020-picture-book-mode/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output
│   └── api.md
└── tasks.md             # Phase 2 output (/speckit.tasks)
```

### Source Code (files modified/created)

```text
app/
├── models.py            # Add extra_images to Image/Scene, extra_image_urls to SavedScene
├── routes.py            # Extra image generation kickoff, new polling/retry endpoints
├── story_options.py     # Add is_picture_book_age() helper
├── services/
│   ├── image.py         # generate_extra_images() method, varied prompt generation
│   └── gallery.py       # Persist extra images in SavedScene

templates/
├── scene.html           # Multi-image vertical layout with per-image loading/retry
└── reader.html          # Display extra images in gallery reader

static/
├── js/app.js            # Multi-image polling logic
└── css/style.css        # Picture book image layout styles

tests/
└── test_all_options.py  # Picture book mode tests
```

**Structure Decision**: Extends existing single-project structure. No new directories needed. All changes are additions to existing files.

## Technical Approach

### Model Changes

The current `Scene` model has a single `image: Image` field. Rather than changing this (which would break backward compatibility), add a new `extra_images: list[Image]` field to Scene. This preserves the main image flow entirely and adds the extra images alongside.

- `Scene.extra_images: list[Image] = []` — list of extra Image objects
- `SavedScene.extra_image_urls: list[str] = []` — persisted extra image URLs
- `SavedScene.extra_image_prompts: list[str] = []` — persisted extra image prompts

### Image Generation

Extra image prompts are derived from the main scene's `image_prompt` by appending variation instructions:
- Close-up: `"{main_prompt}. Close-up portrait shot of the main character, showing facial expression and details."`
- Wide shot: `"{main_prompt}. Wide establishing shot showing the full environment and setting."`

Extra images always use the fastest available model (gpt-image-1-mini if configured, else fall back to user's selected model). Generated as separate async tasks that run in parallel with the main image.

### File Naming

- Main image: `static/images/{scene_id}.png` (unchanged)
- Extra images: `static/images/{scene_id}_extra_0.png`, `static/images/{scene_id}_extra_1.png`

### Polling

Extend the existing `GET /story/image/{scene_id}` endpoint to return extra image statuses alongside the main image. The frontend polls the same endpoint but processes both main and extra image data. Each image slot updates independently.

### Activation Logic

Picture book mode activates when:
1. Tier is "kids" AND
2. `protagonist_age` is "toddler" or "young-child"

This is checked via a simple helper: `is_picture_book_age(protagonist_age: str) -> bool`

## Complexity Tracking

No constitution violations — this section is intentionally empty.
