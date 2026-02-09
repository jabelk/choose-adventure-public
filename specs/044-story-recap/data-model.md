# Data Model: Story Recap

## Model Extensions

### StorySession (existing model — extended)

**File**: `app/models.py`

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `recap_cache` | `dict[str, str]` | `{}` | Maps cache key (path hash) to generated recap text |

**Cache Key Format**: `"|".join(path_history[:scene_depth+1])` — the ordered scene IDs from root to current scene, joined by pipe. This ensures the cache automatically invalidates when the user navigates back and takes a different branch.

### No New Models Required

The recap is a simple string cached on the existing `StorySession`. No new Pydantic models, no new files, no new storage.

## State Transitions

```
Scene Load (depth >= 1)
    ├── Cache HIT (path key matches) → Return cached recap text instantly
    └── Cache MISS
        ├── Generate recap via AI → Store in recap_cache → Return text
        └── AI unavailable → Return empty/error state
```

## Data Flow

1. User navigates to scene (depth >= 1)
2. Client JS fetches `/story/recap/{scene_id}`
3. Server checks `story_session.recap_cache` for matching path key
4. If cached: return immediately
5. If not cached: call `story_service._call_provider()` with recap prompt + scene content
6. Cache result in `story_session.recap_cache[path_key]`
7. Return recap text to client
8. Client renders recap in the collapsible section
