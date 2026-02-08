# Research: Mid-Story Length Control

**Feature**: 025-mid-story-length
**Date**: 2026-02-08

## Decision 1: Route Design (POST with redirect vs AJAX)

**Decision**: Simple POST forms that redirect back to the same scene.

**Rationale**: The spec explicitly states "simple buttons, no settings or configuration needed" and "POST actions that redirect back to the current scene — no AJAX or dynamic UI needed." This matches the existing pattern used for Go Back, Make Choice, and other story navigation.

**Alternatives considered**:
- AJAX with JSON response: More complex, requires JS, no user benefit for a single button click.
- GET with query parameter: Not appropriate for state mutation (violates HTTP semantics).

## Decision 2: Button Placement in Template

**Decision**: Add buttons between the scene content and the choice section, inside the non-ending `{% else %}` block.

**Rationale**: The buttons control story pacing and are related to navigation flow. Placing them near the choices keeps the user's attention in the action area. They must be hidden on ending scenes (handled by being inside `{% else %}`).

**Alternatives considered**:
- In the scene header: Too far from the action area; header is for metadata.
- Below choices: Could be overlooked after the user has already chosen.

## Decision 3: Depth Value Access in Template

**Decision**: Use existing `scene.depth` and `story.target_depth` already passed to the template via the `view_scene` route context.

**Rationale**: Both values are already available in the template context. `scene.depth` is an integer on the Scene model, `story.target_depth` is on the Story model. No new context variables needed.

**Alternatives considered**:
- Compute visibility server-side and pass boolean flags: Unnecessary abstraction; Jinja2 can handle simple comparisons.
