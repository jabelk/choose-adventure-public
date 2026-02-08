# Research: Read Aloud / TTS Narration

**Feature**: 022-read-aloud-tts
**Date**: 2026-02-07

## R1: TTS API Choice

**Decision**: Use OpenAI TTS API (`gpt-4o-mini-tts` model)

**Rationale**:
- OpenAI API key already configured in the project for images and Whisper
- `gpt-4o-mini-tts` is the latest model (March 2025), cheaper than `tts-1` at ~$0.015/min
- Supports voice instructions for steerability (can set tone: "warm and friendly" for kids, "dramatic" for adults)
- 13 built-in voices available (exceeds FR-008's requirement of 4+)
- Streaming support via chunk transfer encoding for low-latency playback

**Alternatives considered**:
- `tts-1` / `tts-1-hd`: Older models, character-based pricing ($15-30/1M chars), no instruction support
- Browser Web Speech API: Free, offline-capable, but voice quality is poor and inconsistent across devices
- Google Cloud TTS: Would require a new API key and dependency

## R2: Audio Format

**Decision**: Use MP3 response format

**Rationale**:
- Universal browser support (Chrome, Safari, Firefox, Edge)
- Good compression for LAN delivery (~1MB per minute)
- Default format for OpenAI TTS API
- `<audio>` element plays MP3 natively on all target devices (iPad, phone, laptop)

**Alternatives considered**:
- Opus: Better compression but Safari support requires container (WebM)
- WAV: Larger files, no benefit for this use case
- AAC: Good but MP3 is simpler and equally supported

## R3: Audio Delivery Pattern

**Decision**: Server generates audio on demand, returns MP3 binary directly (no polling)

**Rationale**:
- OpenAI TTS is fast (~1-3 seconds for typical scenes under 500 words)
- Simpler than the image polling pattern — no background tasks needed
- Client fetches `GET /{prefix}/story/tts/{scene_id}?voice=alloy`, server calls OpenAI, returns MP3
- Browser `<audio>` element handles playback natively
- No permanent storage needed (matches spec assumption)

**Alternatives considered**:
- Background task + polling (like images): Over-engineered for a 1-3 second operation
- Streaming chunks to client: More complex, marginal benefit for short scenes
- WebSocket: Unnecessary complexity
- Pre-generate on scene load: Wastes API calls if user doesn't want audio

## R4: Text Chunking for Long Scenes

**Decision**: Split at sentence boundaries, 4000 character chunks (under `gpt-4o-mini-tts` 2000 token limit)

**Rationale**:
- `gpt-4o-mini-tts` has a 2000 token limit (~4000 chars for English text)
- Split at sentence boundaries (`.` `!` `?`) to avoid mid-word cuts
- Generate multiple audio segments server-side, concatenate, return single MP3
- Most scenes are 100-400 words (~500-2000 chars), well under the limit
- Only very long scenes (epic-length stories) will need splitting

**Alternatives considered**:
- Paragraph-level splitting: Less granular, may still exceed limit
- Client-side sequential playback: More complex, audible gaps between segments

## R5: Voice Selection

**Decision**: Offer 6 voices curated per tier, stored in session cookie

**Rationale**:
- OpenAI has 13 voices, but showing all would overwhelm the UI
- Kids tier defaults: 4 warm/friendly voices (nova, shimmer, coral, fable)
- NSFW tier defaults: 4 varied/dramatic voices (onyx, ash, sage, alloy)
- Voice preference stored in the tier session cookie (same mechanism as other preferences)
- Default voice: `nova` for kids (warm, friendly), `onyx` for NSFW (deep, dramatic)

**Alternatives considered**:
- Show all 13 voices: Too many options, especially for the kids tier
- Browser localStorage: Would work but session cookie keeps it server-aware

## R6: Auto-Play Implementation

**Decision**: JavaScript-driven auto-play triggered on page load, controlled by session preference

**Rationale**:
- Template renders a `data-tts-autoplay="true"` attribute on kids tier scenes
- JavaScript checks this attribute on DOMContentLoaded and triggers playback
- User can toggle auto-play via a small toggle button near the play button
- Toggle state stored in session cookie alongside voice preference
- Auto-play only fires on scene pages (not home, gallery list, etc.)

**Alternatives considered**:
- Server-side auto-play via `<audio autoplay>`: Blocked by most browsers without user interaction
- Always auto-play then let user disable: Bad UX for NSFW tier

## R7: Word/Sentence Highlighting (Stretch Goal - P4)

**Decision**: Sentence-level highlighting using estimated reading speed (no word-level timing)

**Rationale**:
- OpenAI TTS API does NOT provide word-level timing data
- Estimate ~150 words per minute at default speed
- Split scene text into sentences, calculate estimated duration per sentence
- Highlight current sentence by wrapping in `<span class="tts-highlight">` and advancing on timer
- Good enough for the 5-year-old's reading-along use case
- Can be refined later if OpenAI adds timing data

**Alternatives considered**:
- Word-level timing via audio analysis library: Heavy dependency, complex, overkill
- Skip highlighting entirely: Loses educational value for the older child
- Use a different TTS provider with timing: Adds complexity and another API key

## R8: API Key Availability Check

**Decision**: Check `settings.openai_api_key` at template render time, conditionally show TTS controls

**Rationale**:
- FR-011 requires silently hiding the feature when no API key is configured
- Pass `tts_available: bool` to template context
- Template conditionally renders the play button and voice selector
- Same pattern used for voice input (checks API key before showing mic button)

**Alternatives considered**:
- Client-side check via API call: Extra round-trip, flashing UI
- Always show, fail gracefully: Violates FR-011
