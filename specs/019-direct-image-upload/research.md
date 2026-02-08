# Research: Direct Image Upload

**Feature**: 019-direct-image-upload
**Date**: 2026-02-07

## Summary

No technical unknowns. This feature reuses existing patterns (file upload handling from profile photos, reference_images pipeline from image service). Research focused on confirming design choices.

## Decisions

### 1. Temporary file storage location

**Decision**: `data/uploads/{session_id}/` directory per story session.

**Rationale**: Using session_id as the directory name ties uploads directly to a story session. Cleanup is a simple `shutil.rmtree()`. The `data/` directory is already gitignored and used for other persistent/temporary data (stories, progress, profiles, photos).

**Alternatives considered**:
- System temp directory (`/tmp/`) — rejected because Docker containers may have limited `/tmp/` space, and files would be lost on container restart before cleanup runs.
- `data/photos/tmp/` alongside profile photos — rejected because it mixes temporary and permanent files.

### 2. Form encoding strategy

**Decision**: Always use `multipart/form-data` when the upload field is present in the form. Set via JavaScript: when files are selected, add `enctype="multipart/form-data"` to the form; when removed, reset to default.

**Rationale**: FastAPI's `Form()` parameters work transparently with both urlencoded and multipart requests. The dynamic switch satisfies FR-011 (no behavior change when no photos selected).

**Alternatives considered**:
- Always use multipart — rejected because spec requires preserving existing form behavior when no photos chosen.
- Separate upload endpoint — rejected as over-engineering for a simple file-with-form flow.

### 3. Client-side file handling

**Decision**: Use `FileReader.readAsDataURL()` for thumbnail previews, `DataTransfer` for managing the file list, and standard HTML5 drag-and-drop events.

**Rationale**: All target browsers (modern Chrome, Firefox, Safari) support these APIs. No external JS library needed. Consistent with project's "no unnecessary dependencies" approach.

**Alternatives considered**:
- Dropzone.js or FilePond library — rejected per Iterative Simplicity principle. The required functionality (preview + remove + drag-drop) is straightforward with vanilla JS.

### 4. Upload file parameter approach

**Decision**: Use `List[UploadFile]` parameter in FastAPI route handler with `File(default=[])`.

**Rationale**: FastAPI natively supports multiple file uploads via `List[UploadFile]`. The `File()` default allows the parameter to be optional (empty list when no files uploaded). This is the same pattern used by the existing character photo upload endpoint.

**Alternatives considered**:
- Processing files from `request.form()` manually — rejected because FastAPI's typed parameter extraction is cleaner and handles validation.

### 5. Photo path storage in session

**Decision**: Add `reference_photo_paths: list[str] = []` to the `Story` model. Populate at story start with absolute paths to saved temp files.

**Rationale**: The `make_choice` handler needs access to photo paths for every scene's image generation. Storing paths in the Story model (part of StorySession) means they persist through the session and are available in the progress save file.

**Alternatives considered**:
- Separate lookup from session_id to photo paths — rejected as unnecessary indirection. The Story model already carries per-story configuration.
