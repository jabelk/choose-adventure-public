# API Contract: TTS Narration

**Feature**: 022-read-aloud-tts
**Date**: 2026-02-07

## Endpoints

### GET `/{prefix}/story/tts/{scene_id}`

Generate and return TTS audio for a scene's narrative text.

**Path Parameters**:
- `scene_id` (str): The scene identifier

**Query Parameters**:
- `voice` (str, optional): Voice identifier. Defaults to session preference or tier default.

**Response** (success — 200):
- Content-Type: `audio/mpeg`
- Body: MP3 audio binary data

**Response** (no active story or scene not found — 404):
```json
{"detail": "Scene not found"}
```

**Response** (TTS service error — 502):
```json
{"detail": "TTS generation failed"}
```

**Behavior**:
1. Look up scene in current story session (or gallery if gallery context)
2. Extract `scene.content` as plain text
3. If text exceeds 4000 chars, split at sentence boundaries into chunks
4. Call OpenAI TTS API (`gpt-4o-mini-tts`, MP3 format) for each chunk
5. If multiple chunks, concatenate MP3 bytes
6. Return combined audio as `audio/mpeg` response
7. Update session cookie with voice preference if `voice` param provided

**Notes**:
- This endpoint is synchronous — the client waits for the response (typically 1-3 seconds)
- No caching or storage of generated audio
- Respects tier-scoped session cookies (cookie path = `/{prefix}/`)

---

### GET `/{prefix}/gallery/tts/{story_id}/{scene_id}`

Generate and return TTS audio for a gallery (saved) story scene.

**Path Parameters**:
- `story_id` (str): The saved story identifier
- `scene_id` (str): The scene identifier within that story

**Query Parameters**:
- `voice` (str, optional): Voice identifier. Defaults to session preference or tier default.

**Response**: Same as above (200 with MP3, 404, or 502).

**Behavior**:
1. Load saved story from gallery by `story_id`
2. Find scene by `scene_id` within the saved story
3. Same TTS generation as active story endpoint

---

### GET `/{prefix}/tts/voices`

Return available TTS voices for this tier.

**Response** (200):
```json
{
  "voices": [
    {"id": "nova", "name": "Nova (warm)"},
    {"id": "shimmer", "name": "Shimmer (gentle)"},
    {"id": "coral", "name": "Coral (friendly)"},
    {"id": "fable", "name": "Fable (storyteller)"}
  ],
  "current": "nova",
  "autoplay": true
}
```

**Notes**:
- `current` reflects the session's stored voice preference
- `autoplay` reflects the session's auto-play state
- Voice list is tier-specific (curated subset of OpenAI's 13 voices)

---

### POST `/{prefix}/tts/preferences`

Update TTS preferences (voice and auto-play toggle).

**Request Body** (JSON):
```json
{
  "voice": "shimmer",
  "autoplay": false
}
```

Both fields are optional — only provided fields are updated.

**Response** (200):
```json
{"status": "ok"}
```

**Behavior**:
1. Update session cookie with new voice and/or auto-play preference
2. Preference persists for the session duration (scoped to tier)

---

## OpenAI TTS API Call (Internal)

Not a public endpoint — this is the internal call made by `app/services/tts.py`.

```python
response = await client.audio.speech.create(
    model="gpt-4o-mini-tts",
    voice=voice,           # e.g., "nova", "onyx"
    input=text,            # Scene content (max ~4000 chars)
    response_format="mp3",
    instructions=instructions,  # e.g., "Speak warmly and cheerfully, like reading a bedtime story"
)
audio_bytes = response.content
```

**Voice Instructions** (per tier):
- Kids: `"Read this like a warm, friendly bedtime story. Use an engaging, gentle tone suitable for young children."`
- NSFW: `"Read this with a natural, expressive tone. Match the mood of the content."`
