# Implementation Plan: Chapter Stories

**Branch**: `046-chapter-stories` | **Date**: 2026-02-08 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/046-chapter-stories/spec.md`

## Summary

Add a new "Epic" story length (~25 scenes across 5 chapters) with chapter title cards, multi-session save/resume with a "Continue Chapter N" home page prompt, and chapter-aware gallery display. Builds on the existing depth-based pacing system with minimal model changes — chapter metadata (number/title) stored on scenes, chapter boundaries detected by depth modulo arithmetic.

## Technical Context

**Language/Version**: Python 3.11+ (matches existing project)
**Primary Dependencies**: FastAPI, Jinja2, Pydantic, anthropic SDK, openai SDK (all existing — no new dependencies)
**Storage**: JSON flat files (existing `data/progress/`, `data/stories/`)
**Testing**: pytest (existing test suite, 413 tests)
**Target Platform**: Linux server (Docker on NUC), dev on macOS
**Project Type**: Web application (FastAPI + Jinja2 templates)
**Performance Goals**: Scene generation latency unchanged; chapter title cards render instantly (no AI call)
**Constraints**: Must not regress existing short/medium/long story flows
**Scale/Scope**: Single-user home LAN app

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Content Isolation | PASS | Chapter stories use the same tier-scoped routing. No cross-tier access. |
| II. Local-First | PASS | No new external dependencies. Chapter metadata stored in local JSON files. Stories browsable offline. |
| III. Iterative Simplicity | PASS | Adds one new enum value (EPIC), 2 optional fields on Scene/SavedScene, and template-level chapter title rendering. No new abstractions. |
| IV. Archival by Design | PASS | Chapter metadata preserved in SavedStory JSON. Gallery reader shows chapter breaks. Full branching structure kept. |
| V. Fun Over Perfection | PASS | Straightforward extension of existing depth system. No over-engineering. |

## Design Decisions

### D1. How chapters map to scenes

**Decision**: Chapter N covers scenes at depths `(N-1)*5` through `N*5-1`. A 5-chapter epic story has `target_depth=25`. Chapter boundaries are detected with `depth % 5 == 0 and depth > 0`.

**Rationale**: Reuses the existing `depth` field. No new "chapter" entity needed. The AI prompt already tracks `current_depth` and `target_depth` — just needs chapter-awareness added.

**Alternatives rejected**: Separate Chapter model with nested scenes (over-engineered), variable chapter lengths (harder to predict pacing).

### D2. How chapter title cards work

**Decision**: Add `chapter_number: Optional[int]` and `chapter_title: Optional[str]` fields to `Scene` and `SavedScene`. When a scene starts a new chapter (depth is a multiple of 5, or depth==0 for chapter 1), the AI includes a `chapter_title` in its JSON response. The template renders a chapter title card header above the scene content when these fields are present.

**Rationale**: No extra scenes in the graph. Title card is a visual overlay on the first scene of each chapter. Preserved in gallery via the SavedScene fields. Tree-map can show chapter titles as labels.

**Alternatives rejected**: Separate title-card Scene objects (complicates depth counting and choice flow), pure UI overlay without persistence (lost in gallery export).

### D3. AI prompt changes for chapter structure

**Decision**: Extend `SYSTEM_PROMPT` with chapter-aware pacing. When story length is "epic", add instructions like "You are writing Chapter 2 of 5. This chapter should develop [subplot] while advancing the overarching narrative." Include a `chapter_title` field in the JSON output format. The AI generates a chapter title when `is_chapter_start` is true.

**Rationale**: The AI already receives `current_depth` and `target_depth`. Adding chapter context helps it structure 25-scene stories with proper narrative arcs per chapter.

### D4. Separate save slot for chapter stories

**Decision**: Save chapter story progress to `data/progress/{tier}_chapter.json` (separate from the regular `data/progress/{tier}.json`). The home page checks both files and shows both resume banners if both exist.

**Rationale**: Spec requires FR-008 (chapter resume must not interfere with regular resume) and FR-008 (both resumable simultaneously). Separate files are the simplest approach — no changes to the existing progress system.

### D5. "Continue Chapter N" home page banner

**Decision**: Add a second resume banner below the existing one. Compute current chapter number from `len(path_history) // 5 + 1` (or from the chapter_number field on the current scene). Show story title, chapter number, and continue/abandon buttons.

**Rationale**: Reuses the existing resume banner pattern. Two banners (regular + chapter) can coexist without interference.

### D6. Gallery chapter display

**Decision**: Add chapter count to gallery card metadata (e.g., "5 Chapters"). In the reader, render chapter title cards inline just as during play. Add a chapter jump dropdown/links in the reader navigation.

**Rationale**: Minimal template changes. Chapter boundaries are detectable from SavedScene `chapter_number` fields.

### D7. StoryLength enum extension

**Decision**: Add `EPIC = "epic"` with `target_depth=25` and description "Epic saga (~5 chapters, ~25 scenes)". The existing short/medium/long remain unchanged.

**Rationale**: Follows the existing pattern exactly. All downstream code (pacing, keep-going, wrap-up) works with any target_depth value.

## Project Structure

### Documentation (this feature)

```text
specs/046-chapter-stories/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
└── tasks.md             # Phase 2 output (created by /speckit.tasks)
```

### Source Code (repository root)

```text
app/
├── models.py            # Add EPIC to StoryLength, chapter fields to Scene/SavedScene
├── services/
│   ├── story.py         # Chapter-aware SYSTEM_PROMPT, chapter_title in JSON output
│   └── gallery.py       # save_chapter_progress(), load_chapter_progress() methods
├── routes.py            # Epic story start, chapter resume, chapter abandon, gallery chapter display
templates/
├── home.html            # EPIC length radio, chapter story resume banner
├── scene.html           # Chapter title card rendering above scene content
├── gallery.html         # Chapter count on story cards
├── reader.html          # Chapter title cards in reader, chapter jump navigation
static/css/
└── style.css            # Chapter title card styling
tests/
└── test_chapter.py      # Chapter story tests (optional, if time)
```

**Structure Decision**: Extends existing files. No new modules or services.
