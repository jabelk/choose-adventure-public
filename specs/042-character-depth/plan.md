# Implementation Plan: Enhanced Character Creation & Relationship Depth

**Branch**: `042-character-depth` | **Date**: 2026-02-08 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/042-character-depth/spec.md`

## Summary

Add structured character creation with mobile-friendly pill selectors for physical attributes, personality, and style (replacing free-text-only description). Track relationship progression across stories per roster character. Expand kink toggles from 4 to 11+. The structured creator is available on all tiers (with NSFW-only attributes restricted), while relationship tracking and kink toggles are NSFW-only.

## Technical Context

**Language/Version**: Python 3.11+ (existing project)
**Primary Dependencies**: FastAPI, Jinja2, Pydantic (all existing — no new dependencies)
**Storage**: JSON flat files in `data/characters/{tier}/{character_id}.json` (extends existing character storage)
**Testing**: pytest (existing)
**Target Platform**: Self-hosted web on Intel NUC, accessed via LAN browsers (desktop + mobile)
**Project Type**: Web application (Python backend + Jinja2 templates + vanilla JS)
**Performance Goals**: Attribute selector rendering < 100ms, character save < 500ms
**Constraints**: Mobile-first UI (44px minimum tap targets), no new pip dependencies
**Scale/Scope**: ~20 characters per tier, 6 relationship stages, 11+ kink toggles

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Content Isolation | PASS | NSFW-only attributes (body type, bust size, archetype, kink toggles) restricted via tier checks in templates and routes. Kids/Bible tiers get only age-appropriate attributes (hair color, eye color, height). Relationship tracker NSFW-only. |
| II. Local-First | PASS | No new external dependencies. Structured attributes are hardcoded lists. Description composition happens client-side + server-side. |
| III. Iterative Simplicity | PASS | Extends existing patterns: RosterCharacter model gets new fields, KINK_TOGGLES dict gets new entries, pill selector UI matches existing kink toggle pill pattern. No new abstractions. |
| IV. Archival by Design | PASS | Structured attributes stored in character JSON alongside existing fields. Relationship data persisted per character. Composed descriptions stored as text for backward compatibility. |
| V. Fun Over Perfection | PASS | Mobile-friendly pill selectors replace typing — more fun to use. Relationship tracker adds depth without complexity. New kink toggles are data-only additions. |

**Gate result**: All principles pass. No violations to justify.

## Project Structure

### Documentation (this feature)

```text
specs/042-character-depth/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output
│   └── api.md
└── tasks.md             # Phase 2 output (created by /speckit.tasks)
```

### Source Code (repository root)

```text
app/
├── models.py                    # MODIFY: Add attributes dict + relationship fields to RosterCharacter
├── services/character.py        # MODIFY: Add attribute storage/retrieval, relationship advancement
├── story_options.py             # MODIFY: Add 7+ new KINK_TOGGLES entries, add CHARACTER_ATTRIBUTES dict
├── routes.py                    # MODIFY: Accept structured attributes on create/update, inject relationship context
└── tiers.py                     # NO CHANGE (tier detection already available)

templates/
├── characters.html              # MODIFY: Add pill selector UI for structured attributes, relationship display
├── home.html                    # MODIFY: Add inline pill selectors in character section
└── base.html                    # NO CHANGE

static/
├── css/style.css                # MODIFY: Add pill selector styles (extend existing kink-pill pattern)
└── js/
    ├── character-attributes.js  # NEW: Pill selector logic, compose description preview
    └── character-picker.js      # MODIFY: Show relationship stage badge on picker cards

tests/
└── test_character_roster.py     # MODIFY: Add tests for structured attributes, relationship tracking
```

**Structure Decision**: Extends existing single-project structure. No new directories — new code goes into existing files following established patterns. One new JS file for the attribute selector component (shared between characters.html and home.html).

## Design Decisions

### D1: Attribute Data Structure

Structured attributes stored as a flat `dict[str, str]` on `RosterCharacter.attributes`, keyed by attribute category (e.g., `{"hair_color": "blonde", "body_type": "athletic"}`). This is simpler than nested objects and easy to serialize to JSON.

The composed text description is stored in the existing `description` field for backward compatibility — existing characters with free-text descriptions continue to work unchanged.

### D2: Attribute Options Definition

All attribute options defined as a single `CHARACTER_ATTRIBUTES` dict in `app/story_options.py` (same file as `KINK_TOGGLES`). Each attribute category specifies its options, display name, and tier restriction:

```python
CHARACTER_ATTRIBUTES = {
    "hair_color": {
        "label": "Hair Color",
        "options": ["Blonde", "Brunette", "Black", "Red", "Auburn", "Silver", "Pink", "Blue"],
        "tier_restrict": None,  # Available on all tiers
    },
    "bust_size": {
        "label": "Bust Size",
        "options": ["A", "B", "C", "D", "DD"],
        "tier_restrict": "nsfw",  # NSFW only
    },
    # ...
}
```

### D3: Description Composition

Client-side JS composes a preview description from selected pills and displays it in a read-only textarea. On form submit, the server re-composes from the attribute selections to produce the canonical description stored in `RosterCharacter.description`. Free-text override field appends additional text after the composed description.

Composition template: `"{hair_color} hair, {eye_color} eyes, {height}, {body_type} build. {temperament} and {energy}. {clothing_style} style with a {aesthetic_vibe} vibe."`

### D4: Relationship Tracker

New fields on `RosterCharacter`:
- `relationship_stage: str` — one of: strangers, acquaintances, flirting, dating, intimate, committed
- `story_count: int` — number of completed stories with this character
- `last_story_date: Optional[str]` — ISO date of last completed story

Auto-advancement: After `gallery_service.save_story()` is called with a roster character, the character's `story_count` increments and `relationship_stage` advances one level (if not at max). Hook point: routes.py where `gallery_service.save_story(story_session)` is called (6 locations, all have access to `story_session.story.roster_character_ids`).

### D5: Relationship Context Injection

When building character context blocks in routes.py (line 459-474), check `relationship_stage` and `story_count`. Inject relationship context into `content_guidelines`:

```
CHARACTER:
Name: Margot Ellis
Appearance: Blonde hair, hazel eyes, athletic build...
Relationship: You've been dating Margot for a while now (5 stories together). The chemistry is undeniable.
```

### D6: Inline Attribute Selectors on Story Start

The home.html character section (currently has roster picker + manual name/description fields) gets the same pill selector component. If a user selects a roster character AND defines inline attributes, the roster character takes priority (spec requirement). The inline selectors compose a description that goes into the existing manual character description field.

### D7: New Kink Toggles

7 new entries added to `KINK_TOGGLES` dict in `story_options.py`. Same structure as existing toggles: `(display_name, story_prompt, image_prompt_addition)`. No code changes needed beyond data — the existing `build_kink_prompt()` function and template loop handle them automatically.

## Complexity Tracking

> No constitution violations — this section is intentionally empty.
