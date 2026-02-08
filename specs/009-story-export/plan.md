# Implementation Plan: Story Export

**Branch**: `009-story-export` | **Date**: 2026-02-07 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/009-story-export/spec.md`

## Summary

Add export functionality to the gallery so users can download completed
stories as self-contained HTML files (with embedded images and interactive
tree navigation) or as PDF documents (with images, branch-organized layout,
and tree diagram). The HTML export builds a single-file page with inline
D3.js and base64-encoded images. The PDF export uses fpdf2 to generate a
document with scenes organized by branch. A new export service handles
image embedding and content assembly for both formats. Export buttons
appear on gallery cards and in the gallery reader.

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**: FastAPI, Jinja2, Pydantic, fpdf2 (new — PDF generation)
**Storage**: JSON flat files (stories in `data/stories/`, images in `static/images/`)
**Testing**: Manual testing via quickstart guide
**Target Platform**: Linux (Intel NUC) + macOS (development), served via LAN
**Project Type**: Web application (server-rendered)
**Performance Goals**: HTML export < 5 seconds, PDF export < 10 seconds for typical stories
**Constraints**: Single-user, LAN-only, no build tools, no npm, no system-level deps for PDF
**Scale/Scope**: Personal app, 1 concurrent user, stories with 5-20 scenes

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Content Isolation | PASS | Export routes scoped to each tier. No cross-tier access. Export files contain only the requesting tier's content. |
| II. Local-First | PASS | fpdf2 is pure Python, no cloud dependency. Images read from local disk. HTML export is fully self-contained. |
| III. Iterative Simplicity | PASS | One new service file, one new dependency (fpdf2). Reuses existing gallery service and tree builder. No new abstractions. |
| IV. Archival by Design | PASS | This feature directly fulfills archival goals — makes stories portable and shareable as standalone files. |
| V. Fun Over Perfection | PASS | Two pragmatic formats (HTML + PDF). No over-engineering with templates or customization. |

## Project Structure

### Documentation (this feature)

```text
specs/009-story-export/
├── plan.md              # This file
├── spec.md              # Feature specification
├── research.md          # Phase 0: 5 design decisions
├── data-model.md        # Model analysis (no changes needed)
├── quickstart.md        # 8-step manual testing guide
├── contracts/
│   └── routes.md        # New routes and template changes
└── tasks.md             # Phase 2 output (created by /speckit.tasks)
```

### Source Code (repository root)

```text
app/
├── routes.py            # New export routes (HTML + PDF download)
└── services/
    └── export.py        # NEW: Export service (HTML builder + PDF builder)

templates/
├── gallery.html         # Add export buttons on story cards
├── reader.html          # Add export button in reader view
└── export.html          # NEW: Jinja2 template for self-contained HTML export

static/
└── css/
    └── style.css        # Export button styles
```

**Structure Decision**: This feature modifies the existing web application
structure. One new source file is created: `app/services/export.py` (export
logic for both formats). One new template: `templates/export.html` (the
self-contained HTML file template). fpdf2 is the only new dependency.

## Complexity Tracking

No constitution violations. No complexity justifications needed.
