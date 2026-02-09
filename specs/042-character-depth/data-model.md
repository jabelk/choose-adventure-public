# Data Model: Enhanced Character Creation & Relationship Depth

**Feature**: 042-character-depth
**Date**: 2026-02-08

## Entity Changes

### RosterCharacter (MODIFIED)

Extends existing `app/models.py:RosterCharacter` with new optional fields.

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| character_id | str | uuid4() | Existing — unique identifier |
| name | str | required | Existing — max 100 chars |
| description | str | required | Existing — max 500 chars. Now also holds composed description from structured attributes. |
| tier | str | required | Existing — tier name |
| photo_paths | list[str] | [] | Existing — reference photo paths |
| outfits | list[CharacterOutfit] | [] | Existing — outfit configurations |
| created_at | datetime | now() | Existing |
| updated_at | datetime | now() | Existing |
| **attributes** | **dict[str, str]** | **{}** | **NEW** — Structured attribute selections, e.g. `{"hair_color": "Blonde", "body_type": "Athletic"}` |
| **relationship_stage** | **str** | **"strangers"** | **NEW** — Current relationship level (NSFW only) |
| **story_count** | **int** | **0** | **NEW** — Number of completed stories with this character |
| **last_story_date** | **Optional[str]** | **None** | **NEW** — ISO date string of last completed story |

**Backward compatibility**: All new fields have defaults. Existing character JSON files load without changes — Pydantic fills defaults for missing keys.

### CHARACTER_ATTRIBUTES (NEW — configuration, not persisted)

Defined in `app/story_options.py`. Not a Pydantic model — a plain dict used for form rendering and validation.

```python
{
    "category_key": {
        "label": str,           # Display name (e.g., "Hair Color")
        "options": list[str],   # Available choices (e.g., ["Blonde", "Brunette", ...])
        "tier_restrict": Optional[str],  # None = all tiers, "nsfw" = NSFW only
        "group": str,           # Grouping: "physical", "personality", "style"
    }
}
```

Categories by group:

**Physical** (group: "physical"):
- `hair_color`: Hair Color — 8 options — all tiers
- `hair_length`: Hair Length — 4 options — all tiers
- `eye_color`: Eye Color — 6 options — all tiers
- `skin_tone`: Skin Tone — 6 options — all tiers
- `body_type`: Body Type — 5 options — NSFW only
- `bust_size`: Bust Size — 5 options — NSFW only
- `height`: Height — 4 options — all tiers

**Personality** (group: "personality"):
- `temperament`: Temperament — 6 options — all tiers
- `energy`: Energy — 4 options — all tiers
- `archetype`: Archetype — 6 options — NSFW only

**Style** (group: "style"):
- `clothing_style`: Clothing Style — 6 options — all tiers
- `aesthetic_vibe`: Aesthetic Vibe — 4 options — all tiers

### RELATIONSHIP_STAGES (NEW — configuration, not persisted)

Ordered list of relationship progression levels:

```python
RELATIONSHIP_STAGES = [
    "strangers",
    "acquaintances",
    "flirting",
    "dating",
    "intimate",
    "committed",
]
```

Used for:
- Validation of `relationship_stage` field
- Auto-advancement logic (next stage = `STAGES[current_index + 1]`)
- Relationship context prompt generation

### RELATIONSHIP_PROMPTS (NEW — configuration, not persisted)

Maps relationship stage to AI prompt context:

```python
RELATIONSHIP_PROMPTS = {
    "strangers": "You and {name} are meeting for the first time. There's no history between you.",
    "acquaintances": "You and {name} have met before — you're familiar but not close.",
    "flirting": "You and {name} have been flirting — there's clear chemistry and playful tension.",
    "dating": "You and {name} have been dating — you're comfortable together with growing intimacy.",
    "intimate": "You and {name} are intimate partners — deep trust and physical familiarity.",
    "committed": "You and {name} are in a committed relationship — deep bond, shared history, complete trust.",
}
```

### KINK_TOGGLES (MODIFIED — 7 new entries)

Extends existing dict in `app/story_options.py`. Same tuple structure: `(display_name, story_prompt, image_prompt_addition)`.

New entries:
- `role_reversal`
- `power_dynamics`
- `clothing_destruction`
- `size_difference`
- `dominance_submission`
- `hypnosis`
- `bimboification`

## State Transitions

### Relationship Stage Progression

```
strangers → acquaintances → flirting → dating → intimate → committed
```

**Trigger**: Story completion (`gallery_service.save_story()` called with character in `roster_character_ids`).

**Rules**:
- Each completed story advances one stage (if not at max)
- `story_count` always increments regardless of stage
- `last_story_date` always updates to current date
- Manual override available via character detail page (can set any stage)
- Only applies to NSFW tier characters

## Storage

All data stored in existing character JSON files at `data/characters/{tier}/{character_id}.json`. No new files or directories.

Example character JSON after update:

```json
{
    "character_id": "abc-123",
    "name": "Margot Ellis",
    "description": "Blonde hair, hazel eyes, tall, athletic build. Playful and bubbly. Casual style with a natural vibe.",
    "tier": "nsfw",
    "photo_paths": [],
    "outfits": [],
    "attributes": {
        "hair_color": "Blonde",
        "eye_color": "Hazel",
        "height": "Tall",
        "body_type": "Athletic",
        "temperament": "Playful",
        "energy": "Bubbly",
        "clothing_style": "Casual",
        "aesthetic_vibe": "Natural"
    },
    "relationship_stage": "flirting",
    "story_count": 3,
    "last_story_date": "2026-02-08",
    "created_at": "2026-02-08T10:00:00",
    "updated_at": "2026-02-08T12:30:00"
}
```
