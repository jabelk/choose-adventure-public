# API Contracts: Photo Import

**Feature**: 012-photo-import
**Date**: 2026-02-07

## New Routes

All routes are scoped within `create_tier_router()` and prefixed with `/{tier}`.

### POST /{tier}/profiles/{profile_id}/characters/{character_id}/photo

Upload or replace a reference photo for a character.

**Request**: `multipart/form-data`
- `photo`: File upload (JPEG or PNG, max 5 MB)

**Response**: `303 See Other` → redirect to `/{tier}/profiles/{profile_id}` (profile edit page)

**Error cases**:
- Invalid file type (not JPEG/PNG): redirect with `error` query param
- File too large (> 5 MB): redirect with `error` query param
- Character not found: 404
- Profile not found: 404

**Side effects**:
- Saves photo to `data/photos/{tier}/{profile_id}/{character_id}.{ext}`
- Deletes previous photo file if one exists (replacement)
- Updates character's `photo_path` field in profile JSON
- Shows warning flash if image < 256x256 pixels

---

### POST /{tier}/profiles/{profile_id}/characters/{character_id}/photo/delete

Remove a character's reference photo.

**Request**: Empty POST (form submit)

**Response**: `303 See Other` → redirect to `/{tier}/profiles/{profile_id}` (profile edit page)

**Side effects**:
- Deletes photo file from `data/photos/{tier}/{profile_id}/{character_id}.{ext}`
- Sets character's `photo_path` to None in profile JSON

---

### GET /{tier}/photos/{profile_id}/{character_id}

Serve a character's reference photo (tier-scoped for isolation).

**Response**: Image bytes with appropriate `Content-Type` header (`image/jpeg` or `image/png`)

**Error cases**:
- Photo not found: 404
- Profile not in this tier: 404

**Notes**: This route enforces tier isolation — requesting `/kids/photos/...` only accesses kids-tier photos.

---

## Modified Routes

### POST /{tier}/profiles/{profile_id}/characters/add (existing)

No change to the route itself, but the character add form now optionally includes a photo upload field.

### POST /{tier}/profiles/{profile_id}/characters/{character_id}/update (existing)

No change to the route itself, but the character edit form now optionally includes a photo upload field. Photo upload is handled by the separate `/photo` route.

### Image Generation Pipeline (internal)

`ImageService.generate_image()` gains an optional `reference_images: list[str]` parameter.

When `reference_images` is non-empty:
- **DALL-E**: Uses `images.edit` endpoint instead of `images.generate`, passes photo files as input images with `input_fidelity="high"`
- **Gemini**: Includes reference images as `inline_data` parts in the content array alongside the text prompt

When `reference_images` is empty or None: behavior unchanged (backward-compatible).

### start_story route (existing, modified)

When memory mode is on and a profile with photo-linked characters is selected:
1. Calls `build_profile_context()` which now also returns photo paths
2. Passes photo paths to `generate_image()` as `reference_images`

### make_choice route (existing, modified)

Same as start_story — re-applies profile context including photo paths for subsequent scene generation.

## Route Summary

| Method | Path | Purpose | New? |
|--------|------|---------|------|
| POST | `/{tier}/profiles/{pid}/characters/{cid}/photo` | Upload/replace photo | NEW |
| POST | `/{tier}/profiles/{pid}/characters/{cid}/photo/delete` | Remove photo | NEW |
| GET | `/{tier}/photos/{pid}/{cid}` | Serve photo (tier-isolated) | NEW |
