# Implementation Plan: Story Gallery

**Branch**: `003-story-gallery` | **Date**: 2026-02-07 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/003-story-gallery/spec.md`

## Summary

Implement a persistent story archive that auto-saves completed adventures to disk as JSON files and provides a per-tier gallery for browsing and re-reading past stories. Each tier gets a gallery page showing story cards and a read-only story reader with scene-by-scene navigation.

## Technical Context

**Language/Version**: Python 3 (same as existing)
**Primary Dependencies**: FastAPI, Pydantic, Jinja2 (all existing — no new dependencies)
**Storage**: JSON files in `data/stories/` directory, one file per completed story
**Testing**: Manual testing per quickstart.md (per Constitution Principle V)
**Target Platform**: Local LAN server (warp-nuc), macOS for development
**Project Type**: Single web application
**Performance Goals**: Gallery loads in <2 seconds for up to 100 stories
**Constraints**: No external dependencies for serving/browsing (Constitution Principle II)
**Scale/Scope**: Family use, ~10-50 stories expected over time

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Content Isolation | PASS | Gallery is tier-scoped. Routes inside create_tier_router(), files filtered by tier field. No cross-tier leakage. |
| II. Local-First | PASS | JSON files on local disk. No cloud dependency for browsing gallery. |
| III. Iterative Simplicity | PASS | Simple file-per-story persistence. No database, no caching, no pagination. Minimal new code. |
| IV. Archival by Design | PASS | Full branching tree saved (all scenes, not just path taken). JSON is human-readable and portable. Gallery is a first-class browsing interface. |
| V. Fun Over Perfection | PASS | No tests beyond manual verification. Simple scrollable list. No delete/edit features. Ship fast. |

## Project Structure

### Documentation (this feature)

```text
specs/003-story-gallery/
├── plan.md              # This file
├── research.md          # 8 design decisions
├── data-model.md        # SavedStory, SavedScene, SavedChoice entities
├── quickstart.md        # Manual testing guide
├── contracts/
│   └── routes.md        # 3 new routes, 1 modified route, 2 new templates
└── checklists/
    └── requirements.md  # Spec quality checklist
```

### Source Code (repository root)

```text
app/
├── models.py            # MODIFIED: Add SavedStory, SavedScene, SavedChoice models
├── routes.py            # MODIFIED: Add gallery routes, auto-save on ending
└── services/
    └── gallery.py       # NEW: GalleryService (save/load/list stories)

data/
└── stories/             # NEW: Persisted story JSON files (created at runtime)

templates/
├── home.html            # MODIFIED: Add gallery link
├── gallery.html         # NEW: Gallery listing page with story cards
└── reader.html          # NEW: Read-only story scene viewer

static/css/
└── style.css            # MODIFIED: Add gallery card and reader styles
```

**Structure Decision**: Follows existing single-project layout. New service in `app/services/`, new templates in `templates/`, new data directory at project root for persistent storage (separate from `static/` which is for served assets).

## Key Design Decisions

1. **JSON files over database** — Human-readable, portable, no new dependencies (Research Decision 1)
2. **Full branching tree saved** — Constitution Principle IV requires preserving all paths (Research Decision 2)
3. **Auto-save on ending only** — Clean gallery with no abandoned story clutter (Research Decision 3)
4. **Scene index navigation** — Reader uses integer index into path_history for simple Next/Previous (Research Decision 4)
5. **GalleryService class** — Follows existing service pattern (StoryService, ImageService) (Research Decision 5)
6. **SavedStory model** — Dedicated Pydantic model decoupled from session format (Research Decision 6)
