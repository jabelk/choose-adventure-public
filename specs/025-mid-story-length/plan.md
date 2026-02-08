# Implementation Plan: Mid-Story Length Control

**Branch**: `025-mid-story-length` | **Date**: 2026-02-08 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/025-mid-story-length/spec.md`

## Summary

Add "Keep Going" and "Wrap It Up" buttons to the active story scene page that allow users to dynamically adjust the story's `target_depth` mid-session. "Keep Going" extends the target by 3 scenes; "Wrap It Up" reduces it to end within 1-2 scenes. Buttons appear conditionally based on current depth and scene type, and do not appear in the gallery reader.

## Technical Context

**Language/Version**: Python 3.11
**Primary Dependencies**: FastAPI, Jinja2, Pydantic
**Storage**: JSON file-based sessions (existing `app/session.py`)
**Testing**: pytest with `httpx.AsyncClient` / `TestClient`
**Target Platform**: Linux (Intel NUC) / macOS (dev)
**Project Type**: Web application
**Performance Goals**: Instant redirect — no AI generation on button click
**Constraints**: Buttons are simple POST forms that redirect back to the same scene
**Scale/Scope**: 2 new routes, 1 template modification, CSS additions

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Content Isolation | PASS | Buttons scoped within tier router; no cross-tier access. |
| II. Local-First | PASS | No external API calls — just modifies a local session value. |
| III. Iterative Simplicity | PASS | Two simple POST routes, template conditionals, CSS. No new abstractions. |
| IV. Archival by Design | PASS | Modified target_depth is persisted to session and gallery save. |
| V. Fun Over Perfection | PASS | Simple buttons, no configuration UI, no settings page. |

## Project Structure

### Documentation (this feature)

```text
specs/025-mid-story-length/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── spec.md              # Feature specification
├── checklists/
│   └── requirements.md  # Spec quality checklist
└── tasks.md             # Phase 2 output (created by /speckit.tasks)
```

### Source Code (repository root)

```text
app/
└── routes.py            # Two new POST routes: /story/keep-going/{scene_id}, /story/wrap-up/{scene_id}

templates/
└── scene.html           # Add conditional "Keep Going" and "Wrap It Up" buttons

static/css/
└── style.css            # Styles for the new buttons

tests/
└── test_mid_story_length.py  # Tests for button visibility and depth adjustments
```

**Structure Decision**: No new files needed in `app/`. The two new routes fit naturally inside `create_tier_router()` in `app/routes.py`. Template changes go in the existing `scene.html`. CSS goes in `style.css`.

## Implementation Approach

### Routes (app/routes.py)

Two new POST endpoints inside `create_tier_router()`:

1. **POST `/story/keep-going/{scene_id}`**
   - Get story session from cookie
   - Increase `story_session.story.target_depth` by 3
   - Call `update_session()` to persist
   - Redirect back to `/story/scene/{scene_id}`

2. **POST `/story/wrap-up/{scene_id}`**
   - Get story session from cookie
   - Compute new target: `current_depth + 2` where `current_depth = scene.depth`
   - If new target <= current_depth, set to `current_depth + 1`
   - Update `story_session.story.target_depth`
   - Call `update_session()` to persist
   - Redirect back to `/story/scene/{scene_id}`

### Template (templates/scene.html)

Add a `<div class="story-length-controls">` between the scene text and the choices section (inside the `{% else %}` branch, i.e., non-ending scenes only):

- "Keep Going" button: visible when `scene.depth >= story.target_depth - 2`
- "Wrap It Up" button: visible when `scene.depth >= 2`
- Both are `<form>` elements with `method="post"` pointing to the respective routes

### Context Variables

The `view_scene` route already passes `story` and `scene` to the template. Both `scene.depth` and `story.target_depth` are available — no additional context variables needed.

### Gallery Reader Exclusion

The gallery reader uses `reader.html`, not `scene.html`. The buttons are only added to `scene.html`, so they naturally won't appear in the gallery reader. No additional logic needed.

## Complexity Tracking

> No violations — all constitution gates pass.
