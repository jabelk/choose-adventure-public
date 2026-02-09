# Implementation Plan: Character Visual Consistency

**Branch**: `043-visual-consistency` | **Date**: 2026-02-08 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/043-visual-consistency/spec.md`

## Summary

Maintain consistent character appearance across all scene images in a story by carrying forward reference images (roster character photos + the most recently generated scene image) to every subsequent image generation call. Currently, roster photos are passed to scene 1 but continuation scenes rebuild photo_paths from scratch without including previously generated images. The fix adds a `generated_reference_path` field to `Story` that stores the latest generated scene image path, and a helper function that merges roster photos + generated reference into the reference list (capped at 3) before each `generate_image()` call.

## Technical Context

**Language/Version**: Python 3.11+ (matches existing project)
**Primary Dependencies**: FastAPI, Pydantic, openai SDK, google-genai SDK, httpx (all existing — no new dependencies)
**Storage**: In-memory session (Story model) — no new files on disk
**Testing**: pytest (existing test suite)
**Target Platform**: Linux NUC (Docker) + macOS dev laptop
**Project Type**: Web application (Python backend + Jinja2 templates)
**Performance Goals**: <500ms overhead per scene generation for reference image assembly
**Constraints**: Max 3 reference images per API call (API limits + cost)
**Scale/Scope**: Single-user home server, ~5-7 scenes per story

## Constitution Check

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Content Isolation | PASS | No cross-tier data. Reference images scoped to session. |
| II. Local-First | PASS | All reference images are local files on disk. No new cloud dependencies. |
| III. Iterative Simplicity | PASS | Minimal change — one new field on Story, one helper function, update existing call sites. No new abstractions. |
| IV. Archival by Design | PASS | Generated images already saved to disk. No change to archival. |
| V. Fun Over Perfection | PASS | Simple rolling reference approach. Not overengineering with face embeddings or complex similarity matching. |

## Design Decisions

### D1: Rolling Reference Strategy

Use the most recently generated scene image as the single rolling reference, not all prior images. This keeps the reference count low (roster photos take priority) and avoids diminishing quality from stacking old references.

**Reference assembly order** (capped at 3 total):
1. Roster character photos (up to 2 if generated reference exists, up to 3 if not)
2. Most recent generated scene image (1 slot)

### D2: Where to Store the Rolling Reference

Add `generated_reference_path: str = ""` to the `Story` model (Pydantic). This persists across the session lifetime. It's set after each successful image generation and cleared on reset.

### D3: When to Update the Rolling Reference

After `generate_image()` completes successfully (status = COMPLETE), update `story.generated_reference_path` to the file path of the generated image. This happens in a callback/wrapper, not inside ImageService (which shouldn't know about Story sessions).

### D4: Helper Function for Reference Assembly

Create `_build_reference_images(story_session, character_service) -> list[str] | None` as a helper inside the router closure. This replaces the scattered `photo_paths` / `choice_photo_paths` assembly logic with a single function that:
1. Collects roster character photos
2. Appends `story.generated_reference_path` if set and file exists
3. Caps at 3 total
4. Returns the list (or None if empty)

### D5: Updating Reference After Generation

Wrap each `generate_image()` call in an async wrapper that awaits completion and then updates `story.generated_reference_path`. Since `generate_image()` runs as a background task modifying `Image` in-place, the wrapper checks the image status after the task completes and reads the file path from `STATIC_IMAGES_DIR / f"{scene_id}.png"`.

### D6: Reset Mechanism

Add `POST /{tier}/story/reset-appearance` route that clears `story.generated_reference_path` and redirects back to the story page.

### D7: Reference Indicator

Pass a `has_reference_images` boolean to the story template context. The template shows a small badge when true.

## Project Structure

### Documentation (this feature)

```text
specs/043-visual-consistency/
├── plan.md              # This file
├── research.md          # Image pipeline research
├── data-model.md        # Story model extension
├── quickstart.md        # Dev setup and verification
└── tasks.md             # Task breakdown (created by /speckit.tasks)
```

### Source Code (repository root)

```text
app/
├── models.py            # Add generated_reference_path to Story
├── routes.py            # Add _build_reference_images() helper, update all generate_image call sites,
│                        #   add reset-appearance route, add reference indicator to template context
└── services/
    └── image.py         # No changes needed — already accepts reference_images param

templates/
└── story.html           # Add reference indicator badge, add reset-appearance button

static/
└── css/style.css        # Minimal styling for reference indicator

tests/
└── test_visual_consistency.py  # New test file for reference chain logic
```

**Structure Decision**: Existing project structure. Changes touch 4-5 files, all in established locations. No new services or modules needed.
