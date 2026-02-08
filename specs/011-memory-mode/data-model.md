# Data Model: Memory Mode

## Entities

### Profile

A named collection of preferences and characters belonging to a specific tier.

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| profile_id | string (UUID) | Yes | Auto-generated unique identifier |
| name | string | Yes | Display name (e.g., "Lily's Profile") |
| tier | string | Yes | Tier this profile belongs to ("kids" or "nsfw") |
| themes | list[string] | No | Preferred themes (e.g., ["dinosaurs", "space", "pirates"]) |
| art_style | string | No | Preferred image art style (e.g., "watercolor", "pixel art") |
| tone | string | No | Preferred story tone (e.g., "silly and lighthearted") |
| story_elements | list[string] | No | Favorite story elements (e.g., ["talking animals", "treasure hunts"]) |
| characters | list[Character] | No | Characters associated with this profile (max 10) |
| created_at | datetime | Yes | Auto-set on creation |
| updated_at | datetime | Yes | Auto-updated on modification |

**Validation rules**:
- `name` must be non-empty, max 100 characters
- `themes` max 20 items, each max 100 characters
- `story_elements` max 20 items, each max 200 characters
- `art_style` max 200 characters
- `tone` max 200 characters
- `characters` max 10 items

### Character

A named person or entity that can appear in stories. Always belongs to a Profile.

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| character_id | string (UUID) | Yes | Auto-generated unique identifier |
| name | string | Yes | Character's name (e.g., "Lily") |
| description | string | Yes | Character description (e.g., "5 years old, loves dinosaurs, has a pet cat named Whiskers") |
| linked_profile_id | string (UUID) | No | Optional reference to another profile in the same tier |

**Validation rules**:
- `name` must be non-empty, max 100 characters
- `description` must be non-empty, max 500 characters
- `linked_profile_id` must reference an existing profile in the same tier, or be null

## Relationships

```
Profile 1 ──── * Character
   │
   └── tier scoping ──── TierConfig (existing)

Character ── optional link ──> Profile (same tier only)

Story (existing) ── optional ──> Profile (via profile_id field)
```

### Cross-Profile References

- A Character may optionally link to another Profile via `linked_profile_id`
- Links are **same-tier only**: a kids Character MUST NOT link to an nsfw Profile
- Links are **one level deep**: when Profile A is active and its Character links to Profile B, Profile B's characters are included in the prompt context. Profile B's characters' links are NOT followed.
- When a linked Profile is deleted, the `linked_profile_id` on referencing Characters is set to null (graceful degradation)

### Story Model Extension

The existing `Story` model gains one optional field:

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| profile_id | string (UUID) | No | Profile used for this story session (null if memory mode off) |

This field is set at story start and persists for the session. It does NOT create a foreign key dependency — if the profile is later deleted, the field simply becomes a stale reference with no effect.

## Storage

Profiles are stored as JSON files on disk:

```
data/
└── profiles/
    ├── kids/
    │   ├── {profile_id_1}.json
    │   └── {profile_id_2}.json
    └── nsfw/
        └── {profile_id_3}.json
```

Each file contains the full Profile object serialized via Pydantic's `model_dump_json()`. This matches the existing pattern used by `data/stories/` and `data/progress/`.
