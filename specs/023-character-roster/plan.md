# Implementation Plan: Reusable Character Roster

**Branch**: `023-character-roster` | **Date**: 2026-02-07 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/023-character-roster/spec.md`

## Summary

Add a reusable character roster system for the NSFW tier that replaces the existing profile-embedded character storage. Characters are standalone entities with name, description, and optional reference photos, managed via a dedicated CRUD page. A multi-select character picker on the story start form lets users select multiple saved characters. Templates reference characters by a list of names. Existing profile characters are migrated to the roster, and profiles store roster character ID references instead of inline character data.

## Technical Context

**Language/Version**: Python 3 with FastAPI, Jinja2, Pydantic
**Primary Dependencies**: FastAPI, Jinja2, Pydantic, aiofiles, Pillow (for photo validation)
**Storage**: JSON files on disk (`data/characters/{tier}/{character_id}.json`, photos at `data/characters/{tier}/{character_id}/photos/`)
**Testing**: pytest with httpx AsyncClient
**Target Platform**: Linux server (Intel NUC), LAN-only access
**Project Type**: Web application (server-rendered with client-side JS)
**Performance Goals**: Instant character picker interaction (<1s), character list page loads <500ms
**Constraints**: Max 20 characters per tier, max 3 photos per character (reuse existing 10MB/file limit), NSFW tier only
**Scale/Scope**: Single user, ~20 characters max, ~60 photos max

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Content Isolation | PASS | Character roster is NSFW-tier only (FR-013). Storage is tier-scoped at `data/characters/{tier}/`. No cross-tier access. Kids tier has no character management routes. |
| II. Local-First | PASS | All character data stored locally as JSON files. No cloud dependency. Photos stored on disk. No external API calls for character management. |
| III. Iterative Simplicity | PASS | Simple CRUD with flat JSON files. No database. No search/filter (unnecessary at 20-char scale). Reuses existing upload validation. Migration is a one-time script. |
| IV. Archival by Design | PASS | Characters persisted as human-readable JSON. Photos stored alongside in self-contained directory trees. Portable and browsable. |
| V. Fun Over Perfection | PASS | Simple flat-file storage. No ORM, no migrations framework. Reuses existing patterns (profile service style). Multi-select picker is a practical UX win. |

No violations. All gates pass.

## Project Structure

### Documentation (this feature)

```text
specs/023-character-roster/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output
│   └── character-api.md
└── tasks.md             # Phase 2 output (/speckit.tasks)
```

### Source Code (repository root)

```text
app/
├── models.py                    # MODIFY: Add RosterCharacter model, update Profile model
├── tiers.py                     # MODIFY: Update StoryTemplate dataclass (character_names list)
├── routes.py                    # MODIFY: Add character CRUD routes, update story start, update template handling
├── main.py                      # MODIFY: Mount character photo static route
└── services/
    ├── character.py             # NEW: Character roster CRUD service
    ├── profile.py               # MODIFY: Remove inline character storage, add character_ids reference
    └── upload.py                # REUSE: Existing upload validation (no changes needed)

templates/
├── home.html                    # MODIFY: Add multi-select character picker, update template JS
├── characters.html              # NEW: Character management page (list + create/edit form)
└── base.html                    # MODIFY: Add nav link to characters page (NSFW only)

static/
├── js/
│   ├── character-picker.js      # NEW: Multi-select picker logic for story start form
│   └── upload.js                # REUSE: Existing upload logic (no changes needed)
└── css/
    └── style.css                # MODIFY: Add character management and picker styles

data/
└── characters/
    └── nsfw/                    # Runtime: character JSON files and photo directories
        └── {character_id}.json
        └── {character_id}/
            └── photos/

tests/
└── test_all_options.py          # MODIFY: Add character roster tests

scripts/
└── migrate_profile_characters.py  # NEW: One-time migration script
```

**Structure Decision**: Follows existing project conventions — new service in `app/services/`, new template in `templates/`, new JS in `static/js/`. No structural changes to the project layout.

## Complexity Tracking

No constitution violations. No complexity justification needed.
