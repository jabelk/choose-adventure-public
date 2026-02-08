# Implementation Plan: Multi-Model Image & Video Generation

**Branch**: `013-image-video-gen` | **Date**: 2026-02-07 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/013-image-video-gen/spec.md`

## Summary

Expand image generation from 2 provider-level options (DALL-E, Gemini) to 5 specific models (GPT Image 1, GPT Image 1 Mini, GPT Image 1.5, Grok Imagine, Gemini). Add xAI Grok Imagine as a new image provider using the OpenAI SDK with custom base_url. Add video generation for story scenes via Grok Imagine's video API (text-to-video and image-to-video). Video mode is an opt-in toggle that generates short MP4 clips alongside static images, with async polling for results.

## Technical Context

**Language/Version**: Python 3, FastAPI, Jinja2 templates, Pydantic models
**Primary Dependencies**: FastAPI, openai (AsyncOpenAI), google-genai, httpx, Pillow
**New Dependencies**: httpx (for xAI image editing and video API — already a transitive dep of openai)
**Storage**: Local filesystem — JSON for story data, PNG for images, MP4 for videos
**Testing**: Manual via quickstart.md
**Target Platform**: Linux/macOS server (Intel NUC), browser clients on LAN
**Project Type**: Web application (server-rendered templates)
**Performance Goals**: Images within 30s, videos within 90s of scene generation
**Constraints**: Local-first, tier-isolated, all media stored on disk
**Scale/Scope**: Single-user home server, ~5 models, video files 1-10 MB each

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Content Isolation | PASS | Video files follow same tier-isolated route pattern as images. No cross-tier access. |
| II. Local-First | PASS | All videos downloaded and stored locally. Playable offline after generation. External APIs called only during generation. |
| III. Iterative Simplicity | PASS | Builds on existing image service pattern. Video is opt-in, not required. No new abstractions — extends existing registry and service. |
| IV. Archival by Design | PASS | Videos stored alongside images in static/videos/. Saved stories include video references. Gallery and reader display videos. |
| V. Fun Over Perfection | PASS | Video generation is the exciting new capability. Implementation reuses existing patterns (async tasks, polling, registry). No over-engineering. |

**Post-Design Re-check**: All 5 principles PASS. No violations.

## Project Structure

### Documentation (this feature)

```text
specs/013-image-video-gen/
├── plan.md              # This file
├── spec.md              # Feature specification
├── research.md          # Phase 0: API research and decisions
├── data-model.md        # Phase 1: Entity changes
├── quickstart.md        # Phase 1: Validation steps
├── contracts/
│   └── routes.md        # Phase 1: Route contracts
└── tasks.md             # Phase 2: Task breakdown (created by /speckit.tasks)
```

### Source Code (repository root)

```text
app/
├── config.py            # Settings (existing, no changes needed — xai_api_key already loaded)
├── models.py            # MODIFY: Add video fields to Image, Story, SavedScene, SavedStory
├── models_registry.py   # MODIFY: Expand IMAGE_PROVIDERS, add ImageModel dataclass
├── routes.py            # MODIFY: Update image_model handling, add video routes, video mode toggle
├── services/
│   ├── image.py         # MODIFY: Parameterize model in _generate_dalle, add _generate_grok, add video generation
│   └── gallery.py       # MODIFY: Include video cleanup on story deletion
├── tiers.py             # MODIFY: Change default_image_model from "dalle" to "gpt-image-1"

templates/
├── home.html            # MODIFY: Grouped image model selector, video mode toggle
├── scene.html           # MODIFY: Video player, video status polling, video retry
├── gallery.html         # MODIFY: Video badge on story cards
├── reader.html          # MODIFY: Inline video player

static/
├── css/style.css        # MODIFY: Video player styles, model group styles
├── js/app.js            # MODIFY: Video status polling, video retry
└── videos/              # NEW: Video file storage (created at runtime)
```

**Structure Decision**: Existing single-project structure. All changes are modifications to existing files plus a new runtime directory for video storage. No new Python modules needed — video generation is added to the existing image service.
