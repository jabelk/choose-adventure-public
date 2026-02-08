# Implementation Plan: Family Mode

**Branch**: `035-family-mode` | **Date**: 2026-02-07 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/035-family-mode/spec.md`

## Summary

Add a Family Mode feature that lets users save their kids' names, genders, and ages plus parent names once, then toggle Family Mode on the home page to inject those names into every new story. Storage follows the existing JSON-file pattern at `data/family/{tier}/family.json`. A FamilyService handles CRUD and prompt context building. A new Family settings page is accessible from both tiers.

## Technical Context

**Language/Version**: Python 3.11 + Jinja2 templates
**Primary Dependencies**: FastAPI, Pydantic, Jinja2
**Storage**: JSON files at `data/family/{tier}/family.json`
**Testing**: pytest with FastAPI TestClient
**Target Platform**: Web (Docker on Linux NUC, dev on macOS)
**Project Type**: Web application (server-rendered with JS enhancement)
**Performance Goals**: N/A (single-user LAN app)
**Constraints**: Single family per tier, max 6 children + 2 parents
**Scale/Scope**: 2 tiers, 1 family each, 1 new template, 1 new service

## Constitution Check

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Content Isolation | PASS | Family data stored per tier at `data/family/{tier}/`. No cross-tier access. |
| II. Local-First | PASS | All data stored on local filesystem. No cloud dependencies. |
| III. Iterative Simplicity | PASS | Single JSON file per tier, one service class, one template. No abstractions beyond what's needed. |
| IV. Archival by Design | N/A | Family data is configuration, not story content. |
| V. Fun Over Perfection | PASS | Simple single-page form, minimal code. |

## Project Structure

### Documentation (this feature)

```text
specs/035-family-mode/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Entity definitions
├── spec.md              # Feature specification
├── checklists/
│   └── requirements.md  # Spec quality checklist
└── tasks.md             # Phase 2 output
```

### Source Code (files modified/created)

```text
app/
├── models.py                      # Add FamilyChild, FamilyParent, Family models
├── services/
│   └── family.py                  # NEW: FamilyService (CRUD + build_family_context)
├── routes.py                      # Add family routes, family_mode form param, prompt injection
└── main.py                        # Import family service (if needed)

templates/
├── home.html                      # Add Family Mode toggle + Family link
└── family.html                    # NEW: Family settings page

static/css/
└── style.css                      # Family form styles (reuse existing patterns)

data/
└── family/
    ├── kids/family.json           # Created at runtime
    └── nsfw/family.json           # Created at runtime

tests/
└── test_family_mode.py            # NEW: Family CRUD + toggle + prompt injection tests
```

**Structure Decision**: Follows existing project structure. New service at `app/services/family.py`, new template at `templates/family.html`. Family data stored at `data/family/{tier}/family.json` following the per-tier pattern.

## Key Implementation Details

### FamilyService

- `get_family(tier) -> Family | None` — Load family from JSON file
- `save_family(family) -> Family` — Save/overwrite family JSON
- `delete_family(tier) -> bool` — Remove family JSON file
- `build_family_context(family) -> str` — Build prompt addition text

### Prompt Context Format

```text
FAMILY MODE — The following family members should appear as characters in this story:

Children (main characters):
- Isla (girl, age 5) — feature as a main character
- Nora (girl, age 2) — feature as a main character

Parents (supporting characters, include naturally when appropriate):
- Dad
```

### Routes

- `GET /{tier}/family` — Family settings page (show current family or creation form)
- `POST /{tier}/family/save` — Save/update family (receives form with children[] and parents[])
- `POST /{tier}/family/delete` — Delete entire family
- `POST /{tier}/family/remove-child/{index}` — Remove a single child
- `POST /{tier}/family/remove-parent/{index}` — Remove a single parent

### Home Page Integration

- Add `family_mode` hidden form field (like `memory_mode`)
- Show toggle only when `family` exists (passed from route handler)
- In `start_story`, if `family_mode == "on"`, load family and inject context
