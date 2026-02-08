# Implementation Plan: Memory Mode

**Branch**: `011-memory-mode` | **Date**: 2026-02-07 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/011-memory-mode/spec.md`

## Summary

Add toggleable user profiles per tier that shape AI story and image generation. Users create profiles with preferences (themes, art style, tone, story elements) and character definitions. When memory mode is toggled on at story start, the profile's preferences are injected into AI prompts. Profiles are stored as JSON files on disk, strictly isolated by tier. Characters can reference other profiles within the same tier for cross-profile story connections.

## Technical Context

**Language/Version**: Python 3
**Primary Dependencies**: FastAPI, Jinja2, Pydantic (all existing — no new deps)
**Storage**: JSON files on disk (`data/profiles/{tier}/`)
**Testing**: Manual testing via quickstart.md
**Target Platform**: Local LAN web server (Intel NUC)
**Project Type**: Web application (server-rendered)
**Performance Goals**: Profile CRUD operations complete instantly (<100ms), profile loading adds negligible time to story start
**Constraints**: <20 profiles per tier, <10 characters per profile
**Scale/Scope**: Single-user family app, 2 tiers, handful of profiles

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Content Isolation | PASS | Profiles are stored in `data/profiles/{tier}/` — tier-scoped directories enforce isolation. Routes are scoped to `/{tier}/profiles`. Cross-profile character links are same-tier only. |
| II. Local-First | PASS | Profiles stored as local JSON files. No cloud dependency. No external services for profile management. |
| III. Iterative Simplicity | PASS | No new dependencies. Follows existing patterns (JSON files, Pydantic models, Jinja2 templates, form-based CRUD). No abstractions beyond what's needed. |
| IV. Archival by Design | PASS | Profile data is stored in human-readable JSON. Profile ID on Story model preserves which profile influenced the story. |
| V. Fun Over Perfection | PASS | Simple form-based CRUD. No over-engineered admin UI. Profile preferences are free-form text — no rigid taxonomy. |

**Post-design re-check**: All gates still PASS.

## Project Structure

### Documentation (this feature)

```text
specs/011-memory-mode/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── routes.md
└── tasks.md
```

### Source Code (repository root)

```text
app/
├── models.py              # Add Profile, Character Pydantic models; add profile_id to Story
├── services/
│   ├── profile.py         # NEW: ProfileService — CRUD operations, profile context builder
│   └── story.py           # MODIFIED: Accept augmented content_guidelines/image_style
├── routes.py              # MODIFIED: Add profile routes, modify story/start

templates/
├── home.html              # MODIFIED: Add memory mode toggle + profile dropdown
├── profiles.html          # NEW: Profile list with create form
└── profile_edit.html      # NEW: Profile edit with character management

static/css/
└── style.css              # MODIFIED: Profile page styles, memory mode toggle styles

data/
└── profiles/              # NEW: Profile storage
    ├── kids/
    └── nsfw/
```

**Structure Decision**: Follows existing project layout. New service in `app/services/profile.py` matches existing pattern (`gallery.py`, `story.py`, `voice.py`). New templates follow existing Jinja2 pattern extending `base.html`. Storage in `data/profiles/` matches `data/stories/` and `data/progress/`.
