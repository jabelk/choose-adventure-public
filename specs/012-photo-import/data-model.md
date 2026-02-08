# Data Model: Photo Import

**Feature**: 012-photo-import
**Date**: 2026-02-07

## Entity Changes

### Character (modified)

Existing entity from 011-memory-mode, extended with one new field.

| Field | Type | Constraints | Notes |
|-------|------|-------------|-------|
| character_id | str (UUID) | Required, auto-generated | Existing |
| name | str | Required, max 100 chars | Existing |
| description | str | Required, max 500 chars | Existing |
| linked_profile_id | str (optional) | Must be same-tier profile | Existing |
| **photo_path** | **str (optional)** | **Default None** | **NEW — relative path to photo file** |

**photo_path format**: `photos/{tier}/{profile_id}/{character_id}.{ext}` where ext is `jpg` or `png`.

When `photo_path` is None, the character has no reference photo (backward-compatible default).

### Photo File (new — filesystem entity, not a model)

Photos are stored as files on disk. No separate Pydantic model needed — the Character's `photo_path` field is the reference.

**Storage layout**:
```
data/
├── profiles/          # Existing profile JSON files
│   ├── kids/
│   └── nsfw/
└── photos/            # NEW — reference photos
    ├── kids/
    │   └── {profile_id}/
    │       └── {character_id}.jpg   # One photo per character
    └── nsfw/
        └── {profile_id}/
            └── {character_id}.png
```

**File constraints**:
- Formats: JPEG (.jpg) or PNG (.png)
- Max size: 5 MB
- No minimum resolution (warning shown for < 256x256)
- One photo per character (upload replaces existing)

## Relationships

```
Profile (1) ──has-many──> Character (0..10)
Character (1) ──has-one──> Photo file (0..1)  [via photo_path]
Character (0..1) ──links-to──> Profile (0..1)  [via linked_profile_id, same tier]
```

## Deletion Cascade

- **Delete character** → delete photo file at `data/{photo_path}` if exists
- **Delete profile** → delete all character photo files → delete `data/photos/{tier}/{profile_id}/` directory
- **Replace photo** → delete old file, write new file, update `photo_path`
- **Remove photo** → delete file, set `photo_path` to None

## Backward Compatibility

- Existing Character JSON files without `photo_path` field will deserialize with `photo_path=None` (Pydantic optional field default).
- No migration needed — existing profiles continue to work unchanged.
