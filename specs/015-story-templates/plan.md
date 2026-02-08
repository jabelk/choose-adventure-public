# Implementation Plan: Story Templates

**Branch**: `015-story-templates` | **Date**: 2026-02-07 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/015-story-templates/spec.md`

## Summary

Add pre-built story template cards to each tier's home page that pre-fill the story form (prompt + length) when clicked. Templates are defined as static data in the tier configuration, replacing the existing suggestion chips. Each tier gets its own curated collection of 6+ templates with title, description, emoji, prompt text, and suggested length.

## Technical Context

**Language/Version**: Python 3 (backend), Vanilla JavaScript (client-side form filling)
**Primary Dependencies**: No new dependencies. Uses existing FastAPI, Jinja2, dataclass patterns.
**Storage**: Static configuration in Python code (same pattern as existing `suggestions` field on TierConfig)
**Testing**: Manual testing via browser
**Target Platform**: Web browser (desktop + mobile)
**Project Type**: Web application (FastAPI + Jinja2 templates + static files)
**Performance Goals**: No additional network requests — templates are embedded in the page HTML
**Constraints**: Templates must be tier-scoped (content isolation principle)
**Scale/Scope**: ~12 templates total (6 per tier), personal app

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Content Isolation | PASS | Templates are defined per-tier in TierConfig. Kids templates are age-appropriate. No cross-tier access. |
| II. Local-First | PASS | Templates are static data embedded in the app — no external service dependency. |
| III. Iterative Simplicity | PASS | Templates reuse existing TierConfig pattern. No new models, no database, no admin UI. Simple dataclass + Jinja2 rendering. |
| IV. Archival by Design | PASS | Not applicable — templates are configuration, not generated content. Stories started from templates are saved normally. |
| V. Fun Over Perfection | PASS | Static config over database. Emoji icons over image assets. Simple JS form-filling over complex state management. |

**Post-design re-check**: All 5 principles PASS.

## Project Structure

### Documentation (this feature)

```text
specs/015-story-templates/
├── plan.md              # This file
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output (no new routes — N/A)
└── tasks.md             # Phase 2 output (created by /speckit.tasks)
```

### Source Code (new and modified files)

```text
app/
└── tiers.py             # MODIFIED: Add StoryTemplate dataclass, replace suggestions with templates

templates/
└── home.html            # MODIFIED: Replace suggestion chips with template cards grid

static/
├── css/
│   └── style.css        # MODIFIED: Add template card styles
└── js/
    └── app.js           # MODIFIED: Add template selection JS (form pre-fill, highlight)
```

**Structure Decision**: No new files needed. All changes are modifications to existing files. Templates are defined as a list of dataclass instances on TierConfig, rendered by Jinja2 in home.html, with client-side JS handling selection/pre-fill.

## File Change Map

| File | Action | Purpose |
|------|--------|---------|
| `app/tiers.py` | MODIFY | Add `StoryTemplate` dataclass with title, description, emoji, prompt, length. Replace `suggestions: list[str]` with `templates: list[StoryTemplate]` on TierConfig. Define 6 templates per tier. |
| `templates/home.html` | MODIFY | Replace suggestion chips section with template cards grid. Add `data-*` attributes for JS form filling. Add selected state handling. |
| `static/css/style.css` | MODIFY | Add `.template-grid`, `.template-card`, `.template-card.selected` styles. Remove `.prompt-suggestions`, `.suggestion-chip` styles (or leave for backward compat if referenced elsewhere). |
| `static/js/app.js` | MODIFY | Add `selectTemplate(el)` function that reads data attributes and pre-fills prompt + length. Add `clearTemplate()` to deselect. |
