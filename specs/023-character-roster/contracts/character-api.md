# API Contracts: Character Roster

**Feature**: 023-character-roster
**Date**: 2026-02-07

All endpoints are scoped under the NSFW tier prefix (`/nsfw/`).

---

## Character Management Page

### GET /nsfw/characters

**Purpose**: Display character management page with list of all saved characters.

**Response**: HTML page (`characters.html`) with template context:
- `characters`: List of all roster characters (sorted by name)
- `character_count`: Current count
- `max_characters`: 20
- `tier`: TierConfig
- `url_prefix`: "/nsfw"

**Empty State**: Shows "No characters saved yet" message with create form.

---

## Character CRUD

### POST /nsfw/characters/create

**Purpose**: Create a new roster character.

**Request**: `multipart/form-data`

| Field | Type | Required | Constraints |
|-------|------|----------|-------------|
| name | str | Yes | max 100 chars, unique per tier (case-insensitive) |
| description | str | Yes | max 500 chars |
| reference_photos | list[UploadFile] | No | max 3 files, JPEG/PNG, max 10 MB each |

**Success**: 303 redirect to `GET /nsfw/characters` with success flash.
**Errors**:
- Name empty → redirect with error flash
- Name already exists (case-insensitive) → redirect with error flash
- 20 character limit reached → redirect with error flash
- Photo validation failure → redirect with error flash

---

### POST /nsfw/characters/{character_id}/update

**Purpose**: Update an existing character's name, description, and photos.

**Request**: `multipart/form-data`

| Field | Type | Required | Constraints |
|-------|------|----------|-------------|
| name | str | Yes | max 100 chars, unique per tier (excluding self) |
| description | str | Yes | max 500 chars |
| reference_photos | list[UploadFile] | No | New photos to add (max 3 total) |
| remove_photos | list[str] | No | Photo filenames to remove |

**Success**: 303 redirect to `GET /nsfw/characters` with success flash.
**Errors**:
- Character not found → 404
- Name conflict → redirect with error flash

---

### POST /nsfw/characters/{character_id}/delete

**Purpose**: Delete a character and all its photos.

**Request**: No body required.

**Success**: 303 redirect to `GET /nsfw/characters` with success flash.
**Side Effects**:
- Removes character JSON file
- Removes character photos directory
- Profile references to this character become stale (silently ignored on next load)

**Errors**:
- Character not found → 404

---

## Character Photos

### GET /nsfw/characters/{character_id}/photo/{filename}

**Purpose**: Serve a character's reference photo.

**Response**: Image file with appropriate `Content-Type` (image/jpeg or image/png).

**Errors**:
- Character or photo not found → 404

---

## Character Picker API (for story start form)

### GET /nsfw/characters/api/list

**Purpose**: Return all characters as JSON for client-side picker population.

**Response**: `application/json`
```json
{
  "characters": [
    {
      "character_id": "uuid",
      "name": "Margot Ellis",
      "description": "Early 30s, honey-blonde hair...",
      "photo_urls": ["/nsfw/characters/uuid/photo/0_uuid.jpg"],
      "photo_count": 1
    }
  ],
  "count": 5,
  "max": 20
}
```

---

## Story Start Integration

### POST /nsfw/story/start (MODIFIED)

**New form fields** (additive to existing):

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| roster_character_ids | list[str] | No | Character IDs selected from picker (checkbox values) |

**Behavior changes**:
- If `roster_character_ids` provided: load each character, inject names/descriptions into content_guidelines, collect photo paths
- Roster characters are additive with manual `character_name`/`character_description`
- Photo priority: roster character photos + direct uploads, up to 3 total
- Store `roster_character_ids` on Story model for context rebuild on subsequent choices

---

## Profile Integration (MODIFIED)

### POST /nsfw/profiles/create (MODIFIED)

No changes needed — profiles don't reference characters at creation time.

### GET /nsfw/profiles/{profile_id} (MODIFIED)

**Additional template context**:
- `roster_characters`: List of all roster characters (for checkbox selection)
- `selected_character_ids`: Profile's current character_ids list

### POST /nsfw/profiles/{profile_id}/update (MODIFIED)

**New form field**:

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| character_ids | list[str] | No | Roster character IDs to associate with profile |

**Removed routes** (after migration):
- `POST /nsfw/profiles/{profile_id}/characters/add`
- `POST /nsfw/profiles/{profile_id}/characters/{character_id}/update`
- `POST /nsfw/profiles/{profile_id}/characters/{character_id}/delete`
- `POST /nsfw/profiles/{profile_id}/characters/{character_id}/photo`
- `POST /nsfw/profiles/{profile_id}/characters/{character_id}/photo/delete`
