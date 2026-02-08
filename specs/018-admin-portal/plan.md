# Implementation Plan: Admin Portal

**Branch**: `018-admin-portal` | **Date**: 2026-02-07 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/018-admin-portal/spec.md`

## Summary

Add a standalone `/admin` page that provides storage visibility and management: a dashboard showing disk usage, a unified story list with delete (including associated media), orphan file detection and cleanup, and in-progress save management. Follows the existing FastAPI + Jinja2 + file-based storage patterns. No new dependencies required.

## Technical Context

**Language/Version**: Python 3.12
**Primary Dependencies**: FastAPI, Jinja2 (already in project)
**Storage**: File-based — JSON in `data/stories/` and `data/progress/`, images in `static/images/`, videos in `static/videos/`
**Testing**: Manual testing via browser (consistent with project approach)
**Target Platform**: Linux server (NUC) via Docker, macOS for local dev
**Project Type**: Web application (server-rendered templates)
**Performance Goals**: Dashboard loads in under 3 seconds with 100+ stories
**Constraints**: No new dependencies, no authentication
**Scale/Scope**: Single admin page with 4 sections, 1 new template, 1 new service, 1 new router

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Content Isolation | PASS | Admin page is tier-independent at `/admin`. Does not create cross-tier navigation in user-facing pages. Stories from all tiers are visible only in admin context. |
| II. Local-First | PASS | No external API calls. All operations are local filesystem reads/deletes. |
| III. Iterative Simplicity | PASS | Single page, no new dependencies, follows existing patterns (gallery service, Jinja2 templates). No abstractions beyond what's needed. |
| IV. Archival by Design | PASS | Does not change archival format. Delete is intentional admin action with confirmation. Orphan cleanup only removes unreferenced files. |
| V. Fun Over Perfection | PASS | Simple implementation — one service file, one template, one router. No over-engineering. |

No violations. No complexity tracking needed.

## Project Structure

### Documentation (this feature)

```text
specs/018-admin-portal/
├── plan.md              # This file
├── research.md          # Phase 0 output (minimal — no unknowns)
├── quickstart.md        # Phase 1 output
└── tasks.md             # Phase 2 output (/speckit.tasks command)
```

### Source Code (repository root)

```text
app/
├── main.py              # MODIFY — mount admin router
├── services/
│   └── admin.py         # NEW — AdminService (storage stats, orphan detection, delete logic)
└── admin_routes.py      # NEW — admin router (/admin, /admin/delete-story, etc.)

templates/
└── admin.html           # NEW — admin dashboard template
```

**Structure Decision**: Follows existing project conventions. A new `admin_routes.py` at the app level (like `routes.py`) with a dedicated `AdminService` in services. The admin router is mounted directly on the app (not through the tier router factory) since it's tier-independent.

## Key Design Decisions

### 1. Separate router file (not in routes.py)

The existing `routes.py` uses a `create_tier_router()` factory pattern scoped to tiers. The admin page is tier-independent, so it gets its own `admin_routes.py` with a simple `APIRouter(prefix="/admin")` mounted in `main.py`.

### 2. AdminService for all business logic

A single `AdminService` class handles:
- **Storage stats**: Walk each directory, count files, sum sizes
- **Story listing**: Reuse `GalleryService.list_stories()` across all tiers, plus raw file listing for corrupted files
- **Story deletion**: Delete JSON + find all scene IDs in the story + delete matching image/video files
- **Orphan detection**: Collect all scene IDs from all stories and in-progress saves, compare against files on disk
- **In-progress listing**: Read each progress file, extract metadata

### 3. Confirmation via JavaScript confirm()

Simple browser `confirm()` dialogs before destructive POST actions. No custom modal needed — this is a personal admin tool.

### 4. POST-redirect-GET for all actions

Delete and cleanup actions use POST forms that redirect back to `/admin` after completion. Standard pattern that prevents accidental resubmission.

## Dependencies

No new Python packages. Uses only:
- `pathlib` (stdlib) — file operations
- `json` (stdlib) — reading story files
- `os` (stdlib) — file size calculation
- Existing `GalleryService` — reuse story loading logic
- Existing `SavedStory` model — story metadata
