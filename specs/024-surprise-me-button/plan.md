# Implementation Plan: "Surprise Me" Button

**Branch**: `024-surprise-me-button` | **Date**: 2026-02-07 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/024-surprise-me-button/spec.md`

## Summary

Add a one-tap "Surprise Me" button to both tier home pages that starts a story with randomly selected parameters (template, story flavor options, art style, length, and kinks for NSFW). The button submits a POST to a new server-side endpoint that assembles random parameters and redirects to the existing `/story/start` flow. No new data models or services needed — this is a thin endpoint + template/CSS change.

## Technical Context

**Language/Version**: Python 3 with FastAPI, Jinja2 templates
**Primary Dependencies**: FastAPI, Python `random` module, existing `app/story_options.py` and `app/models_registry.py`
**Storage**: N/A — no new data persistence
**Testing**: pytest with existing `TestClient` fixtures
**Target Platform**: Self-hosted web app on Intel NUC (LAN-only)
**Project Type**: Web application (server-rendered templates)
**Performance Goals**: Instant response — the surprise-me endpoint just assembles random values and redirects
**Constraints**: Must work on both tiers with content isolation
**Scale/Scope**: Single new route + template button + CSS styling

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Content Isolation | PASS | Random selections scoped to tier's own templates, options, and kinks. Kids tier never selects NSFW content. |
| II. Local-First | PASS | No new external dependencies. Uses Python `random` module. |
| III. Iterative Simplicity | PASS | Minimal feature: one route, one button, simple randomization. No over-engineering. |
| IV. Archival by Design | PASS | Stories started via "Surprise Me" flow through the existing story start pipeline and are archived normally. |
| V. Fun Over Perfection | PASS | This IS the fun feature. Zero decision fatigue, immediate gratification. |

## Project Structure

### Documentation (this feature)

```text
specs/024-surprise-me-button/
├── plan.md              # This file
├── spec.md              # Feature specification
├── research.md          # Phase 0 output (minimal — no unknowns)
├── checklists/
│   └── requirements.md  # Spec quality checklist
└── tasks.md             # Phase 2 output (created by /speckit.tasks)
```

### Source Code (repository root)

```text
app/
├── routes.py            # MODIFY: Add surprise_me POST route inside create_tier_router()
├── story_options.py     # READ ONLY: Use get_option_groups(), KINK_TOGGLES for random selection
├── models_registry.py   # READ ONLY: Use get_art_styles(), get_available_models()
└── tiers.py             # READ ONLY: Access tier_config.templates for random template

templates/
└── home.html            # MODIFY: Add "Surprise Me" button near "Start Adventure"

static/css/
└── style.css            # MODIFY: Add surprise-me button styling

tests/
└── test_surprise_me.py  # CREATE: Tests for surprise-me endpoint
```

**Structure Decision**: This feature touches existing files only (routes, template, CSS) plus one new test file. No new modules, services, or models needed.

## Implementation Approach

### Server-Side Endpoint

A new `POST /{tier}/story/surprise` route inside `create_tier_router()`:

1. Randomly select a template from `tier_config.templates` (or generate a fallback prompt if empty)
2. Randomly select one value from each story flavor option group using `get_option_groups()` and `choices_for_tier(tier)`
3. Randomly select an art style from `get_art_styles(tier_config.name)`
4. Randomly select a story length from `["short", "medium", "long"]`
5. For NSFW tier: randomly select 0-2 kink keys from `KINK_TOGGLES`
6. Pick first available AI model and image model
7. Assemble all params into a form-like dict and call the existing `start_story()` logic internally, or redirect to `/story/start` with the params

**Design decision**: The endpoint will directly invoke the same logic as `start_story()` rather than doing a redirect-with-form-data (which would require client-side form construction). This keeps it as a simple POST that returns the same response as `start_story()`.

### Template Button

A prominent button placed in the home page header area, next to the existing "Start Adventure" button area. It's a simple `<form>` with `action="/{tier}/story/surprise"` and `method="post"` containing just a submit button — no form fields.

### Styling

Fun, visually distinct button with a different color/style from the primary "Start Adventure" button. Uses existing CSS custom properties for tier theming.

## Complexity Tracking

No constitution violations. No complexity justifications needed.
