# Data Model: Chapter Stories

## Modified Entities

### StoryLength (Enum Extension)

Add new value to existing enum in `app/models.py`:

| Value | target_depth | Description |
|-------|-------------|-------------|
| SHORT | 3 | Quick 5-minute story (~3 chapters) |
| MEDIUM | 5 | Standard 10-15 minute story (~5 chapters) |
| LONG | 7 | Extended 20+ minute story (~7 chapters) |
| **EPIC** | **25** | **Epic saga (~5 chapters, ~25 scenes)** |

### Scene (2 new optional fields)

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| chapter_number | Optional[int] | None | Chapter number (1-based). Set on the first scene of each chapter. None for non-epic stories. |
| chapter_title | Optional[str] | None | AI-generated chapter title. Set on the first scene of each chapter. None for non-epic stories. |

### SavedScene (2 new optional fields — mirrors Scene)

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| chapter_number | Optional[int] | None | Preserved from Scene on gallery save. |
| chapter_title | Optional[str] | None | Preserved from Scene on gallery save. |

## Unchanged Entities

- **Story**: No changes. `length` field already stores the StoryLength enum. `target_depth` already stored as int.
- **SavedStory**: No changes. `length` field stores string value. `target_depth` already stored as int.
- **StorySession**: No changes. Serializes all Scene data including new optional fields.
- **Choice / SavedChoice**: No changes.

## Chapter Boundary Logic (Derived, Not Stored)

```
SCENES_PER_CHAPTER = 5  # constant for epic stories

is_chapter_start = (depth % SCENES_PER_CHAPTER == 0) and story.length == "epic"
chapter_number = (depth // SCENES_PER_CHAPTER) + 1
total_chapters = target_depth // SCENES_PER_CHAPTER
```

## Progress Save Files

| File Pattern | Purpose |
|-------------|---------|
| `data/progress/{tier}.json` | Regular story progress (unchanged) |
| `data/progress/{tier}_chapter.json` | Epic/chapter story progress (new) |

## Backward Compatibility

- `chapter_number` and `chapter_title` default to `None` — existing scenes/stories load without changes
- New `EPIC` length only appears when selected — existing short/medium/long unchanged
- Progress files are separate — no migration needed
