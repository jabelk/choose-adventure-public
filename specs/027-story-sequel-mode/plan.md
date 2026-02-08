# Implementation Plan: Story Sequel Mode

**Branch**: `027-story-sequel-mode` | **Date**: 2026-02-07 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/027-story-sequel-mode/spec.md`

## Summary

Add a "Continue Story" button to the gallery reader page that lets users start a sequel from any completed story. The sequel inherits the original story's characters, kinks, art style, model selections, and other settings, and uses the original ending scene as AI context to generate a continuation. Three priority tiers: P1 (core sequel launch), P2 (pre-launch customization form), P3 (sequel chain visibility in gallery).

## Technical Context

**Language/Version**: Python 3.14 (existing project)
**Primary Dependencies**: FastAPI, Jinja2, Pydantic, anthropic SDK, openai SDK
**Storage**: JSON flat files in `data/stories/` (existing gallery storage)
**Testing**: pytest with mocked AI services (existing pattern)
**Target Platform**: Self-hosted web app on LAN (Intel NUC)
**Project Type**: Web application (FastAPI + Jinja2 templates)
**Performance Goals**: Standard web app response times
**Constraints**: No external dependencies for browsing/reading
**Scale/Scope**: Single-user hobby project

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Content Isolation | PASS | Sequels are tier-locked (FR-007, FR-011). The `continue_story` route runs inside `create_tier_router()` so it's automatically scoped to the correct tier. Cross-tier sequels are prevented by checking `saved.tier == tier_config.name`. |
| II. Local-First | PASS | No new cloud dependencies. Sequel metadata stored in existing JSON files. AI APIs only called for scene generation (same as existing flow). |
| III. Iterative Simplicity | PASS | P1 is minimal — one new route, one button, field carryover. P2/P3 add complexity only when P1 is validated. No new abstractions needed; follows existing patterns. |
| IV. Archival by Design | PASS | Sequel stories are saved to the gallery like any other story. Parent-child relationships stored as IDs in the JSON, browsable through the existing gallery. |
| V. Fun Over Perfection | PASS | Feature is fun-focused (more stories!). Implementation reuses existing route patterns. No over-engineering. |

All gates pass. No violations to track.

## Project Structure

### Documentation (this feature)

```text
specs/027-story-sequel-mode/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── spec.md              # Feature specification
├── checklists/
│   └── requirements.md  # Spec quality checklist
└── tasks.md             # Phase 2 output (created by /speckit.tasks)
```

### Source Code (modified files)

```text
app/
├── models.py            # Add parent_story_id, sequel_story_ids, sequel_context fields
├── routes.py            # Add continue_story route (P1), sequel_customize route (P2), update reader context (P3)
└── services/
    └── gallery.py       # Fix save_story to persist all Story fields; add update_sequel_links helper (P3)

templates/
├── reader.html          # Add "Continue Story" button (P1), sequel chain nav (P3)
└── sequel_customize.html # New template for P2 customization form

static/css/
└── style.css            # Sequel button and chain nav styles

tests/
└── test_sequel_mode.py  # New test file
```

**Structure Decision**: All changes fit within the existing project structure. One new template file (`sequel_customize.html`) for P2. No new services or modules needed.

## Implementation Approach

### P1: Core Sequel Launch (MVP)

1. **Model changes**: Add `parent_story_id: Optional[str] = None` and `sequel_context: str = ""` to `Story`. Add `parent_story_id: Optional[str] = None` and `sequel_story_ids: list[str] = []` to `SavedStory`.

2. **Fix `save_story`**: The current `gallery.save_story()` doesn't persist `art_style`, `protagonist_gender/age`, `character_type`, `num_characters`, `writing_style`, `conflict_type`, `roster_character_ids`, `bedtime_mode`, or `parent_story_id`. Fix this to persist all fields (prerequisite for sequel carryover).

3. **New route `POST /gallery/{story_id}/continue`**: Loads the SavedStory, extracts the ending scene, builds a new Story with inherited fields, generates the opening scene with sequel context, creates a new StorySession, and redirects to the first scene.

4. **Sequel context prompt**: When generating the sequel's opening scene, prepend the original ending content as context with an instruction: "SEQUEL CONTEXT: The following is how the previous story ended. Continue the narrative from this point with a new plot thread while maintaining the same characters and world."

5. **Reader template**: Add a "Continue Story" button in the `reader-nav` div, next to the export buttons.

### P2: Customization Form

1. **New template `sequel_customize.html`**: Form pre-filled with inherited settings (length, kinks, model, art style). Includes a "sequel prompt" textarea for the user to hint at the sequel direction.

2. **Route split**: The "Continue Story" button goes to a GET route that renders the customization form. The form POSTs to a new route that creates the sequel session.

### P3: Sequel Chain Visibility

1. **Forward references**: When a sequel is saved to the gallery, update the parent story's JSON to add the sequel's story_id to `sequel_story_ids`.

2. **Reader nav**: Show "Sequel of: [title]" link when `parent_story_id` is set, and "Continued in: [title]" links when `sequel_story_ids` is non-empty.

## Key Design Decisions

1. **Sequel context is last scene only** — not the full story. Keeps AI context manageable and avoids token limits.

2. **Sequels are independent stories** — they get their own story_id, own gallery entry, own scenes. They just happen to have a `parent_story_id` linking back.

3. **Field inheritance happens at sequel creation time** — we copy fields from SavedStory to a new Story. If the user later edits a roster character, it doesn't retroactively change existing sequels.

4. **Fix `save_story` as a prerequisite** — this is a bug fix that benefits all features, not just sequels. Several Story fields aren't being persisted to SavedStory.
