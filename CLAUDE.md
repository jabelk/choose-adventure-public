# Choose Your Own Adventure

Interactive choose your own adventure web app with images.

## Tech Stack

<!-- Replace with your project's tech stack -->
- {{LANGUAGE}} (managed with {{PACKAGE_MANAGER}})

## Branching Strategy

- **Never commit directly to `main`.**
- For each unit of work (feature, fix, refactor), create a new branch off `main`:
  - Format: `<short-description>` (e.g., `add-episode-parser`, `fix-url-handling`)
- When work is complete, create a pull request against `main` with a summary of what was done.
- Merge the PR (squash or merge commit, no rebase) to keep a clean paper trail.
- Delete the feature branch after merge.

## Documentation Strategy

There are two documentation audiences. Keep them separate.

### For Agents: `.specify/` (source of truth)

All design decisions, specs, plans, and task tracking live here. This is the **primary reference for Claude and other coding agents**. Before making implementation decisions, always consult the relevant `.specify/` files.

**Directory structure:**

| Path | Purpose | When to update |
|------|---------|----------------|
| `.specify/memory/constitution.md` | Non-negotiable project principles. All work must comply. | Rarely — only when principles change. |
| `specs/<feature>/spec.md` | What to build. User stories, requirements, acceptance criteria. | Created via `/speckit.specify`, updated if requirements change. |
| `specs/<feature>/plan.md` | How to build it. Tech choices, architecture, project structure. | Created via `/speckit.plan`, updated if approach changes. |
| `specs/<feature>/tasks.md` | Ordered task breakdown with dependencies and checkpoints. | Created via `/speckit.tasks`, checked off during implementation. |
| `specs/<feature>/research.md` | Phase 0 research output (dependencies, alternatives). | Created during `/speckit.plan`. |
| `specs/<feature>/data-model.md` | Entity definitions and relationships. | Created during `/speckit.plan`. |
| `specs/<feature>/contracts/` | API contracts, interfaces. | Created during `/speckit.plan`. |
| `.specify/templates/` | Templates used by spec-kit. Do not edit directly. | Never — managed by spec-kit. |
| `.specify/scripts/` | Helper scripts for spec-kit. Do not edit directly. | Never — managed by spec-kit. |

### For Humans: `docs/` and `README.md`

High-level documentation for human readers lives in `docs/` and the repo `README.md`.

- `README.md` — Project overview, how to install, how to run, quick examples.
- `docs/` — Architecture overview, design rationale, usage guides. Written in plain language for a human audience.

### Rules for Documentation Updates

1. **Do not create markdown files outside of `.specify/`, `docs/`, or `README.md`** unless explicitly asked.
2. **Do not proactively generate or rewrite docs.** Only update docs when: (a) the user asks, or (b) a spec-kit command requires it.
3. **Keep updates surgical.** When updating a `.specify/` file, edit the specific section that changed — do not regenerate the entire file.
4. **Spec files are append/edit, not rewrite.** If a plan or spec exists, update it incrementally. Do not overwrite prior decisions without discussion.

## Spec-Driven Development Workflow

This project uses [GitHub Spec Kit](https://github.com/github/spec-kit). The workflow is:

1. `/speckit.constitution` — Establish project principles (done once, lives in `.specify/memory/constitution.md`)
2. `/speckit.specify` — Write the specification for a feature
3. `/speckit.plan` — Create the implementation plan
4. `/speckit.tasks` — Break the plan into ordered tasks
5. `/speckit.implement` — Execute tasks

**Before writing any code**, check that a spec and plan exist for the work. If they don't, raise it with the user.

## Agent Behavior Guidelines

- **Always read `.specify/memory/constitution.md` before starting a new feature** to ensure compliance with project principles.
- **Always read the relevant `specs/<feature>/` files before implementing** to understand the design decisions already made.
- **Do not skip the spec-kit workflow.** If asked to build something new, suggest running through specify → plan → tasks → implement.
- **Commit after each logical unit of work**, not after every single file change.
- **When in doubt about a design decision**, check the spec and plan first, then ask the user.

## Active Technologies
<!-- Updated automatically by spec-kit during /speckit.plan -->
- Python 3.11+ + FastAPI, Jinja2, uvicorn, anthropic (AsyncAnthropic), openai (AsyncOpenAI), python-dotenv, python-multipar (001-core-story-engine)
- In-memory (server-side session dict) + local filesystem for generated images (001-core-story-engine)
- Python 3.11+ (same as 001) + FastAPI, Jinja2, uvicorn, anthropic, openai (same as 001) (002-content-isolation)
- In-memory sessions + local filesystem for images (same as 001) (002-content-isolation)
- Python 3 (same as existing) + FastAPI, Pydantic, Jinja2 (all existing — no new dependencies) (003-story-gallery)
- JSON files in `data/stories/` directory, one file per completed story (003-story-gallery)
- Python 3 (matches existing project) + FastAPI, Pydantic, Jinja2 (all existing — no new dependencies) (004-story-resume)
- JSON files in `data/progress/{tier_name}.json` (004-story-resume)
- Python 3.11+ + FastAPI, Jinja2, Pydantic, anthropic SDK, openai SDK (005-image-polish)
- JSON flat files (stories in `data/stories/`, progress in `data/progress/`) (005-image-polish)
- Python 3.11+ + FastAPI, Jinja2, Pydantic, anthropic SDK, openai SDK, google-genai (new) (006-multi-model)
- Python 3.11+ + FastAPI, Jinja2, Pydantic, D3.js v7 (vendored) (008-branching-explorer)
- Python 3.11+ + FastAPI, Jinja2, Pydantic, fpdf2 (new — PDF generation) (009-story-export)
- JSON flat files (stories in `data/stories/`, images in `static/images/`) (009-story-export)
- Python 3.11+ (server), JavaScript ES6+ (client) + FastAPI (existing), OpenAI SDK (existing, for Whisper), Web Speech API (browser), MediaRecorder API (browser) (010-voice-input)
- N/A — audio is ephemeral, not persisted (010-voice-input)
- Python 3 + FastAPI, Jinja2, Pydantic (all existing — no new deps) (011-memory-mode)
- JSON files on disk (`data/profiles/{tier}/`) (011-memory-mode)
- Python 3.14 (managed with pip/venv) + FastAPI, Jinja2, Pydantic, anthropic SDK, openai SDK, google-genai SDK, Pillow (NEW — for image dimension validation) (012-photo-import)
- Local filesystem (JSON + image files in `data/`) (012-photo-import)
- Python 3, FastAPI, Jinja2 templates, Pydantic models + FastAPI, openai (AsyncOpenAI), google-genai, httpx, Pillow (013-image-video-gen)
- Local filesystem — JSON for story data, PNG for images, MP4 for videos (013-image-video-gen)
- Python 3 (backend unchanged), Vanilla JavaScript (service worker + gestures) + No new pip/npm dependencies. All PWA features are browser-native APIs. (014-mobile-pwa)
- Browser Cache API (via service worker) for offline conten (014-mobile-pwa)
- Python 3 (backend), Vanilla JavaScript (client-side form filling) + No new dependencies. Uses existing FastAPI, Jinja2, dataclass patterns. (015-story-templates)
- Static configuration in Python code (same pattern as existing `suggestions` field on TierConfig) (015-story-templates)
- Bash (deploy scripts), INI (systemd), Caddyfile (reverse proxy) + systemd, Caddy (apt package), Python 3.10+ (on NUC) (016-linux-hosting)
- No new storage — app uses existing file-based storage (016-linux-hosting)
- Python 3.12 (matching NUC), Bash for scripts + Docker Compose v2, Caddy 2 (alpine image), python:3.12-slim base (017-docker-deployment)
- Filesystem — bind mounts for `data/` and `static/images/` and `static/videos/` (017-docker-deployment)
- Python 3.12 + FastAPI, Jinja2 (already in project) (018-admin-portal)
- File-based — JSON in `data/stories/` and `data/progress/`, images in `static/images/`, videos in `static/videos/` (018-admin-portal)
- Python 3.12 + FastAPI, Jinja2, python-multipart (already in project for profile photo uploads) (019-direct-image-upload)
- File-based — temporary uploads in `data/uploads/{session_id}/`, cleaned up on session end (019-direct-image-upload)
- JSON flat files in `data/stories/`, images in `static/images/` (020-picture-book-mode)
- Python 3 (FastAPI + Jinja2) + OpenAI SDK (`openai` package, already installed), HTML5 Audio API (022-read-aloud-tts)
- N/A (audio generated on demand, not persisted) (022-read-aloud-tts)
- Python 3 with FastAPI, Jinja2, Pydantic + FastAPI, Jinja2, Pydantic, aiofiles, Pillow (for photo validation) (023-character-roster)
- JSON files on disk (`data/characters/{tier}/{character_id}.json`, photos at `data/characters/{tier}/{character_id}/photos/`) (023-character-roster)
- Python 3 with FastAPI, Jinja2 templates + FastAPI, Python `random` module, existing `app/story_options.py` and `app/models_registry.py` (024-surprise-me-button)
- N/A — no new data persistence (024-surprise-me-button)
- Python 3.11 + FastAPI, Jinja2, Pydantic (025-mid-story-length)
- JSON file-based sessions (existing `app/session.py`) (025-mid-story-length)
- Python 3.14 (existing project) + FastAPI, Jinja2, Pydantic, anthropic SDK, openai SDK (027-story-sequel-mode)
- JSON flat files in `data/stories/` (existing gallery storage) (027-story-sequel-mode)
- Python 3.14 (existing project) + FastAPI, Jinja2, fpdf2 (already used for story PDF export), anthropic/openai SDKs (image generation) (028-coloring-page-export)
- Static files on disk at `static/images/` (PNG), no database (028-coloring-page-export)
- Python 3 with FastAPI, Jinja2 templates + Vanilla JavaScript (client-side), existing ImageService (server-side) (031-scene-image-prompt-tweaks)
- Existing `static/images/` for images, `data/stories/` for gallery JSON (031-scene-image-prompt-tweaks)
- Python 3 with FastAPI, Jinja2 templates + Vanilla JavaScript (client-side only), HTML5 Audio API (032-sound-effects-ambiance)
- Static audio files in `static/audio/`, mute preference in browser localStorage (032-sound-effects-ambiance)
- Python 3 with FastAPI, Jinja2 templates + Existing CharacterService, character-picker.js, characters.html template (033-kids-favorite-characters)
- JSON files at `data/characters/{tier}/{character_id}.json`, photos at `data/characters/{tier}/{character_id}/photos/` (033-kids-favorite-characters)
- Python 3.11 + JavaScript (vanilla, no framework) + FastAPI, Jinja2, Pydantic (034-refresh-templates)
- N/A (templates are hardcoded in `app/tiers.py`) (034-refresh-templates)
- Python 3.11 + Jinja2 templates + FastAPI, Pydantic, Jinja2 (035-family-mode)
- JSON files at `data/family/{tier}/family.json` (035-family-mode)
- Python 3.11+ (same as existing project) + FastAPI, Jinja2, Pydantic, anthropic SDK, openai SDK, httpx (for Bible API calls — already installed) (036-bible-story-tier)
- N/A — templates hardcoded in Python, verse text fetched at runtime from Bible API (036-bible-story-tier)

## Recent Changes
<!-- Updated automatically by spec-kit during /speckit.plan -->
