# Implementation Plan: Core Story Engine

**Branch**: `001-core-story-engine` | **Date**: 2026-02-07 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-core-story-engine/spec.md`

## Summary

Build a Python web application where a user enters a text prompt and selects a story length, then plays through an AI-generated choose-your-own-adventure story with images. Scenes are generated on-demand (one at a time as choices are made) using Claude for text and OpenAI gpt-image-1 for images. The app runs locally via FastAPI with Jinja2 server-side templates.

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**: FastAPI, Jinja2, uvicorn, anthropic (AsyncAnthropic), openai (AsyncOpenAI), python-dotenv, python-multipart
**Storage**: In-memory (server-side session dict) + local filesystem for generated images
**Testing**: pytest (critical paths only per Principle V)
**Target Platform**: macOS (development), Linux x86_64 (Intel NUC deployment)
**Project Type**: Single project (server-side rendered web app)
**Performance Goals**: First scene text in <30 seconds; image quality prioritized over speed
**Constraints**: LAN-only access, single concurrent user for v1, no database
**Scale/Scope**: 1 user, ~4 pages (home, scene, error, loading), ~8 source files

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Content Isolation | PASS (deferred) | v1 is single-tier. Spec explicitly defers content isolation to later feature. No violation — architecture does not preclude adding tiers later. |
| II. Local-First | PASS | App runs entirely on local machine. AI APIs used for generation only; app serves content from local filesystem. |
| III. Iterative Simplicity | PASS | Minimal dependencies, no abstractions, on-demand generation is simplest viable approach. No premature multi-model support. |
| IV. Archival by Design | PASS (deferred) | v1 stories are ephemeral. Pydantic models with JSON serialization ensure future archival is trivial to add. Images saved to disk already. |
| V. Fun Over Perfection | PASS | Flat project structure, minimal testing, no over-engineering. Focus on getting story playback working. |

**Post-Phase 1 re-check**: All gates still pass. Design adds no unnecessary complexity.

## Project Structure

### Documentation (this feature)

```text
specs/001-core-story-engine/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output
│   └── routes.md        # Route contracts
└── tasks.md             # Phase 2 output (/speckit.tasks)
```

### Source Code (repository root)

```text
app/
├── __init__.py           # Package init
├── main.py               # FastAPI app creation, static files mount, startup
├── routes.py             # All route handlers (home, start, scene, choose, back, image status)
├── models.py             # Pydantic models (Story, Scene, Choice, Image, StorySession, enums)
├── session.py            # In-memory session store (dict-based, cookie session IDs)
├── config.py             # Settings from environment variables (API keys, defaults)
└── services/
    ├── __init__.py
    ├── story.py           # Claude API integration — scene generation, context management, summarization
    └── image.py           # OpenAI API integration — image generation, local file saving

templates/
├── base.html             # Base layout (head, body wrapper, common CSS/JS)
├── home.html             # Prompt input form with length selector
├── scene.html            # Scene display (text, image, choices, navigation)
└── error.html            # Error page with retry button

static/
├── css/
│   └── style.css         # App styling
├── js/
│   └── app.js            # Minimal JS for image polling and loading states
└── images/               # Generated scene images (created at runtime)

requirements.txt          # Python dependencies
.env.example              # API key template
```

**Structure Decision**: Single project with flat `app/` package. Server-side rendered with Jinja2 — no frontend/backend split. Services separated into `story.py` and `image.py` for clarity, but no deeper abstraction layers. This is the simplest structure that supports all v1 requirements.

## Complexity Tracking

No violations to justify. Design follows all constitution principles without exceptions.
