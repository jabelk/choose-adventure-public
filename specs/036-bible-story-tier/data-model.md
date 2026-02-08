# Data Model: Bible Story Tier

## Entity Changes

### StoryTemplate (extended)

Existing dataclass in `app/tiers.py`. Two new optional fields:

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| scripture_reference | str | "" | Bible passage reference, e.g., "Genesis 6-9", "1 Samuel 17" |
| section | str | "" | Grouping label for collapsible display, e.g., "Old Testament — Genesis" |

Both fields are optional with empty string defaults so existing kids and nsfw templates are unaffected.

### TierConfig (no schema changes)

A new `"bible"` entry in the `TIERS` dict uses all existing fields:

| Field | Value |
|-------|-------|
| name | "bible" |
| prefix | "bible" |
| display_name | "Bible Stories" |
| is_public | True |
| theme_class | "theme-bible" |
| content_guidelines | BIBLE_CONTENT_GUIDELINES (new constant) |
| image_style | "warm reverent children's Bible illustration..." |
| default_model | "claude" |
| default_image_model | "gpt-image-1" |
| templates | 75+ StoryTemplate entries with scripture_reference and section |
| tts_default_voice | "fable" |
| tts_autoplay_default | True |
| tts_voices | [("fable", "Fable (storyteller)"), ("nova", "Nova (warm)"), ("shimmer", "Shimmer (gentle)")] |
| tts_instructions | "Read this like a warm, reverent Bible story..." |

### OptionGroup (extended)

Add a `bible` field (list of OptionChoice) alongside existing `kids` and `nsfw` fields. Update `choices_for_tier()` to return `self.bible` when `tier == "bible"`.

Bible tier gets options for:
- **writing_style**: "Storyteller Narrator", "You Are The Hero", "Extra Simple Words"
- **num_characters**: reuse kids options
- **conflict_type**: not applicable (stories follow scripture)
- **protagonist_gender/age/character_type**: not applicable (characters are biblical)

### BibleService (new)

New service in `app/services/bible.py`:

| Method | Input | Output | Description |
|--------|-------|--------|-------------|
| fetch_verses | scripture_reference: str | str (verse text) | Calls YouVersion Platform API to get NIrV text for a passage |
| parse_reference | user_input: str | str (API-formatted ref) | Converts "Genesis 6:1-22" to YouVersion passage ID format |
| validate_reference | user_input: str | bool | Checks if input resembles a valid Bible book/passage |

Falls back gracefully if YouVersion API is unreachable — returns empty string and lets the AI use its training data. Service interface is API-agnostic so the backend can be swapped.

## No Database Changes

All data is hardcoded in Python (templates in `app/tiers.py`) or fetched at runtime from API.Bible. No new files on disk.
