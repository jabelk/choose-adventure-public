# Data Model: Character Visual Consistency

## Modified Entity: Story

**File**: `app/models.py`

### New Field

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `generated_reference_path` | `str` | `""` | Absolute file path of the most recently generated scene image, used as a rolling reference for subsequent image generations. Empty string means no generated reference yet. |

### Backward Compatibility

- Default `""` ensures existing sessions and saved stories load without error
- Empty string is falsy in Python, so `if story.generated_reference_path:` works naturally
- No migration needed — field is session-scoped, not persisted to disk

## Reference Assembly Logic

### Priority Order (max 3 total)

1. **Direct upload photos** (`story.reference_photo_paths`) — highest priority, override everything
2. **Roster character photos** — collected from `character_service.get_absolute_photo_paths(rc)` for each selected roster character
3. **Generated scene reference** (`story.generated_reference_path`) — rolling reference from last successful generation

### Cap Logic

```
if direct_uploads:
    refs = direct_uploads[:3]
else:
    refs = roster_photos[:2 if generated_ref else 3]
    if generated_ref and len(refs) < 3:
        refs.append(generated_ref)
```

## State Transitions

```
Story Start (Scene 1):
  generated_reference_path = ""
  → generate_image() with roster photos only
  → on success: generated_reference_path = "/path/to/static/images/{scene1_id}.png"

Scene 2+:
  generated_reference_path = "/path/to/scene_N-1.png"
  → generate_image() with roster photos + generated_reference_path
  → on success: generated_reference_path = "/path/to/static/images/{sceneN_id}.png"

Reset Appearance:
  generated_reference_path = "" (cleared)
  → next scene uses roster photos only (if any)
  → on success: generated_reference_path starts fresh

Image Generation Failure:
  generated_reference_path unchanged (keeps last successful reference)
```
