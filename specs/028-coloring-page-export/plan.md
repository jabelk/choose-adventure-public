# Implementation Plan: Coloring Page Export

**Branch**: `028-coloring-page-export` | **Date**: 2026-02-07 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/028-coloring-page-export/spec.md`

## Summary

Add a "Coloring Page" button to the gallery reader that generates a black-and-white line-art version of any scene image. Uses the existing image generation service with a coloring page style override prompt. Provides PNG download directly and PDF download via fpdf2 (already a dependency). Available on both tiers.

## Technical Context

**Language/Version**: Python 3.14 (existing project)
**Primary Dependencies**: FastAPI, Jinja2, fpdf2 (already used for story PDF export), anthropic/openai SDKs (image generation)
**Storage**: Static files on disk at `static/images/` (PNG), no database
**Testing**: pytest with FastAPI TestClient (existing pattern)
**Target Platform**: Linux server (Intel NUC), development on macOS
**Project Type**: Web application (Python backend, Jinja2 templates)
**Performance Goals**: Coloring page generation under 30 seconds (limited by image API latency)
**Constraints**: Single image API call per coloring page, on-demand generation (no caching)
**Scale/Scope**: Single user, LAN-only

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Content Isolation | PASS | Feature uses existing tier-scoped gallery routes. No cross-tier access possible — routes already verify `saved.tier == tier_config.name`. |
| II. Local-First | PASS | Coloring pages require an external image API call (same as all image generation). Gallery browsing of already-generated coloring pages works offline since they're served as static PNGs. |
| III. Iterative Simplicity | PASS | Reuses existing image generation service and export pattern. No new dependencies, abstractions, or infrastructure. Single API call per coloring page. |
| IV. Archival by Design | PASS | Generated coloring pages are saved as static PNG files alongside original scene images. They persist with the story data. |
| V. Fun Over Perfection | PASS | Simple implementation — one button, one API call, two download formats. No over-engineering. |

All 5 gates pass. No violations to justify.

## Project Structure

### Documentation (this feature)

```text
specs/028-coloring-page-export/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── spec.md              # Feature specification
└── checklists/
    └── requirements.md  # Spec quality checklist
```

### Source Code (files modified/created)

```text
app/
├── routes.py                  # Add GET /gallery/{story_id}/{scene_id}/coloring endpoint
│                              # Add GET /gallery/{story_id}/{scene_id}/coloring/pdf endpoint
├── services/
│   └── image.py               # Add generate_coloring_page() method
│   └── export.py              # Add export_coloring_pdf() function
templates/
└── reader.html                # Add "Coloring Page" button + coloring page display area
static/
├── css/style.css              # Add coloring page UI styles
├── js/coloring-page.js        # Client-side button handler (fetch + display)
└── images/                    # Coloring PNGs saved as {scene_id}_coloring.png
tests/
└── test_coloring_page.py      # Tests for coloring page generation and download
```

**Structure Decision**: This feature adds to the existing project structure. No new directories needed. Coloring pages are stored alongside original scene images using the `{scene_id}_coloring.png` naming convention (matching the extra image pattern `{scene_id}_extra_{index}.png`).

## Implementation Approach

### Image Generation

The existing `ImageService.generate_image()` method generates images from a prompt + model. For coloring pages, we add a new method `generate_coloring_page()` that:

1. Takes a scene's `image_prompt` string
2. Prepends/replaces the style with: `"Simple black and white coloring page line art, thick outlines, no shading, no color, no grayscale, suitable for children to color in. Scene: {original_prompt}"`
3. Calls the same image generation backend (defaulting to gpt-image-1 or the story's image_model)
4. Saves the result as `static/images/{scene_id}_coloring.png`
5. Returns the URL path

### Route Design

Two new routes in the gallery section of `create_tier_router`:

1. **`GET /gallery/{story_id}/{scene_id}/coloring`** — Generates (if not already cached on disk) and returns the coloring page PNG as a file download. The JS button handler calls this via fetch, displays the result, and provides download links.

2. **`GET /gallery/{story_id}/{scene_id}/coloring/pdf`** — Takes the coloring PNG and wraps it in a single-page PDF using fpdf2 (same library as story export). Returns the PDF as a download.

### Client-Side Flow

1. User clicks "Coloring Page" button on scene image in gallery reader
2. Button shows loading state (disabled + spinner)
3. JavaScript fetches `GET .../coloring` endpoint
4. On success: displays the coloring image in a modal/overlay with "Download PNG" and "Download PDF" buttons
5. On error: shows error message with retry button
6. Download PNG: direct link to the generated image file
7. Download PDF: link to the `/coloring/pdf` endpoint

### PDF Generation

Use fpdf2 (already a dependency) to create a single-page PDF:
- US Letter paper (8.5" x 11" / 216mm x 279mm)
- Image centered with 20mm margins
- Scaled to fit page width (176mm) while maintaining aspect ratio
- No text, just the coloring page image
