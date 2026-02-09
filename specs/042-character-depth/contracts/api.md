# API Contracts: Enhanced Character Creation & Relationship Depth

**Feature**: 042-character-depth
**Date**: 2026-02-08

All routes are prefixed with `/{tier_prefix}` (e.g., `/nsfw/`, `/kids/`, `/bible/`).

## Modified Endpoints

### POST `/{tier}/characters/create`

**Changes**: Accepts optional structured attribute form fields in addition to existing `name` and `description`.

**Form Fields**:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| name | str | Yes | Character name (max 100 chars) |
| description | str | No | Free-text override (max 500 chars). If empty and attributes provided, auto-composed from attributes. |
| reference_photos | File[] | No | Existing — photo uploads |
| attr_hair_color | str | No | Attribute selection (e.g., "Blonde") |
| attr_hair_length | str | No | Attribute selection |
| attr_eye_color | str | No | Attribute selection |
| attr_skin_tone | str | No | Attribute selection |
| attr_body_type | str | No | Attribute selection (NSFW only, ignored on other tiers) |
| attr_bust_size | str | No | Attribute selection (NSFW only) |
| attr_height | str | No | Attribute selection |
| attr_temperament | str | No | Attribute selection |
| attr_energy | str | No | Attribute selection |
| attr_archetype | str | No | Attribute selection (NSFW only) |
| attr_clothing_style | str | No | Attribute selection |
| attr_aesthetic_vibe | str | No | Attribute selection |

**Behavior**:
1. Collect all `attr_*` fields into `attributes` dict (strip `attr_` prefix)
2. Validate that NSFW-only attributes are only present for NSFW tier
3. Compose description from attributes if `description` field is empty
4. If `description` is provided, append it after composed text
5. Save character with both `attributes` dict and composed `description`
6. Redirect to characters page (303)

### POST `/{tier}/characters/{character_id}/update`

**Changes**: Same attribute fields as create. Pre-populated from existing `attributes` dict.

**Additional behavior**: Re-compose description from updated attributes. If user modified the free-text override, append it.

### POST `/{tier}/characters/{character_id}/relationship`

**NEW endpoint** (NSFW only).

**Form Fields**:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| relationship_stage | str | Yes | One of: strangers, acquaintances, flirting, dating, intimate, committed |

**Response**: 303 redirect to character edit page.

**Behavior**: Validate stage value, update character's `relationship_stage` field.

### GET `/{tier}/characters/api/list`

**Changes**: Response includes new fields.

**Response** (existing + new fields):

```json
[
    {
        "character_id": "abc-123",
        "name": "Margot Ellis",
        "description": "Blonde hair, hazel eyes...",
        "photo_urls": ["/nsfw/characters/abc-123/photo/photo1.jpg"],
        "attributes": {"hair_color": "Blonde", "eye_color": "Hazel"},
        "relationship_stage": "flirting",
        "story_count": 3
    }
]
```

### POST `/{tier}/start` (story start)

**Changes**: Accepts inline attribute fields for one-off character definition.

**New Form Fields** (in addition to all existing fields):

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| inline_attr_hair_color | str | No | Inline character attribute |
| inline_attr_* | str | No | Same attribute categories as character create, prefixed with `inline_attr_` |

**Behavior**:
- If `roster_character_ids` is provided, inline attributes are ignored (roster character takes priority)
- If no roster character and inline attributes are present, compose description and inject into `content_guidelines`
- Inline characters are NOT saved to the roster (one-off use)

## Configuration Endpoint

### GET `/{tier}/characters/api/attributes`

**NEW endpoint**. Returns available attribute options for the current tier.

**Response**:

```json
{
    "physical": [
        {"key": "hair_color", "label": "Hair Color", "options": ["Blonde", "Brunette", ...]},
        {"key": "eye_color", "label": "Eye Color", "options": ["Brown", "Blue", ...]}
    ],
    "personality": [
        {"key": "temperament", "label": "Temperament", "options": ["Shy", "Bold", ...]}
    ],
    "style": [
        {"key": "clothing_style", "label": "Clothing Style", "options": ["Casual", "Sporty", ...]}
    ]
}
```

**Behavior**: Filters out NSFW-only categories for non-NSFW tiers.
