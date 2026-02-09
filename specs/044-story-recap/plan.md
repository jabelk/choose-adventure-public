# Implementation Plan: Story Recap / "Previously On..."

**Branch**: `044-story-recap` | **Date**: 2026-02-08 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/044-story-recap/spec.md`

## Summary

Add an AI-generated "Story so far" recap section to scene pages. The recap appears as a single collapsible section at scene depth 2+. It auto-expands when resuming a saved story, stays collapsed during active play. Recaps are generated on-demand via AJAX, cached in-memory on the session, and adapt language to the tier's content guidelines. No new dependencies.

## Technical Context

**Language/Version**: Python 3.11+ (same as existing project)
**Primary Dependencies**: FastAPI, Jinja2, Pydantic, anthropic SDK, openai SDK, google-genai SDK (all existing — no new pip dependencies)
**Storage**: In-memory session cache (`StorySession.recap_cache` dict) — no disk persistence needed
**Testing**: pytest (`venv/bin/python -m pytest tests/ -v --ignore=tests/test_browser.py`)
**Target Platform**: Self-hosted web app on Intel NUC, accessed via LAN browsers
**Project Type**: Web application (server-rendered with client-side AJAX)
**Performance Goals**: Recap loads within 3 seconds; cached recaps under 500ms; scene page never blocked
**Constraints**: No page load delay for recap generation; graceful degradation when AI unavailable
**Scale/Scope**: Single-user home server; stories up to ~20 scenes; 3 tiers (kids, nsfw, bible)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Content Isolation | PASS | Recap uses tier-specific content guidelines. Each tier generates recaps independently. No cross-tier data sharing. |
| II. Local-First | PASS | Recap is generated via the same AI APIs already used for story generation. Graceful degradation when APIs unavailable — page loads normally, recap shows fallback. |
| III. Iterative Simplicity | PASS | Minimal implementation: one new model field, one new endpoint, one JS function, one template section. No new services or abstractions. |
| IV. Archival by Design | PASS | Recaps are ephemeral (session-scoped cache). They don't need archival — the scene content they summarize is already archived. |
| V. Fun Over Perfection | PASS | Solves a real usability problem (forgetting story context) with minimal code. Enhances the reading experience. |

## Design Decisions

### D1: Recap Generation Method

**Decision**: Add a `generate_recap()` method to `StoryService` that calls the existing `_call_provider()` dispatcher with a recap-specific system prompt.

**Rationale**: Reuses the existing multi-model AI infrastructure. The recap uses the same model as the story, ensuring consistent voice. No new service class needed.

### D2: Resume Detection via Query Parameter

**Decision**: Add `?resumed=1` query parameter to the redirect URL in the `resume_story()` route. The scene view handler checks for this parameter and passes `recap_expanded=True` to the template.

**Rationale**: Simplest approach — no model changes, no session mutation, automatically clears on next navigation. The query parameter is transient by design.

### D3: Async Recap Loading via AJAX

**Decision**: Scene page renders immediately with a placeholder. Client-side JavaScript fetches `GET /{tier}/story/recap/{scene_id}` which returns JSON with the recap text. The endpoint checks the cache first, generates on-demand if needed.

**Rationale**: Consistent with existing async patterns (image polling, TTS). Never blocks page load. Cache makes subsequent loads instant.

### D4: Cache Keying by Path History

**Decision**: Cache key is `"|".join(path_history[:depth+1])` — the ordered scene IDs from root to current scene. Stored in `StorySession.recap_cache: dict[str, str]`.

**Rationale**: Automatically invalidates when the user goes back and takes a different branch (the path changes, producing a different key). No explicit invalidation logic needed.

### D5: Tier-Appropriate Recap Prompts

**Decision**: Include `tier_config.content_guidelines` in the recap system prompt. Add a short recap-specific instruction (e.g., "Summarize in 2-3 sentences using simple words" for kids, "Preserve the story's tone" for NSFW).

**Rationale**: The content guidelines already encode tier-appropriate language rules. Adding a recap-specific instruction on top ensures the right format and length.

### D6: Graceful Degradation

**Decision**: If recap generation fails (AI unavailable, timeout, error), the AJAX endpoint returns `{"status": "error"}`. The client JS hides the recap section entirely rather than showing an error message.

**Rationale**: The recap is a convenience feature. Showing an error for it would be worse than showing nothing. The story page is fully functional without it.

### D7: Collapsible UI with Persistent State

**Decision**: The recap section is a `<details>` element (or div with JS toggle). The `open` attribute is controlled by: (a) `recap_expanded` template variable (true on resume, false on active play), (b) user interaction (click to toggle). State is per-page-load only — not persisted.

**Rationale**: Simplest implementation. The `<details>` HTML element provides native collapse/expand with no JS required for basic functionality. JS enhances it with async loading on first expand.

## Project Structure

### Documentation (this feature)

```text
specs/044-story-recap/
├── spec.md
├── plan.md              # This file
├── research.md
├── data-model.md
├── quickstart.md
├── checklists/
│   └── requirements.md
└── tasks.md             # Created by /speckit.tasks
```

### Source Code (modified files)

```text
app/
├── models.py            # Add recap_cache field to StorySession
├── routes.py            # Add recap endpoint, resume query param, template context
└── services/
    └── story.py         # Add generate_recap() method

templates/
└── scene.html           # Add collapsible recap section

static/
├── css/style.css        # Recap section styling
└── js/app.js            # Recap fetch + toggle logic

tests/
└── test_recap.py        # New test file
```

**Structure Decision**: All changes are modifications to existing files plus one new test file. No new services, models, or infrastructure. Follows the established pattern of adding features within `create_tier_router()` in `routes.py`.
