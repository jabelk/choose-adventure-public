# Implementation Plan: Direct Image Upload

**Branch**: `019-direct-image-upload` | **Date**: 2026-02-07 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/019-direct-image-upload/spec.md`

## Summary

Add a "Reference Photos" upload field to the story start form so users can upload 1-3 images (JPEG/PNG, max 10MB each) directly without creating a profile. Uploaded photos are saved to a temporary directory, passed as `reference_images` to the image generator for every scene, and cleaned up when the story session ends. Works independently of the profile/memory mode system. Uses existing image generation pipeline which already supports reference images.

## Technical Context

**Language/Version**: Python 3.12
**Primary Dependencies**: FastAPI, Jinja2, python-multipart (already in project for profile photo uploads)
**Storage**: File-based — temporary uploads in `data/uploads/{session_id}/`, cleaned up on session end
**Testing**: Manual testing via browser (consistent with project approach)
**Target Platform**: Linux server (NUC) via Docker, macOS for local dev
**Project Type**: Web application (server-rendered templates)
**Performance Goals**: File upload and story start complete in under 5 seconds for 3 photos totaling 30MB
**Constraints**: No new dependencies, max 3 files, max 10MB per file, JPEG/PNG only
**Scale/Scope**: Modify story start form, route handler, and session model. Add temp file storage and cleanup.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Content Isolation | PASS | Upload field is added to the tier-scoped form template. Each tier's uploads are isolated via session ID. No cross-tier access. |
| II. Local-First | PASS | File uploads are stored locally on disk. No cloud storage or external services involved in the upload flow. |
| III. Iterative Simplicity | PASS | Reuses existing `reference_images` pipeline in image.py. No new abstractions — just file save, path tracking, and cleanup. Client-side thumbnails via FileReader API (no server processing). |
| IV. Archival by Design | PASS | Reference photos are temporary by design (per-session). They don't need archival — the generated story images are what get archived. |
| V. Fun Over Perfection | PASS | Simple file input with drag-and-drop. Client-side validation and previews. No complex upload library or image processing. |

No violations. No complexity tracking needed.

## Project Structure

### Documentation (this feature)

```text
specs/019-direct-image-upload/
├── plan.md              # This file
├── research.md          # Phase 0 output (minimal — no unknowns)
├── quickstart.md        # Phase 1 output
└── tasks.md             # Phase 2 output (/speckit.tasks command)
```

### Source Code (repository root)

```text
app/
├── routes.py            # MODIFY — add UploadFile parameter to start_story, save files, pass paths
├── models.py            # MODIFY — add reference_photo_paths field to Story model
├── session.py           # MODIFY — add cleanup hook for temp files on session delete
└── services/
    └── upload.py        # NEW — UploadService (save temp files, validate, cleanup)

templates/
└── home.html            # MODIFY — add Reference Photos upload area with drag-drop and previews

static/
└── js/
    └── upload.js        # NEW — client-side file validation, thumbnail previews, drag-drop
```

**Structure Decision**: Follows existing project conventions. A new `UploadService` in services handles file I/O (similar to how `ProfileService` handles character photos). The upload JS is separated into its own file to keep the template clean. Route changes go in the existing tier router factory since uploads are tier-scoped.

## Key Design Decisions

### 1. Temporary storage in data/uploads/{session_id}/

Uploaded files are saved to `data/uploads/{session_id}/` where session_id is the story's session UUID. This ties uploads to a specific story session and makes cleanup straightforward — delete the directory when the session ends.

### 2. Form encoding switch via JavaScript

The form starts as standard `application/x-www-form-urlencoded`. When files are selected, JavaScript sets `enctype="multipart/form-data"`. When all files are removed, it switches back. This preserves existing behavior for stories without uploads (FR-011).

### 3. Client-side thumbnail previews

Use the browser's `FileReader.readAsDataURL()` to generate thumbnail previews entirely client-side. No server round-trips for previews. Each thumbnail gets a remove button (X) that removes the file from the selection.

### 4. UploadService for file operations

A small service class that handles:
- **save_upload_files()**: Validate types/sizes, save to temp directory, return list of file paths
- **get_upload_paths()**: Get existing upload paths for a session
- **cleanup_session()**: Delete the temp directory for a session

### 5. Direct uploads override profile photos

When both direct uploads and memory mode profile photos exist, direct uploads take priority (FR-008). The route handler checks for direct uploads first and uses them if present, otherwise falls back to profile photos.

### 6. Cleanup triggers

Temp files are cleaned up in three scenarios:
- **Story completion**: When story is saved to gallery, delete temp uploads
- **New story start**: When user starts a new story in the same tier, delete previous session's uploads
- **Admin deletion**: When admin deletes in-progress save, include upload cleanup (extends existing admin service)

### 7. File validation

Server-side validation enforces:
- Max 3 files per upload
- Max 10MB per file
- JPEG/PNG content types only

Client-side validation mirrors these rules for immediate feedback (before form submission).

## Dependencies

No new Python packages. Uses only:
- `pathlib` (stdlib) — file operations
- `shutil` (stdlib) — directory cleanup
- `uuid` (stdlib) — already used for session IDs
- Existing `UploadFile` from FastAPI/Starlette — file upload handling
- Existing `python-multipart` — already installed for profile photo uploads
