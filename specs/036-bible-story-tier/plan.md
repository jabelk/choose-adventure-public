# Implementation Plan: Bible Story Tier

**Branch**: `036-bible-story-tier` | **Date**: 2026-02-08 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/036-bible-story-tier/spec.md`

## Summary

Add a dedicated Bible story tier at `/bible/` with 75+ interactive story templates spanning Genesis to Revelation. The tier uses biblically accurate content guidelines with NIrV-style scripture quotes, a Bible verse API for accurate text injection, warm reverent illustration style, and collapsible testament/book navigation for the template library. A guided reference field lets users request stories by Bible passage. The tier inherits all existing features (gallery, export, TTS, family mode, etc.) through the existing router factory pattern.

## Technical Context

**Language/Version**: Python 3.11+ (same as existing project)
**Primary Dependencies**: FastAPI, Jinja2, Pydantic, anthropic SDK, openai SDK, httpx (for Bible API calls — already installed)
**Storage**: N/A — templates hardcoded in Python, verse text fetched at runtime from Bible API
**Testing**: pytest (existing test suite pattern)
**Target Platform**: Linux server (Docker on NUC), local dev on macOS
**Project Type**: Web application (existing structure)
**Performance Goals**: N/A — same as existing tiers
**Constraints**: Bible API calls must fall back gracefully if unreachable (local-first principle)
**Scale/Scope**: 75+ templates, 1 new service file, ~8 files modified

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Content Isolation | PASS | New tier gets own URL namespace (/bible/), routing, session cookies, and theme. No cross-access with kids or adult tiers. Constitution explicitly states "New tiers SHOULD be addable without modifying existing tier interfaces." |
| II. Local-First | PASS | Bible API is optional — falls back to AI training data if unreachable. Templates are hardcoded locally. All story data stored on local filesystem. |
| III. Iterative Simplicity | PASS | Leverages existing router factory pattern. No new abstractions. Only new code is the tier config, templates, Bible API service, and collapsible UI sections. |
| IV. Archival by Design | PASS | Bible stories use the same gallery, export, and story persistence infrastructure. No changes needed. |
| V. Fun Over Perfection | PASS | The 75+ templates are a large but straightforward data entry task. No over-engineering — it's just more TierConfig data. |

**Gate result**: ALL PASS. No violations to justify.

**Post-Phase 1 re-check**: All principles still satisfied. The Bible API service is a small, focused addition that degrades gracefully. The collapsible template UI is simple CSS + JS with no new dependencies.

## Project Structure

### Documentation (this feature)

```text
specs/036-bible-story-tier/
├── plan.md              # This file
├── spec.md              # Feature specification
├── research.md          # Bible API research, tier extension analysis
├── data-model.md        # StoryTemplate extension, BibleService, TierConfig
├── quickstart.md        # Setup and verification steps
├── contracts/
│   └── routes.md        # Route behavior for Bible tier
├── checklists/
│   └── requirements.md  # Spec quality checklist
└── tasks.md             # Task breakdown (created by /speckit.tasks)
```

### Source Code (repository root)

```text
app/
├── tiers.py                 # MODIFIED: Add scripture_reference + section fields to StoryTemplate,
│                            #           add BIBLE_CONTENT_GUIDELINES, add "bible" TierConfig
├── bible_templates.py       # NEW: 75+ Bible story StoryTemplate definitions
├── story_options.py         # MODIFIED: Add bible field to OptionGroup, update choices_for_tier()
├── routes.py                # MODIFIED: Add _SURPRISE_FALLBACK_BIBLE, inject scripture_reference
│                            #           into prompt, handle guided reference field
├── config.py                # MODIFIED: Add BIBLE_API_KEY setting
└── services/
    └── bible.py             # NEW: BibleService (fetch_verses, validate_reference, parse_reference)

templates/
├── home.html                # MODIFIED: Collapsible sections for Bible tier, guided reference field
└── landing.html             # MODIFIED: Add Bible tier card with description

static/css/
└── style.css                # MODIFIED: Add .theme-bible and .tier-card-bible styles

.env.example                 # MODIFIED: Add BIBLE_API_KEY entry
```

**Structure Decision**: Follows existing project structure exactly. Bible templates are in a separate `bible_templates.py` file (not inline in `tiers.py`) because 75+ templates would make `tiers.py` unmanageably long. The `tiers.py` file imports from `bible_templates.py`.

## Complexity Tracking

No constitution violations — table not needed.
