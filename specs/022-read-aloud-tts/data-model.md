# Data Model: Read Aloud / TTS Narration

**Feature**: 022-read-aloud-tts
**Date**: 2026-02-07

## Entities

### TTS Voice Configuration

No new persistent data model changes required. TTS is stateless — audio is generated on demand and not stored.

**Session-level state** (stored in existing tier session cookie):

| Field | Type | Description |
|-------|------|-------------|
| `tts_voice` | `str` | Selected voice identifier (e.g., "nova", "onyx"). Defaults per tier. |
| `tts_autoplay` | `bool` | Whether auto-play is enabled. Default: `True` for kids, `False` for NSFW. |

### TierConfig Extension

Add two fields to the existing `TierConfig` dataclass in `app/tiers.py`:

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `tts_default_voice` | `str` | `"nova"` | Default TTS voice for this tier |
| `tts_autoplay_default` | `bool` | `False` | Whether auto-play is on by default |
| `tts_voices` | `list[tuple[str, str]]` | `[]` | Available voices as `(id, display_name)` pairs |

**Kids tier**: `tts_default_voice="nova"`, `tts_autoplay_default=True`, voices: nova, shimmer, coral, fable
**NSFW tier**: `tts_default_voice="onyx"`, `tts_autoplay_default=False`, voices: onyx, ash, sage, alloy

### Scene Text Extraction

The scene's `content` field (existing `Scene.content: str`) is used directly as TTS input. No transformation needed — the content is already plain narrative text. Choice labels are separate (`Scene.choices`) and naturally excluded.

## Relationships

```
TierConfig --has--> tts_default_voice, tts_autoplay_default, tts_voices
Session Cookie --stores--> tts_voice, tts_autoplay (per-tier)
Scene.content --input-to--> OpenAI TTS API --returns--> MP3 audio bytes
```

## State Transitions

### Play Button States

```
idle --> loading --> playing --> idle
  ^                    |
  |                    v
  +--- (stop tap) ----+
  +--- (navigate) ----+
  +--- (error) -------+
```

- `idle`: Play button shown (speaker icon)
- `loading`: Fetching audio from server (spinner/pulse animation)
- `playing`: Audio playing (stop icon shown)
- Transitions back to `idle` on: stop tap, audio ends, navigation, error
