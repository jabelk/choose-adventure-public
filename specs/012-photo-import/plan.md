# Implementation Plan: Photo Import

**Branch**: `012-photo-import` | **Date**: 2026-02-07 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/012-photo-import/spec.md`

## Summary

Add the ability for users to upload reference photos for characters in their profiles. When memory mode is active, these photos are passed to the AI image generation APIs (OpenAI `images.edit` with `input_fidelity="high"`, Gemini with `inline_data`) so generated story images feature characters that visually resemble the real people in the uploaded photos. Photos are stored locally on disk, tier-isolated, and cleaned up on character/profile deletion.

## Technical Context

**Language/Version**: Python 3.14 (managed with pip/venv)
**Primary Dependencies**: FastAPI, Jinja2, Pydantic, anthropic SDK, openai SDK, google-genai SDK, Pillow (NEW — for image dimension validation)
**Storage**: Local filesystem (JSON + image files in `data/`)
**Testing**: Manual testing via quickstart.md
**Target Platform**: Intel NUC home server (LAN-only), development on macOS
**Project Type**: Web application (server-rendered templates)
**Performance Goals**: Photo upload + thumbnail display < 10 seconds
**Constraints**: Max 5 MB per photo, JPEG/PNG only, one photo per character
**Scale/Scope**: Personal use, ~10 profiles, ~100 characters max

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Content Isolation | PASS | Photos stored in `data/photos/{tier}/`, served via tier-scoped routes. No cross-tier access possible. |
| II. Local-First | PASS | Photos stored on local disk. External AI APIs used only for generation (existing pattern). App remains functional for browsing when APIs are unreachable. |
| III. Iterative Simplicity | PASS | Minimal new dependency (Pillow for dimension check). Extends existing models/services rather than creating new abstractions. No over-engineering. |
| IV. Archival by Design | PASS | Photos persist on disk alongside profiles. Not dependent on interactive story flow. |
| V. Fun Over Perfection | PASS | Simple file upload UX, no fancy cropping/editing tools. Gets to the fun part (personalized images) fast. |

**Post-design re-check**: All principles still PASS. One new dependency (Pillow) is justified for image dimension validation — it's a standard Python library and the only alternative is reading raw file headers manually.

## Project Structure

### Documentation (this feature)

```text
specs/012-photo-import/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/
│   └── routes.md        # Phase 1 output
└── tasks.md             # Phase 2 output (created by /speckit.tasks)
```

### Source Code (repository root)

```text
app/
├── models.py            # MODIFIED — add photo_path to Character
├── services/
│   ├── image.py         # MODIFIED — add reference_images parameter, images.edit support
│   ├── profile.py       # MODIFIED — photo CRUD methods, build_profile_context returns photo paths
│   └── ...
├── routes.py            # MODIFIED — photo upload/delete/serve routes, pass reference_images to image generation
└── config.py            # No changes needed

data/
└── photos/              # NEW — reference photo storage
    ├── kids/
    │   └── {profile_id}/
    │       └── {character_id}.{ext}
    └── nsfw/
        └── {profile_id}/
            └── {character_id}.{ext}

templates/
└── profile_edit.html    # MODIFIED — photo upload form, thumbnail display, remove button

static/
└── css/
    └── style.css        # MODIFIED — photo thumbnail and upload form styles
```

**Structure Decision**: Extends existing project structure. No new directories in `app/` — photo handling is added to the existing `ProfileService` and `ImageService`. Photo files live in `data/photos/` following the same tier-scoped pattern as `data/profiles/`.

## Key Implementation Details

### OpenAI images.edit Integration

The current `_generate_dalle()` method uses `images.generate`. When reference images are provided, we switch to `images.edit`:

```python
# With reference images:
response = await self.openai_client.images.edit(
    model="gpt-image-1",
    image=image_files,        # list of file objects
    prompt=prompt,
    input_fidelity="high",    # preserve facial likeness
    size="1024x1024",
)

# Without reference images (unchanged):
response = await self.openai_client.images.generate(
    model="gpt-image-1",
    prompt=prompt,
    n=1,
    size="1024x1024",
)
```

### Gemini Reference Image Integration

Gemini's `generate_content` supports mixed content (text + images):

```python
contents = [
    genai.types.Part(inline_data=genai.types.Blob(mime_type="image/jpeg", data=photo_bytes)),
    f"Generate an image incorporating the person from the reference photo: {prompt}",
]
```

### Profile Context Builder Extension

`build_profile_context()` currently returns `tuple[str, str]` (content_addition, image_style_addition). It will be extended to return `tuple[str, str, list[str]]` — the third element is a list of absolute photo file paths for characters that have photos (including cross-profile linked characters, one level deep).

## Complexity Tracking

No constitution violations. No complexity justification needed.
