# Research: Photo Import

**Feature**: 012-photo-import
**Date**: 2026-02-07

## Decision 1: How to Pass Reference Photos to Image Generation APIs

**Decision**: Use OpenAI `images.edit` endpoint (instead of `images.generate`) with `input_fidelity="high"` to preserve facial likeness. For Gemini, pass reference images as `inline_data` in the content array.

**Rationale**: OpenAI's `images.generate` endpoint does NOT accept reference images — it's text-only. The `images.edit` endpoint with `gpt-image-1` supports multiple input images and has an `input_fidelity` parameter specifically designed for preserving facial features. Gemini's `generate_content` endpoint natively supports image inputs alongside text.

**Alternatives considered**:
- Text-only descriptions of people ("a 5-year-old girl with brown hair"): Does not produce likeness, defeats the purpose of photo import.
- Fine-tuning a model on user photos: Massively overkill, expensive, slow, and requires ML infrastructure.
- Using a separate face-swap service: Adds external dependency, more complex pipeline, privacy concerns.

## Decision 2: Photo Storage Location

**Decision**: Store photos at `data/photos/{tier}/{profile_id}/{character_id}.{ext}` alongside existing profile data in `data/profiles/`.

**Rationale**: Follows the existing local-first file storage pattern (profiles in `data/profiles/`, stories in `data/stories/`, gallery in `data/progress/`). Directory structure mirrors profile hierarchy for natural cleanup when profiles/characters are deleted. Tier at the top level ensures physical isolation.

**Alternatives considered**:
- Store inside the profile JSON as base64: Bloats JSON files, makes profile loading slow, complicates serialization.
- Store in `static/images/` with generated images: Mixes user uploads with AI outputs, no tier isolation in static serving.
- Store in a database: Violates local-first/flat-file constitution principle, unnecessary complexity.

## Decision 3: Photo Serving Route Design

**Decision**: Serve photos via a tier-scoped route `GET /{tier}/photos/{profile_id}/{character_id}` that reads from disk and returns the image bytes with proper content type.

**Rationale**: Serving through application routes (not static file serving) enforces tier isolation — a request to `/kids/photos/...` can only access kids-tier photos. Direct filesystem serving would bypass tier checks. The route validates that the requested photo belongs to the correct tier before serving.

**Alternatives considered**:
- Static file serving with path-based access control: FastAPI's `StaticFiles` mount doesn't have per-request tier validation.
- Signed URLs: Overkill for a LAN-only personal app with no authentication.

## Decision 4: Character Model Extension for Photo Reference

**Decision**: Add an optional `photo_path` field (str, default None) to the existing Character model. This stores the relative path from the data root to the photo file (e.g., `photos/kids/abc123/def456.jpg`).

**Rationale**: Minimal model change — one optional field. The path is relative so it works across different deployment locations. Using a path reference (not embedding) keeps the JSON profile files small and fast to load. The `photo_path` being None means "no photo" which is the default and backward-compatible.

**Alternatives considered**:
- Separate PhotoMetadata model with its own JSON file: Over-engineered for one file per character.
- Store photo metadata (dimensions, size) in the model: Not needed — the image file on disk is the source of truth, and we only need the path to pass it to the API.

## Decision 5: Image Generation Pipeline Modification

**Decision**: Add an optional `reference_images` parameter (list of file paths) to `ImageService.generate_image()`. When present, DALL-E uses `images.edit` instead of `images.generate`, and Gemini includes the images in its content array. When absent (or empty), behavior is unchanged.

**Rationale**: Backward-compatible — existing calls without reference_images work exactly as before. The decision of which API endpoint to use is encapsulated in the image service. The route layer collects reference photo paths from the profile and passes them down.

**Alternatives considered**:
- Always use `images.edit` even without reference images: Unnecessary API change, potential behavior differences.
- Pass reference images as part of the prompt text: APIs don't work this way — images must be binary data, not text descriptions.

## Decision 6: Profile Context Builder Extension

**Decision**: Extend `build_profile_context()` to return a third value: a list of `(character_name, photo_path)` tuples for characters that have photos. This is used by routes to collect the actual photo file paths for image generation.

**Rationale**: The profile context builder already knows about all characters (including cross-profile linked ones). Adding photo path collection here keeps the logic centralized — routes don't need to re-traverse character lists. The photo paths are separate from the text context because they serve different purposes (text goes to story AI, photos go to image AI).

**Alternatives considered**:
- Have routes independently look up photo paths: Duplicates the character traversal logic (including cross-profile linking).
- Embed photo paths in the text prompt: Image APIs need actual binary data, not file paths in text.
