# Data Model: Cover Art Generator

**Feature**: 045-cover-art-generator
**Date**: 2026-02-08

## Model Changes

### SavedStory (extended)

Two new fields added to the existing `SavedStory` model in `app/models.py`:

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `cover_art_url` | `Optional[str]` | `None` | URL path to the cover art image (e.g., `/static/images/{story_id}_cover.png`) |
| `cover_art_status` | `str` | `"none"` | Generation status: `"none"`, `"generating"`, `"complete"`, `"failed"` |

**Status transitions**:
```
none → generating → complete
none → generating → failed
complete → generating → complete  (regenerate)
complete → generating → failed    (regenerate fails)
failed → generating → complete    (regenerate succeeds)
```

**Backward compatibility**: Both fields have defaults (`None` and `"none"`), so existing gallery JSON files will load without error. Stories saved before this feature will have no cover art and display the first scene image as before.

## File Storage

### Cover Art Images

| Pattern | Location | Example |
|---------|----------|---------|
| `{story_id}_cover.png` | `static/images/` | `static/images/a1b2c3d4_cover.png` |

Cover images share the `static/images/` directory with scene images. The `_cover` suffix prevents collision with scene image files (which use `{scene_id}.png`).

## No New Models

No new Pydantic models are needed. The cover art is a simple extension of the existing `SavedStory` model with two additional fields.
