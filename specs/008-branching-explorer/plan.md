# Implementation Plan: Story Branching Explorer

**Branch**: `008-branching-explorer` | **Date**: 2026-02-07 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/008-branching-explorer/spec.md`

## Summary

Add story branching and a visual tree map to the choose-your-own-adventure
app. Users can go back to any choice point and pick a different option,
generating a new branch while preserving the original. A collapsible tree
map (rendered with D3.js) shows all explored branches during active play
and in the gallery reader. Explored choices are visually marked. The
gallery reader changes from index-based to scene-ID-based navigation to
support branching. All explored branches are saved to gallery and preserved
in progress files. No data model changes needed — the existing Scene
parent-child structure already forms a tree.

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**: FastAPI, Jinja2, Pydantic, D3.js v7 (vendored)
**Storage**: JSON flat files (stories in `data/stories/`, progress in `data/progress/`)
**Testing**: Manual testing via quickstart guide
**Target Platform**: Linux (Intel NUC) + macOS (development), served via LAN
**Project Type**: Web application (server-rendered)
**Performance Goals**: Tree map renders 10-30 nodes instantly. D3 layout is O(n).
**Constraints**: Single-user, LAN-only, no build tools, no npm
**Scale/Scope**: Personal app, 1 concurrent user, trees of 10-30 nodes

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Content Isolation | PASS | Tree map and branching scoped to each tier. No cross-tier access. |
| II. Local-First | PASS | D3.js vendored locally. No CDN dependency. Tree rendering is client-side. |
| III. Iterative Simplicity | PASS | No new abstractions. Reuses existing scene dict and parent-child links. D3.js is the only new dep, vendored as a single file. |
| IV. Archival by Design | PASS | All explored branches are saved to gallery. Tree map in reader makes the archive truly explorable. This directly fulfills the constitution's requirement to "preserve the full branching structure." |
| V. Fun Over Perfection | PASS | Interactive tree visualization is the fun part. D3 handles the hard layout math. |

## Project Structure

### Documentation (this feature)

```text
specs/008-branching-explorer/
├── plan.md              # This file
├── spec.md              # Feature specification
├── research.md          # Phase 0: 7 design decisions
├── data-model.md        # Model analysis (no changes needed)
├── quickstart.md        # 10-step manual testing guide
├── contracts/
│   └── routes.md        # New + modified routes and template changes
└── tasks.md             # Phase 2 output (created by /speckit.tasks)
```

### Source Code (repository root)

```text
app/
├── models.py            # Add navigate_to() method to StorySession
├── routes.py            # New navigate + tree routes, modify scene/gallery routes
└── tree.py              # NEW: Tree building helper (scenes dict → nested tree)

templates/
├── scene.html           # Add tree map toggle, explored choice indicators
├── reader.html          # Replace linear nav with tree map, scene-ID URLs
└── base.html            # Add D3.js script tag

static/
├── js/
│   ├── d3.v7.min.js     # NEW: Vendored D3.js v7
│   └── tree-map.js      # NEW: Tree map rendering component
└── css/
    └── style.css        # Tree map and explored choice styles
```

**Structure Decision**: This feature modifies the existing web application
structure. Two new files are created: `app/tree.py` (tree building helper)
and `static/js/tree-map.js` (D3 tree rendering). D3.js is vendored as a
single file. All other changes are modifications to existing files.

## Complexity Tracking

No constitution violations. No complexity justifications needed.
