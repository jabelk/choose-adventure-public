# Implementation Plan: Image Retry & Polish

**Branch**: `005-image-polish` | **Date**: 2026-02-07 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/005-image-polish/spec.md`

## Summary

Improve the image generation experience with retry/regenerate capabilities,
polished loading animations, and smooth transitions. Add a POST retry endpoint
that resets Image status and kicks off a new background generation task. Replace
the basic spinner with a CSS pulsing gradient placeholder. Add a regenerate
button overlay on completed images. Prevent layout shift with fixed aspect-ratio
containers. No model changes needed — the existing Image/ImageStatus models
already support all required states.

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**: FastAPI, Jinja2, Pydantic, anthropic SDK, openai SDK
**Storage**: JSON flat files (stories in `data/stories/`, progress in `data/progress/`)
**Testing**: Manual testing via quickstart guide
**Target Platform**: Linux (Intel NUC) + macOS (development), served via LAN
**Project Type**: Web application (server-rendered with JS polling)
**Performance Goals**: Smooth 60fps CSS animations, no layout shift on image load
**Constraints**: Single-user, LAN-only, no WebSocket infrastructure
**Scale/Scope**: Personal app, 1 concurrent user, ~10-30s image generation time

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Content Isolation | PASS | Retry/regenerate endpoints scoped to `/{tier}/` prefix. No cross-tier access. |
| II. Local-First | PASS | No new cloud dependencies. Retry reuses existing OpenAI API calls. |
| III. Iterative Simplicity | PASS | Builds on existing polling + Image model. No new abstractions. |
| IV. Archival by Design | PASS | Regenerated images overwrite on disk; gallery reader is read-only. |
| V. Fun Over Perfection | PASS | CSS-only animations, minimal JS changes, no over-engineering. |

## Project Structure

### Documentation (this feature)

```text
specs/005-image-polish/
├── plan.md              # This file
├── spec.md              # Feature specification
├── research.md          # Phase 0: 8 design decisions
├── data-model.md        # No model changes; state transition docs
├── quickstart.md        # 8-step manual testing guide
├── contracts/
│   └── routes.md        # 1 new POST endpoint, modified JS contracts
├── checklists/
│   └── requirements.md  # Spec quality checklist (all pass)
└── tasks.md             # Phase 2 output (created by /speckit.tasks)
```

### Source Code (repository root)

```text
app/
├── routes.py            # Add POST /{tier}/story/image/{scene_id}/retry
├── services/
│   └── image.py         # No changes (existing generate_image works as-is)
└── models.py            # No changes (Image/ImageStatus already sufficient)

templates/
└── scene.html           # Update image container markup for new states

static/
├── css/
│   └── style.css        # Pulsing placeholder, fade-in, regenerate button styles
└── js/
    └── app.js           # retryImage(), updated pollImageStatus(), showFailedState()
```

**Structure Decision**: This feature touches the existing web application structure.
No new files are created — all changes are modifications to existing files. The
route, template, CSS, and JS changes follow the established patterns.

## Complexity Tracking

No constitution violations. No complexity justifications needed.
