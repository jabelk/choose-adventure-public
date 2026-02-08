# Tasks: Story Templates

**Input**: Design documents from `/specs/015-story-templates/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), data-model.md, quickstart.md

**Tests**: No tests requested in the feature specification. Manual testing via quickstart.md.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Define the StoryTemplate dataclass and add template data to tier configuration.

- [X] T001 Add StoryTemplate dataclass to app/tiers.py — define a dataclass with fields: `title` (str), `description` (str), `emoji` (str), `prompt` (str), `length` (str, default "medium"). Replace the `suggestions: list[str]` field on TierConfig with `templates: list[StoryTemplate]` (default empty list).
- [X] T002 Define 6 kids tier templates in app/tiers.py — add a list of 6 StoryTemplate instances to the kids TierConfig. Genres: animal adventure, fairy tale, space exploration, underwater quest, forest mystery, superhero origin. Each template needs a catchy title, 1-2 sentence description, emoji, full prompt text (2-3 sentences), and suggested length.
- [X] T003 Define 6 adult tier templates in app/tiers.py — add a list of 6 StoryTemplate instances to the nsfw TierConfig. Genres: noir detective, horror survival, sci-fi thriller, fantasy epic, political intrigue, post-apocalyptic journey. Each template needs a title, description, emoji, prompt, and suggested length.

---

## Phase 2: User Story 1 — Browse and Start from a Template (Priority: P1)

**Goal**: Users see template cards on the home page, click one to pre-fill the form, and start a story.

**Independent Test**: Load home page, click a template, verify form pre-fills, submit to start a story.

### Implementation for User Story 1

- [X] T004 [P] [US1] Add template card CSS to static/css/style.css — add styles for `.template-grid` (responsive grid, 2 columns on desktop, 1 on mobile), `.template-card` (clickable card with emoji, title, description, border, hover effect), `.template-card.selected` (highlighted state with accent border and background). Cards should have `cursor: pointer`, `min-height: 44px` for touch targets, and transition effects.
- [X] T005 [P] [US1] Add template selection JavaScript to static/js/app.js — add a `selectTemplate(card)` function that: (1) reads `data-prompt` and `data-length` attributes from the clicked card, (2) fills the prompt textarea, (3) sets the matching length radio button, (4) toggles `.selected` class on the card (removing it from siblings), (5) if clicking an already-selected card, clears the form and deselects. Also add a `clearTemplate()` helper.
- [X] T006 [US1] Update templates/home.html to display template cards — add a `.template-grid` section above the prompt form (after the resume banner, before the form). Render each template from `tier.templates` as a `.template-card` div with `data-prompt` and `data-length` attributes. Each card shows the emoji, title, and description. Wire up `onclick="selectTemplate(this)"`.
- [X] T007 [US1] Pass templates to the home template context — in app/routes.py, verify that `tier` is already passed to the home template context (it is via create_tier_router). No additional context variables needed since templates are accessed via `tier.templates` in Jinja2.

---

## Phase 3: User Story 2 — Tier-Specific Template Collections (Priority: P2)

**Goal**: Each tier has its own curated templates matching its audience.

**Independent Test**: Load kids home page and adult home page, verify completely different template sets.

### Implementation for User Story 2

- [X] T008 [US2] Verify tier isolation of templates — this is handled by the data definition in T002 and T003 (each tier has its own template list on TierConfig). The Jinja2 template renders `tier.templates` which is automatically scoped. No additional code needed — just verify by loading both tier home pages.

---

## Phase 4: User Story 3 — Template Replaces Suggestion Chips (Priority: P3)

**Goal**: Remove suggestion chips, templates serve as the sole inspiration source.

**Independent Test**: Load home page, verify no suggestion chips section.

### Implementation for User Story 3

- [X] T009 [US3] Remove suggestion chips from templates/home.html — delete the `.prompt-suggestions` section (the "Need inspiration?" block with suggestion chip buttons). Templates now serve this purpose.
- [X] T010 [US3] Remove suggestions field from TierConfig in app/tiers.py — remove the `suggestions: list[str]` field from TierConfig and the suggestion data from both tier definitions (since templates replace them). Update any references.
- [X] T011 [US3] Clean up suggestion chip CSS from static/css/style.css — remove or comment out `.prompt-suggestions`, `.suggestions-label`, `.suggestions`, `.suggestion-chip` styles since they are no longer used.

---

## Phase 5: Polish & Verification

**Purpose**: Final validation and edge case handling.

- [X] T012 Verify the full quickstart.md flow (all 9 steps) — load the app, test template selection, deselection, form modification, story start, tier isolation, mobile responsiveness.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — can start immediately
- **User Story 1 (Phase 2)**: Depends on Setup (T001-T003 — template data must exist)
- **User Story 2 (Phase 3)**: Depends on Setup (T002-T003 — tier templates must be defined)
- **User Story 3 (Phase 4)**: Can start after US1 is complete (templates must be working before removing chips)
- **Polish (Phase 5)**: Depends on all user stories being complete

### Parallel Opportunities

- T004 and T005 can run in parallel (CSS vs JS — different files)
- T002 and T003 can run in parallel (different tiers — same file but different sections)
- T009, T010, T011 affect different files but T010 should come before T009 (remove data before template reference)

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- No new pip dependencies — all changes are to existing files
- Templates are static config, no database or file storage needed
- The `tier` object is already available in Jinja2 templates via `create_tier_router` context
- Commit after each phase completion
