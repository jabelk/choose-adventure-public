# Data Model: Reusable Character Roster

**Feature**: 023-character-roster
**Date**: 2026-02-07

## Entities

### RosterCharacter (NEW)

Standalone character entity stored as individual JSON files.

| Field | Type | Required | Constraints | Notes |
|-------|------|----------|-------------|-------|
| character_id | str (UUID) | Yes | Auto-generated | Primary identifier |
| name | str | Yes | max 100 chars, unique per tier (case-insensitive) | Display name |
| description | str | Yes | max 500 chars | Physical appearance description |
| tier | str | Yes | Must match valid tier name | Scoping — "nsfw" only at launch |
| photo_paths | list[str] | No | max 3 entries | Relative paths: `characters/{tier}/{character_id}/photos/{filename}` |
| created_at | datetime | Yes | Auto-generated | Creation timestamp |
| updated_at | datetime | Yes | Auto-updated on save | Last modification timestamp |

**Storage**: `data/characters/{tier}/{character_id}.json`
**Photos**: `data/characters/{tier}/{character_id}/photos/{index}_{character_id[:8]}.{ext}`

**Validation Rules**:
- Name uniqueness: case-insensitive comparison within tier (`name.lower()`)
- Max 20 characters per tier
- Photo validation: JPEG/PNG only, max 10 MB per file, max 3 photos

### Profile (MODIFIED)

Remove inline `characters: list[Character]` field. Add `character_ids: list[str]` reference field.

| Field | Type | Change | Notes |
|-------|------|--------|-------|
| characters | list[Character] | REMOVE | No longer stored inline |
| character_ids | list[str] | ADD | List of RosterCharacter UUIDs referenced by this profile |

**Updated Profile fields** (after migration):

| Field | Type | Required | Constraints |
|-------|------|----------|-------------|
| profile_id | str (UUID) | Yes | Auto-generated |
| name | str | Yes | max 100 chars |
| tier | str | Yes | Valid tier name |
| themes | list[str] | No | User preferences |
| art_style | str | No | Image style preference |
| tone | str | No | Story tone preference |
| story_elements | list[str] | No | Narrative elements |
| character_ids | list[str] | No | References to RosterCharacter IDs |
| created_at | datetime | Yes | Auto-generated |
| updated_at | datetime | Yes | Auto-updated |

### StoryTemplate (MODIFIED)

Replace single character fields with list-based character references.

| Field | Type | Change | Notes |
|-------|------|--------|-------|
| character_name | str | REMOVE | Replaced by character_names list |
| character_description | str | REMOVE | Replaced by character_data list |
| character_names | list[str] | ADD | List of character names to match against roster |
| character_data | list[dict] | ADD | Inline fallback data per character: `[{"name": "...", "description": "..."}]` |

### Story (MODIFIED)

Update to support multiple characters.

| Field | Type | Change | Notes |
|-------|------|--------|-------|
| character_name | str | KEEP | For manual/ad-hoc character entry (backward compat) |
| character_description | str | KEEP | For manual/ad-hoc character entry |
| roster_character_ids | list[str] | ADD | IDs of roster characters used in this story |

## Relationships

```text
RosterCharacter (1) ←──referenced-by──→ (N) Profile.character_ids
RosterCharacter (1) ←──matched-by-name──→ (N) StoryTemplate.character_names
RosterCharacter (N) ←──used-in──→ (1) Story.roster_character_ids
```

## State Transitions

### Character Lifecycle

```text
[Created] → [Active] → [Edited] → [Active] → [Deleted]
                ↑                      |
                └──────────────────────┘
```

- **Created**: New character saved via management page. JSON file written.
- **Active**: Character available in picker, templates, profile references.
- **Edited**: Name, description, or photos updated. JSON file overwritten.
- **Deleted**: JSON file and photos directory removed. Profile references silently ignored. Template fallback to inline data.

## Directory Layout (Runtime)

```text
data/
├── characters/
│   └── nsfw/
│       ├── {uuid-1}.json
│       ├── {uuid-1}/
│       │   └── photos/
│       │       ├── 0_{uuid-1[:8]}.jpg
│       │       └── 1_{uuid-1[:8]}.png
│       ├── {uuid-2}.json
│       └── {uuid-2}/
│           └── photos/
└── profiles/
    └── nsfw/
        └── {profile-id}.json    # Now contains character_ids instead of characters
```
